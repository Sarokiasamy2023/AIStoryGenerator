"""Hybrid DOCX Analyzer - Combines Pattern Parsing + OCR

This analyzer uses:
1. DOCX text structure (STEP/Description/Action) as the skeleton
2. OCR on screenshots to extract concrete field names and values
3. Smart matching to generate accurate test steps

Expected output:
- Type "sarokiasamy2@dmigs.com.dcp.dcpuat" into "Username"
- Type "Grantee@123" into "Password"
- Click "Log in"
- Type "3" into "Number of Counties Served"
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import re

try:
    from docx_step_pattern_parser import DocxStepPatternParser
except ImportError:
    DocxStepPatternParser = None  # type: ignore

try:
    from docx_screenshot_ocr import DocxScreenshotOCRAnalyzer
except ImportError:
    DocxScreenshotOCRAnalyzer = None  # type: ignore


@dataclass
class HybridStep:
    """A concrete test step with context."""
    step_number: int
    step_title: str
    action: str  # e.g., "Type \"3\" into \"Number of Counties Served\""
    source: str  # "pattern", "ocr", or "hybrid"
    confidence: float  # 0.0 to 1.0


class DocxHybridAnalyzer:
    """Combines DOCX pattern parsing with OCR for accurate step generation."""

    def __init__(self):
        self.pattern_parser = DocxStepPatternParser() if DocxStepPatternParser else None
        self.ocr_analyzer = DocxScreenshotOCRAnalyzer() if DocxScreenshotOCRAnalyzer else None

    def analyze(self, docx_path: str) -> Dict[str, Any]:
        """Generate hybrid test steps from DOCX."""
        if not self.pattern_parser or not self.ocr_analyzer:
            raise RuntimeError(
                "DocxStepPatternParser and DocxScreenshotOCRAnalyzer are required. "
                "Ensure both modules are available."
            )

        # Step 1: Parse DOCX structure (STEP titles, descriptions, actions)
        pattern_steps = self.pattern_parser.parse_docx(docx_path)

        # Step 2: Run OCR to extract field names and values
        ocr_steps = self.ocr_analyzer.extract_concrete_steps(docx_path)

        # Step 3: Combine them intelligently
        hybrid_steps = self._combine_steps(pattern_steps, ocr_steps)

        return {
            "total_steps": len(hybrid_steps),
            "steps": [self._format_step(s) for s in hybrid_steps],
            "pattern_count": len(pattern_steps),
            "ocr_count": len(ocr_steps),
            "hybrid_count": len(hybrid_steps),
        }

    def _combine_steps(
        self, pattern_steps: List[Dict[str, Any]], ocr_steps: List[str]
    ) -> List[HybridStep]:
        """Intelligently combine pattern-based and OCR-based steps."""
        hybrid_steps: List[HybridStep] = []

        # Build a pool of OCR-extracted field names and values
        ocr_fields = self._extract_ocr_fields(ocr_steps)
        
        # Track which OCR steps have been used to avoid duplicates
        used_ocr_indices = set()

        for step_data in pattern_steps:
            step_num = step_data.get("step_number", 0)
            step_title = step_data.get("title", "")
            description = step_data.get("description", "")
            actions = step_data.get("actions", [])
            
            # Create context for this step (title + description)
            step_context = f"{step_title} {description}".lower()

            # For each action bullet, try to generate concrete steps
            for action_text in actions:
                concrete_steps, used_indices = self._generate_concrete_from_action(
                    action_text, ocr_fields, step_num, step_title, step_context, used_ocr_indices
                )
                hybrid_steps.extend(concrete_steps)
                used_ocr_indices.update(used_indices)

        # Don't add leftover OCR steps - they're likely noise or already matched

        # Sort by step number
        hybrid_steps.sort(key=lambda s: s.step_number)

        return hybrid_steps

    def _extract_ocr_fields(self, ocr_steps: List[str]) -> Dict[str, List[str]]:
        """Extract field names and values from OCR steps."""
        fields = {
            "type_fields": [],  # [(value, field_name), ...]
            "click_buttons": [],  # [button_name, ...]
            "verify_text": [],  # [text, ...]
        }

        for step in ocr_steps:
            # Parse "Type \"value\" into \"field\""
            type_match = re.match(r'Type "([^"]+)" into "([^"]+)"', step)
            if type_match:
                value, field = type_match.groups()
                fields["type_fields"].append((value, field))
                continue

            # Parse "Click \"button\""
            click_match = re.match(r'Click "([^"]+)"', step)
            if click_match:
                button = click_match.group(1)
                fields["click_buttons"].append(button)
                continue

            # Parse "Verify \"text\""
            verify_match = re.match(r'Verify "([^"]+)"', step)
            if verify_match:
                text = verify_match.group(1)
                fields["verify_text"].append(text)

        return fields

    def _generate_concrete_from_action(
        self,
        action_text: str,
        ocr_fields: Dict[str, List[str]],
        step_num: int,
        step_title: str,
        step_context: str,
        used_indices: set,
    ) -> tuple[List[HybridStep], set]:
        """Generate concrete steps from an action bullet using OCR context.
        
        Returns: (steps, set of OCR indices used)
        """
        steps: List[HybridStep] = []
        new_used_indices = set()
        action_lower = action_text.lower()

        # Check if this is a generic "fill all fields" action
        is_generic_fill = any(phrase in action_lower for phrase in [
            "fill all fields",
            "enter all",
            "using the values detected",
            "with values from screenshot",
            "values from the screenshot",
            "using values from",
        ])

        # Pattern 1: "Enter/Type/Input X into Y"
        if any(kw in action_lower for kw in ["enter", "type", "input", "fill"]):
            if is_generic_fill:
                # For generic "fill all fields", use ALL unused OCR fields that are contextually relevant
                for idx, (value, field) in enumerate(ocr_fields["type_fields"]):
                    if idx in used_indices:
                        continue
                    
                    # Only use fields that are contextually relevant to this step
                    if self._is_field_relevant_to_context(field, step_context):
                        steps.append(
                            HybridStep(
                                step_number=step_num,
                                step_title=step_title,
                                action=f'Type "{value}" into "{field}"',
                                source="hybrid",
                                confidence=0.85,
                            )
                        )
                        new_used_indices.add(idx)
            else:
                # For specific actions, find best match only
                best_match = None
                best_score = 0
                best_idx = -1
                
                for idx, (value, field) in enumerate(ocr_fields["type_fields"]):
                    if idx in used_indices:
                        continue
                        
                    # Score the match quality
                    score = self._score_field_match(action_lower, field.lower())
                    if score > best_score:
                        best_score = score
                        best_match = (value, field)
                        best_idx = idx
                
                if best_match and best_score > 0:
                    value, field = best_match
                    steps.append(
                        HybridStep(
                            step_number=step_num,
                            step_title=step_title,
                            action=f'Type "{value}" into "{field}"',
                            source="hybrid",
                            confidence=min(0.95, 0.7 + best_score * 0.1),
                        )
                    )
                    new_used_indices.add(best_idx)

        # Check for generic click actions
        is_generic_click = any(phrase in action_lower for phrase in [
            "shown in screenshot",
            "shown in the screenshot",
            "as shown",
            "check boxes",
            "select options",
        ])

        # Pattern 2: "Click/Select/Press X"
        if any(kw in action_lower for kw in ["click", "select", "press", "choose", "open", "check"]):
            if is_generic_click:
                # For generic actions, use multiple unused buttons that are contextually relevant
                count = 0
                for idx, button in enumerate(ocr_fields["click_buttons"]):
                    key = f"click_{idx}"
                    if key in used_indices:
                        continue
                    
                    # Only use buttons that are contextually relevant
                    if self._is_button_relevant_to_context(button, step_context):
                        # Add up to 5 buttons for generic actions
                        if count < 5:
                            steps.append(
                                HybridStep(
                                    step_number=step_num,
                                    step_title=step_title,
                                    action=f'Click "{button}"',
                                    source="hybrid",
                                    confidence=0.75,
                                )
                            )
                            new_used_indices.add(key)
                            count += 1
            else:
                # For specific actions, find best match only
                best_match = None
                best_score = 0
                best_idx = -1
                
                for idx, button in enumerate(ocr_fields["click_buttons"]):
                    key = f"click_{idx}"
                    if key in used_indices:
                        continue
                        
                    score = self._score_button_match(action_lower, button.lower())
                    if score > best_score:
                        best_score = score
                        best_match = button
                        best_idx = idx
                
                if best_match and best_score > 0:
                    steps.append(
                        HybridStep(
                            step_number=step_num,
                            step_title=step_title,
                            action=f'Click "{best_match}"',
                            source="hybrid",
                            confidence=min(0.95, 0.7 + best_score * 0.1),
                        )
                    )
                    new_used_indices.add(f"click_{best_idx}")

        # Pattern 3: "Verify/Check X"
        if any(kw in action_lower for kw in ["verify", "check", "confirm", "ensure"]):
            for idx, text in enumerate(ocr_fields["verify_text"]):
                key = f"verify_{idx}"
                if key in used_indices:
                    continue
                    
                if text.lower() in action_lower:
                    steps.append(
                        HybridStep(
                            step_number=step_num,
                            step_title=step_title,
                            action=f'Verify "{text}"',
                            source="hybrid",
                            confidence=0.85,
                        )
                    )
                    new_used_indices.add(key)
                    break

        # If no OCR match, create a generic step from the action text
        if not steps:
            generic_action = self._create_generic_action(action_text)
            if generic_action:
                steps.append(
                    HybridStep(
                        step_number=step_num,
                        step_title=step_title,
                        action=generic_action,
                        source="pattern",
                        confidence=0.5,
                    )
                )

        return steps, new_used_indices
    
    def _score_field_match(self, action_lower: str, field_lower: str) -> int:
        """Score how well a field matches an action (0-5)."""
        score = 0
        field_words = field_lower.split()
        
        # +3 if field name is explicitly in action
        if field_lower in action_lower:
            score += 3
        
        # +1 for each significant word match
        significant_words = [w for w in field_words if len(w) > 3]
        for word in significant_words[:3]:  # Max 3 words
            if word in action_lower:
                score += 1
        
        return score
    
    def _score_button_match(self, action_lower: str, button_lower: str) -> int:
        """Score how well a button matches an action (0-5)."""
        score = 0
        
        # +4 if button name is explicitly in action
        if button_lower in action_lower:
            score += 4
        
        # +2 for each word match
        button_words = button_lower.split()
        for word in button_words:
            if len(word) > 2 and word in action_lower:
                score += 2
        
        return min(score, 5)
    
    def _is_field_relevant_to_context(self, field: str, context: str) -> bool:
        """Check if a field is relevant to the current step context."""
        field_lower = field.lower()
        
        # Filter out instructional/metadata text
        noise_patterns = [
            "statement",
            "back to main",
            "sponsor",
            "person is not required",
            "government performance",
            "burden for this collection",
            "access to care",
        ]
        
        if any(noise in field_lower for noise in noise_patterns):
            return False
        
        # Field should have reasonable keywords
        field_keywords = [
            "number", "name", "total", "count", "value", "amount",
            "counties", "population", "patient", "served", "panel",
            "ratio", "funding", "fees", "grants", "services",
            "member", "organization", "consortium", "network",
            "disease", "diabetes", "screening", "pressure", "tobacco",
            "measures", "numerator", "denominator", "percentage",
            "miles", "encounters", "sites", "providers", "capacity",
            "username", "password", "email",
        ]
        
        return any(kw in field_lower for kw in field_keywords)
    
    def _is_button_relevant_to_context(self, button: str, context: str) -> bool:
        """Check if a button is relevant to the current step context."""
        button_lower = button.lower()
        
        # Common navigation buttons are always relevant
        nav_buttons = ["next", "finish", "done", "submit", "ok", "log in", "login"]
        if button_lower in nav_buttons:
            return True
        
        # Filter out noise
        noise_patterns = ["statement", "back to main", "sponsor"]
        if any(noise in button_lower for noise in noise_patterns):
            return False
        
        # Button should be reasonably short (not a sentence)
        if len(button) > 50:
            return False
        
        return True

    def _create_generic_action(self, action_text: str) -> Optional[str]:
        """Create a generic action from action text if no OCR match."""
        action_lower = action_text.lower()

        # Common patterns
        if "click" in action_lower or "select" in action_lower:
            # Extract quoted text or capitalized words
            quoted = re.findall(r'"([^"]+)"', action_text)
            if quoted:
                return f'Click "{quoted[0]}"'

        if "type" in action_lower or "enter" in action_lower:
            # Try to extract field name
            quoted = re.findall(r'"([^"]+)"', action_text)
            if len(quoted) >= 2:
                return f'Type "{quoted[0]}" into "{quoted[1]}"'

        # Fallback: return the action text as a comment
        return f"# {action_text}"

    def _is_high_confidence_ocr(self, ocr_step: str) -> bool:
        """Check if an OCR step is high confidence (good field/button name)."""
        # High confidence if it's a Click or Verify step
        if ocr_step.startswith("Click") or ocr_step.startswith("Verify"):
            return True

        # High confidence if Type step has a good field name
        if ocr_step.startswith("Type"):
            match = re.match(r'Type "([^"]+)" into "([^"]+)"', ocr_step)
            if match:
                _, field = match.groups()
                # Good field names are longer and have keywords
                field_keywords = [
                    "number", "name", "username", "password", "email",
                    "counties", "population", "patient", "served",
                    "total", "ratio", "funding", "miles", "encounters"
                ]
                if len(field) > 15 and any(kw in field.lower() for kw in field_keywords):
                    return True

        return False

    def _format_step(self, step: HybridStep) -> Dict[str, Any]:
        """Format a HybridStep for JSON output."""
        return {
            "step_number": step.step_number,
            "step_title": step.step_title,
            "action": step.action,
            "source": step.source,
            "confidence": step.confidence,
        }
