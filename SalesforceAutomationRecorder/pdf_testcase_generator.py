"""PDF Test Case Generator

Takes the structured analysis from PdfDocumentAnalyzer and produces
high-level POSITIVE / NEGATIVE / EDGE test case scenarios.

This is heuristic-based and deliberately generic:
- No field names or values are hardcoded.
- Scenarios are grouped by functional categories (Navigation, Submission, etc.).
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Dict, Any


@dataclass
class PdfTestCaseScenario:
    name: str
    category: str
    scenario_type: str  # POSITIVE, NEGATIVE, EDGE
    steps: List[str]
    expected: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PdfTestCaseGenerator:
    """Generate generic POS/NEG/EDGE test cases from PDF analysis output."""

    def generate_from_analysis(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        categorized = analysis.get("categorized_sections", {}) or {}
        validation_rules = analysis.get("validation_rules", []) or []
        user_actions = analysis.get("user_actions", []) or []
        expected_results = analysis.get("expected_results", []) or []

        scenarios: List[PdfTestCaseScenario] = []

        for category, lines in categorized.items():
            if not lines:
                continue

            # Build a short description from first 1-2 lines of this category.
            description_parts = lines[:2]
            description = " ".join(description_parts)

            # Try to find concrete actions and outcomes that belong to this bucket by
            # intersecting categorized lines with the global user_actions / expected_results.
            category_actions: List[str] = []
            category_expected: List[str] = []

            for line in lines:
                if line in user_actions and line not in category_actions:
                    category_actions.append(line)
                if line in expected_results and line not in category_expected:
                    category_expected.append(line)

            base_name = f"{category} Behavior"

            # Choose a rule message, if any, to anchor NEGATIVE / EDGE behavior.
            rule_message = validation_rules[0] if validation_rules else "rule described in the user guide"

            # ----------------------------
            # POSITIVE scenario
            # ----------------------------
            pos_steps: List[str] = []

            if category_actions:
                # Use up to two concrete actions from the guide.
                primary_actions = category_actions[:2]
                for act in primary_actions:
                    pos_steps.append(act)
            else:
                pos_steps.append(
                    f"Follow the documented {category.lower()} steps as described in the user guide."
                )

            if description:
                pos_steps.append(f"Reference: {description}")

            if category_expected:
                # Use the first detected expected behavior for POSITIVE.
                pos_expected = [category_expected[0]]
            else:
                pos_expected = [
                    "System accepts the action and records the data / navigation successfully.",
                ]

            scenarios.append(
                PdfTestCaseScenario(
                    name=base_name,
                    category=category,
                    scenario_type="POSITIVE",
                    steps=pos_steps,
                    expected=pos_expected,
                )
            )

            # ----------------------------
            # NEGATIVE scenario
            # ----------------------------
            neg_steps: List[str] = []

            if category_actions:
                neg_steps.append(
                    f"Attempt the same {category.lower()} action with missing or invalid information." 
                )
                if description:
                    neg_steps.append(f"Based on: {description}")
            else:
                neg_steps.append(
                    f"Input violates at least one documented {category.lower()} rule (e.g., required data is omitted or incorrect)."
                )
                if description:
                    neg_steps.append(f"Reference: {description}")

            # Prefer an expected result mentioning errors from this category, otherwise fall back
            # to a generic rule-based error message.
            neg_expected: List[str] = []
            error_like = [e for e in category_expected if "error" in e.lower() or "cannot" in e.lower()]
            if error_like:
                neg_expected.append(error_like[0])
            else:
                neg_expected.append(f"System enforces the rule and shows a validation message related to: {rule_message}.")

            scenarios.append(
                PdfTestCaseScenario(
                    name=base_name,
                    category=category,
                    scenario_type="NEGATIVE",
                    steps=neg_steps,
                    expected=neg_expected,
                )
            )

            # ----------------------------
            # EDGE scenario
            # ----------------------------
            edge_steps: List[str] = []

            edge_steps.append(
                f"Perform the {category.lower()} action using boundary conditions around the documented rules (for example, limits implied by: {rule_message})."
            )
            if description:
                edge_steps.append(f"Reference: {description}")

            # For EDGE, prefer a non-error expected result if available, otherwise a generic one.
            edge_expected: List[str] = []
            non_error_like = [e for e in category_expected if "error" not in e.lower()]
            if non_error_like:
                edge_expected.append(non_error_like[0])
            else:
                edge_expected.append("System accepts the boundary input and behaves as documented without unexpected errors.")

            scenarios.append(
                PdfTestCaseScenario(
                    name=base_name,
                    category=category,
                    scenario_type="EDGE",
                    steps=edge_steps,
                    expected=edge_expected,
                )
            )

        return [s.to_dict() for s in scenarios]
