"""PDF Document Analyzer

Reads a PDF (e.g., SHCP Grantee user guide) and extracts a high-level
"what I understood" summary without any hardcoded business rules.

This is a first-pass analyzer focused on:
- document title and top-level headings
- sections that look like test areas ("Verify", "Steps", "Expected Result")
- bullet/numbered lists that describe behavior or rules
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

try:
    import fitz  # PyMuPDF
except ImportError:  # pragma: no cover
    fitz = None


@dataclass
class AnalyzedSection:
    title: str
    summary_points: List[str]


@dataclass
class PdfAnalysisResult:
    file_path: str
    total_pages: int
    headings: List[str]
    sections: List[AnalyzedSection]
    categorized_sections: Dict[str, List[str]]
    validation_rules: List[str]
    user_actions: List[str]
    expected_results: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "total_pages": self.total_pages,
            "headings": self.headings,
            "sections": [
                {"title": s.title, "summary_points": s.summary_points}
                for s in self.sections
            ],
            "categorized_sections": self.categorized_sections,
            "validation_rules": self.validation_rules,
            "user_actions": self.user_actions,
            "expected_results": self.expected_results,
        }


class PdfDocumentAnalyzer:
    """Lightweight analyzer that derives understanding purely from PDF text.

    No field names, values, or error messages are hardcoded. Everything is
    inferred from the document text using generic patterns.
    """

    def analyze(self, pdf_path: str) -> Dict[str, Any]:
        if fitz is None:
            raise RuntimeError("PyMuPDF (fitz) is not available in this environment")

        doc = fitz.open(pdf_path)
        all_text_lines: List[str] = []

        for page in doc:
            text = page.get_text("text") or ""
            lines = [ln.rstrip() for ln in text.splitlines()]
            all_text_lines.extend(lines)

        headings = self._extract_headings(all_text_lines)
        sections = self._extract_sections(all_text_lines)
        categorized_sections = self._categorize_lines(all_text_lines)
        validation_rules, user_actions, expected_results = self._extract_rule_like_info(all_text_lines)

        result = PdfAnalysisResult(
            file_path=pdf_path,
            total_pages=len(doc),
            headings=headings,
            sections=sections,
            categorized_sections=categorized_sections,
            validation_rules=validation_rules,
            user_actions=user_actions,
            expected_results=expected_results,
        )
        return result.to_dict()

    # ------------------------------------------------------------------
    # Heuristics
    # ------------------------------------------------------------------

    def _extract_headings(self, lines: List[str]) -> List[str]:
        """Extract likely headings.

        Heuristics:
        - short lines
        - either ALL CAPS or start with a number + dot (e.g., "1. Verify ...")
        - or contain keywords like "Verify", "Test Case", "Overview".
        """
        headings: List[str] = []
        seen = set()

        for raw in lines:
            line = raw.strip()
            if not line:
                continue
            if len(line) > 120:
                continue

            is_numbered = bool(re.match(r"^\d+\.\s+", line))
            is_all_caps = line.isupper() and len(line) > 3
            has_keyword = any(k in line for k in ["Verify", "Test Case", "Overview", "User Guide"])

            if is_numbered or is_all_caps or has_keyword:
                norm = line
                if norm not in seen:
                    headings.append(norm)
                    seen.add(norm)

        return headings

    def _extract_sections(self, lines: List[str]) -> List[AnalyzedSection]:
        """Group lines into numbered high-level sections and summarize key points.

        We now treat any line starting with "N." as a potential section heading,
        not just those that start with "Verify". This matches documents like the
        SHCP guide where steps are numbered but don't always include the word
        "Verify".
        """
        sections: List[AnalyzedSection] = []
        current_title: str | None = None
        buffer: List[str] = []

        def flush_current():
            nonlocal current_title, buffer
            if current_title and buffer:
                summary = self._summarize_block(buffer)
                if summary:
                    sections.append(AnalyzedSection(title=current_title, summary_points=summary))
            current_title = None
            buffer = []

        for raw in lines:
            line = raw.strip()
            if not line:
                continue

            # Section header: numbered line, e.g. "6. Select the CBD Performance Reports tab..."
            if re.match(r"^\d+\.\s+", line):
                flush_current()
                current_title = line
                continue

            # Inside a section, collect content
            if current_title:
                buffer.append(line)

        flush_current()
        return sections

    def _summarize_block(self, block_lines: List[str]) -> List[str]:
        """Produce a compact summary of a logical test area.

        Heuristics:
        - Extract short sentences that look like:
          - navigation (Navigate, Open, Click, Login)
          - behavior description (system displays, status updates, PDF generated)
        - Prefer lines containing: Steps, Expected Result, error, status.
        """
        points: List[str] = []

        for line in block_lines:
            low = line.lower()
            # Prefer lines that clearly describe steps or outcomes
            if any(k in low for k in ["steps", "expected", "result", "status", "navigate", "login", "open", "click", "generate pdf", "submit", "error", "updates", "saved", "listed"]):
                cleaned = line.strip()
                if cleaned and cleaned not in points:
                    points.append(cleaned)

        # Fallback: if nothing matched, take up to 3 short lines as generic summary
        if not points:
            for line in block_lines:
                if 0 < len(line) <= 120:
                    points.append(line.strip())
                    if len(points) >= 3:
                        break

        return points

    # ------------------------------------------------------------------
    # Additional higher-level extraction for grouping & rules
    # ------------------------------------------------------------------

    def _categorize_lines(self, lines: List[str]) -> Dict[str, List[str]]:
        """Classify lines into functional buckets based on simple keywords."""
        section_keywords = {
            "Navigation": ["login", "navigate", "select the", "click", "open"],
            "Report Lists": ["approved reports", "change requested", "in progress reports", "recently viewed", "submitted reports"],
            "Form Interaction": ["start (if the form", "edit (if the form", "required fields", "form page", "section name", "click next"],
            "Submission": ["submit for review", "submit to", "approval history", "status updates to submitted"],
            "PDF Generation": ["generate a pdf", "download pdf", "preview"],
            "Change Requests": ["request changes", "change request"],
            "Data Extracts": ["data extracts", "raw data report", "export"],
        }

        categorized: Dict[str, List[str]] = {k: [] for k in section_keywords}

        for raw in lines:
            line = raw.strip()
            if not line:
                continue
            low = line.lower()
            for section, keywords in section_keywords.items():
                if any(k in low for k in keywords):
                    if line not in categorized[section]:
                        categorized[section].append(line)
                    break

        return categorized

    def _extract_rule_like_info(self, lines: List[str]) -> tuple[list[str], list[str], list[str]]:
        """Extract simple validation rules, user actions, and expected results.

        This is still heuristic-based, but gives us structured pieces that can
        later be turned into POSITIVE / NEGATIVE / EDGE test cases.
        """
        char_limit_re = re.compile(r"(\d+)\s*(characters|chars)", re.IGNORECASE)
        numeric_limit_re = re.compile(r"(\d+)\s*(digits|numbers)", re.IGNORECASE)
        required_re = re.compile(r"(required field|must complete|cannot be blank|must be completed)", re.IGNORECASE)
        dropdown_re = re.compile(r"(dropdown|select\s+yes|select\s+no)", re.IGNORECASE)

        validation_rules: List[str] = []
        user_actions: List[str] = []
        expected_results: List[str] = []

        for raw in lines:
            line = raw.strip()
            if not line:
                continue
            low = line.lower()

            # Validation rules
            m_char = char_limit_re.search(line)
            if m_char:
                limit = m_char.group(1)
                desc = f"Character limit detected: {limit}"
                if desc not in validation_rules:
                    validation_rules.append(desc)

            m_num = numeric_limit_re.search(line)
            if m_num:
                limit = m_num.group(1)
                desc = f"Numeric limit detected: {limit} digits"
                if desc not in validation_rules:
                    validation_rules.append(desc)

            if required_re.search(line):
                desc = "Required field detected"
                if desc not in validation_rules:
                    validation_rules.append(desc)

            if dropdown_re.search(line):
                desc = "Dropdown behavior detected (specific allowed values / selection rules)"
                if desc not in validation_rules:
                    validation_rules.append(desc)

            # User actions
            if re.search(r"\b(enter|select|type|choose|fill|upload|click|navigate|open|login)\b", low):
                if line not in user_actions:
                    user_actions.append(line)

            # Expected results / system behavior
            if re.search(r"\b(error|updates|saved|status|displays|listed|generated|appears|logs out)\b", low):
                if line not in expected_results:
                    expected_results.append(line)

        return validation_rules, user_actions, expected_results
