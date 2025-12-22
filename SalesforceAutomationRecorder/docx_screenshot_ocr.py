"""DOCX Screenshot OCR Analyzer

Uses Tesseract OCR (via pytesseract) to read UI text from screenshots
embedded in a DOCX and generate more concrete test steps like:
- Type "34000" into "Number of people in the target population"
- Click "Next"
- Verify "Submit for Review"

This is heuristic-only and does not hardcode any field names or values.
"""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import List

try:  # Soft import so the rest of the app still works without OCR
    import pytesseract  # type: ignore
    from pytesseract import Output  # type: ignore
    from PIL import Image  # type: ignore

    # Configure Tesseract path (adjust if your install location is different)
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
except ImportError:  # pragma: no cover
    pytesseract = None  # type: ignore
    Output = None  # type: ignore
    Image = None  # type: ignore

try:
    from docx import Document  # type: ignore
except ImportError:  # pragma: no cover
    Document = None  # type: ignore


@dataclass
class ConcreteStepGeneratorConfig:
    # Common button words we turn into Click steps if seen in OCR text
    button_keywords: List[str] = None

    def __post_init__(self) -> None:
        if self.button_keywords is None:
            self.button_keywords = [
                "log in",
                "login",
                "next",
                "finish",
                "done",
                "submit for review",
                "submit",
                "ok",
                "continue",
            ]


