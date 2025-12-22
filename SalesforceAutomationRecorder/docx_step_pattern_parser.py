"""DOCX Step Pattern Parser

Parses a DOCX like "SHCP Screenshots.docx" that follows a
STEP / Description / Screenshot / Action pattern and produces
structured step definitions without hardcoding any field names
or values.

Relies purely on the document text structure:
- Headings like "STEP 1 — Login"
- A line starting with "Description:" followed by one or more
  description lines until a blank line or "Screenshot" marker
- A section starting with "Action / Input:" followed by bullet
  lines (starting with '-', '•', '*') which are treated as
  action steps.

This parser does NOT inspect image contents; it only reads the
DOCX text. That keeps it generic and free of any hardcoded UI
knowledge.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Dict, Any

try:
    from docx import Document  # type: ignore
except ImportError:  # pragma: no cover
    Document = None  # type: ignore


@dataclass
class DocxStep:
    step_number: int
    title: str
    description: str
    actions: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DocxStepPatternParser:
    """Parser for STEP/Description/Action DOCX user guides."""

    def parse_docx(self, path: str) -> List[Dict[str, Any]]:
        if Document is None:
            raise RuntimeError(
                "python-docx is required to parse DOCX files. "
                "Install it with: pip install python-docx"
            )

        doc = Document(path)
        paragraphs: List[str] = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                paragraphs.append("")
            else:
                paragraphs.append(text)

        steps: List[DocxStep] = []

        current_step_number: int | None = None
        current_title: str = ""
        current_description_lines: List[str] = []
        current_actions: List[str] = []
        in_description = False
        in_actions = False

        def flush_step() -> None:
            nonlocal current_step_number, current_title, current_description_lines, current_actions
            if current_step_number is None:
                return
            description = " ".join(l for l in current_description_lines if l).strip()
            step = DocxStep(
                step_number=current_step_number,
                title=current_title.strip(),
                description=description,
                actions=[a.strip() for a in current_actions if a.strip()],
            )
            steps.append(step)
            current_step_number = None
            current_title = ""
            current_description_lines = []
            current_actions = []

        for raw in paragraphs:
            line = raw.strip()

            # New STEP header, e.g. "STEP 1 — Login"
            if line.upper().startswith("STEP "):
                flush_step()

                step_num = None
                title = line
                try:
                    rest = line[5:].strip()  # after 'STEP '
                    parts = rest.split(" ", 1)
                    step_num = int(parts[0].strip("-—"))
                    if len(parts) > 1:
                        title = parts[1].lstrip("-— ")
                except Exception:
                    step_num = None

                current_step_number = step_num if step_num is not None else (len(steps) + 1)
                current_title = title
                in_description = False
                in_actions = False
                continue

            if line.lower().startswith("description:"):
                in_description = True
                in_actions = False
                remaining = line[len("Description:"):].strip()
                if remaining:
                    current_description_lines.append(remaining)
                continue

            if line.lower().startswith("screenshot placeholder"):
                in_description = False
                in_actions = False
                continue

            if line.lower().startswith("action / input:") or line.lower().startswith("action/input:"):
                in_actions = True
                in_description = False
                continue

            # Blank line ends description section
            if not line:
                if in_description:
                    in_description = False
                continue

            if in_description:
                current_description_lines.append(line)
                continue

            if in_actions:
                # Bullet lines may start with -, •, * or similar
                bullet = line
                if bullet[0] in {"-", "•", "*"}:
                    bullet = bullet[1:].strip()
                current_actions.append(bullet)
                continue

        # Flush last step
        flush_step()

        return [s.to_dict() for s in steps]