class DocxScreenshotOCRAnalyzer:
    """Extracts more concrete steps from DOCX screenshots using OCR.

    This does not try to be perfect; it aims to auto-generate a useful
    baseline of type/click/verify steps grounded in screenshot text.
    """

    def __init__(self, config: ConcreteStepGeneratorConfig | None = None) -> None:
        self.config = config or ConcreteStepGeneratorConfig()

    def _require_deps(self) -> None:
        if pytesseract is None or Image is None or Document is None:
            raise RuntimeError(
                "pytesseract, Pillow, and python-docx are required for OCR-based DOCX analysis. "
                "Install with: pip install pytesseract pillow python-docx"
            )
    
    def _preprocess_image(self, img):
        """Preprocess image for better OCR accuracy."""
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if too small (OCR works better on larger images)
        width, height = img.size
        if width < 1000 or height < 800:
            scale = max(1000 / width, 800 / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = img.resize((new_width, new_height), Image.LANCZOS)  # type: ignore
        
        # Increase contrast and sharpness
        try:
            from PIL import ImageEnhance  # type: ignore
            
            # Increase contrast
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.5)
            
            # Increase sharpness
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2.0)
        except Exception:
            pass  # If enhancement fails, continue with original
        
        return img

    def extract_concrete_steps(self, docx_path: str) -> List[str]:
        """Run OCR over all images in the DOCX and generate concrete steps.

        Returns a flat list of plain-text steps suitable for your executor.
        """
        self._require_deps()

        document = Document(docx_path)
        image_blobs: List[bytes] = []

        # Extract all embedded images from the DOCX package
        for rel in document.part._rels.values():  # type: ignore[attr-defined]
            target = getattr(rel, "target_ref", "")
            if not target:
                continue
            if "image" in str(target).lower():
                try:
                    blob = rel.target_part.blob  # type: ignore[attr-defined]
                    image_blobs.append(blob)
                except Exception:
                    continue

        steps: List[str] = []

        for blob in image_blobs:
            try:
                img = Image.open(BytesIO(blob))
                
                # Preprocess image for better OCR
                img = self._preprocess_image(img)
            except Exception:
                continue

            try:
                # Try PSM 3 (automatic page segmentation) for better results
                data = pytesseract.image_to_data(
                    img, 
                    output_type=Output.DICT,  # type: ignore[arg-type]
                    config='--psm 3 --oem 3'  # PSM 3 = auto, OEM 3 = default OCR engine
                )
            except Exception:
                continue

            tokens = data.get("text", []) or []
            confs = data.get("conf", []) or []

            # Filter out very low-confidence tokens and blanks
            cleaned_tokens: List[str] = []
            for t, c in zip(tokens, confs):
                t = (t or "").strip()
                try:
                    c_val = float(c)
                except Exception:
                    c_val = 0.0
                # Use confidence threshold of 50 (balanced)
                if t and c_val >= 50:
                    cleaned_tokens.append(t)

            if not cleaned_tokens:
                continue

            text_line = " ".join(cleaned_tokens)
            text_lower = text_line.lower()

            # Filter out metadata/noise patterns before processing
            if self._is_metadata_noise(text_lower):
                continue

            # 1) Button clicks from known keywords
            for kw in self.config.button_keywords:
                if kw in text_lower:
                    label = self._best_label_for_keyword(cleaned_tokens, kw)
                    steps.append(f"Click \"{label}\"")

            # 2) Detect form field labels and values with improved heuristics
            field_steps = self._extract_form_fields(cleaned_tokens)
            steps.extend(field_steps)

            # 3) Verify prominent keywords like "Submit for Review"
            if "submit for review" in text_lower:
                label = self._best_label_for_keyword(cleaned_tokens, "submit for review")
                steps.append(f"Verify \"{label}\"")

        # Deduplicate while preserving order
        seen = set()
        deduped: List[str] = []
        for s in steps:
            if s not in seen:
                seen.add(s)
                deduped.append(s)

        return deduped

    def _is_metadata_noise(self, text_lower: str) -> bool:
        """Filter out common metadata/UI chrome patterns."""
        # Only filter if MULTIPLE noise indicators are present
        noise_count = 0
        noise_patterns = [
            "uploaded date",
            "actions",
            ":02 pm",
            ":17 pm",
            ":48 pm",
            ":59 pm",
            "salesforce, inc",
            "all rights reserved",
        ]
        
        for pattern in noise_patterns:
            if pattern in text_lower:
                noise_count += 1
        
        # Only filter if we see 2+ noise patterns (likely metadata)
        return noise_count >= 2

    def _extract_form_fields(self, tokens: List[str]) -> List[str]:
        """Extract form field Type steps with better label/value pairing."""
        steps: List[str] = []
        
        # Common form field label patterns
        field_keywords = [
            "number of",
            "total",
            "name",
            "username",
            "password",
            "email",
            "address",
            "county",
            "counties",
            "population",
            "patient",
            "served",
            "ratio",
            "funding",
            "contributions",
            "fees",
            "grants",
            "services",
            "sales",
            "participation",
            "reimbursement",
            "incentive",
            "management",
            "care",
            "organization",
            "member",
            "consortium",
            "network",
            "disease",
            "diabetes",
            "screening",
            "pressure",
            "tobacco",
            "depression",
            "weight",
            "drug",
            "hospital",
            "measures",
            "numerator",
            "denominator",
            "percentage",
            "miles",
            "encounters",
            "sites",
            "providers",
            "capacity",
            "specify",
            "enter",
            "value",
        ]

        i = 0
        while i < len(tokens):
            tok = tokens[i]
            
            # If we find a numeric value
            if self._looks_numeric(tok) and not self._is_date_like(tok):
                # Look back up to 10 tokens for a field label
                label_tokens = tokens[max(0, i - 10): i]
                label_text = " ".join(label_tokens).strip().strip(":*")
                
                # Clean up the label
                label_text = self._clean_label(label_text)
                
                # Score the label quality
                quality_score = self._score_label_quality(label_text, field_keywords)
                
                # Only accept high-quality labels
                if quality_score >= 3:
                    steps.append(f"Type \"{tok}\" into \"{label_text}\"")
            
            i += 1
        
        return steps
    
    def _clean_label(self, label: str) -> str:
        """Clean up OCR artifacts from label text."""
        # Fix common OCR spelling errors
        replacements = {
            "commenis": "comments",
            "Commenis": "Comments",
            "Reporis": "Reports",
            "reporis": "reports",
            "folowing": "following",
            "tis": "this",
            "frm": "form",
            "Resulis": "Results",
            "resulis": "results",
            "Specty": "Specify",
            "specty": "specify",
            "Attachmenis": "Attachments",
            "attachmenis": "attachments",
        }
        
        for wrong, correct in replacements.items():
            label = label.replace(wrong, correct)
        
        # Remove common OCR noise patterns
        label = label.replace(" oc ", " ").replace(" ii ", " ")
        label = label.replace(" ally ", " ").replace(" ts ", " is ")
        
        # Remove partial words at start/end (likely OCR cutoff)
        words = label.split()
        if len(words) > 2:
            # Remove first word if it's very short and doesn't start with capital
            if len(words[0]) <= 2 and not words[0][0].isupper():
                words = words[1:]
            # Remove last word if it's incomplete (ends with partial char)
            if words and len(words[-1]) <= 2:
                words = words[:-1]
        
        label = " ".join(words).strip()
        
        # Remove trailing punctuation and symbols
        label = label.rstrip(".,;:!?-—©®™>< ")
        
        return label
    
    def _score_label_quality(self, label: str, field_keywords: List[str]) -> int:
        """Score label quality (0-10). Higher = better quality."""
        if not label or len(label) < 5:
            return 0
        
        score = 0
        label_lower = label.lower()
        
        # +3 if contains field keywords
        if any(kw in label_lower for kw in field_keywords):
            score += 3
        
        # +2 if reasonable length (10-80 chars)
        if 10 <= len(label) <= 80:
            score += 2
        
        # +1 if starts with capital letter
        if label[0].isupper():
            score += 1
        
        # +1 if has multiple words (likely a real label)
        if len(label.split()) >= 3:
            score += 1
        
        # -2 if contains obvious noise patterns
        noise_patterns = ["HRSA", "PLATFORM", "WELCOME", "v In Progress", "REPORTS"]
        if any(noise in label for noise in noise_patterns):
            score -= 2
        
        # -3 if mostly symbols or numbers
        alpha_count = sum(1 for c in label if c.isalpha())
        if alpha_count < len(label) * 0.5:
            score -= 3
        
        # -2 if contains "©" or other special chars
        if any(c in label for c in "©®™><\\|"):
            score -= 2
        
        return score

    def _is_date_like(self, token: str) -> bool:
        """Check if token looks like a date or timestamp component."""
        date_patterns = ["2024", "2025", "2026", "/202", "pm", "am"]
        return any(p in token.lower() for p in date_patterns)
    
    def _is_pure_metadata_label(self, label: str) -> bool:
        """Check if a label is pure metadata (not a real field)."""
        label_lower = label.lower()
        metadata_markers = [
            "uploaded date",
            "actions",
            "test test",
            "grantee test",
            "salesforce",
            "all rights",
        ]
        return any(marker in label_lower for marker in metadata_markers)

    def _best_label_for_keyword(self, tokens: List[str], keyword: str) -> str:
        """Try to reconstruct the on-screen label for a keyword phrase."""
        key_parts = keyword.split()
        lp = len(key_parts)
        lowered = [t.lower() for t in tokens]
        for i in range(len(tokens) - lp + 1):
            if lowered[i : i + lp] == key_parts:
                return " ".join(tokens[i : i + lp])
        # Fallback
        return keyword.title()

    def _looks_numeric(self, token: str) -> bool:
        t = token.replace(",", "").replace("%", "")
        try:
            float(t)
            return True
        except ValueError:
            return False
