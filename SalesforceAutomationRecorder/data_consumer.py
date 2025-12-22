"""
Data Consumer
Manages consumption of test data from data.csv with tracking of used rows.

Features:
- Loads data from data.csv
- Tracks which rows have been used (via data_usage.json)
- Returns next available row
- Generates data if CSV doesn't exist
- Replaces placeholders in test steps with actual data
"""

import csv
import json
import os
import re
import difflib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple

# Placeholder pattern: %field_name%
PLACEHOLDER_PATTERN = re.compile(r'%([^%]+)%')


class DataConsumer:
    """
    Manages test data consumption from data.csv with usage tracking.
    """
    
    def __init__(self, data_file: str = "outputs/data.csv", usage_file: str = "outputs/data_usage.json"):
        self.data_file = data_file
        self.usage_file = usage_file
        self.headers: List[str] = []
        self.rows: List[Dict] = []
        self.usage_data: Dict = {"used_rows": [], "last_used_index": -1}
        self.current_row: Optional[Dict] = None
        self.current_row_index: int = -1
        
        # Load existing data and usage info
        self._load_usage()
        if self.data_exists():
            self._load_data()
    
    def data_exists(self) -> bool:
        """Check if data.csv exists"""
        return Path(self.data_file).exists()
    
    def _load_data(self):
        """Load data from CSV file"""
        try:
            with open(self.data_file, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                self.headers = reader.fieldnames or []
                self.rows = list(reader)
            print(f"📊 Loaded {len(self.rows)} rows from {self.data_file}")
        except Exception as e:
            print(f"⚠️ Error loading data: {e}")
            self.headers = []
            self.rows = []

    def _strip_wrapping_quotes(self, value: str) -> str:
        if value is None:
            return ""
        s = str(value).strip()
        if len(s) >= 2 and ((s.startswith("'") and s.endswith("'")) or (s.startswith('"') and s.endswith('"'))):
            return s[1:-1].strip()
        return s

    def _to_bool(self, value) -> bool:
        s = self._strip_wrapping_quotes(value).strip().lower()
        return s in {"true", "1", "yes", "y"}

    def _scenario_type_normalized(self, value: str) -> str:
        return self._strip_wrapping_quotes(value).strip().lower()

    def _get_used_flag_column(self) -> Optional[str]:
        # Prefer the CSV column that exists in this project
        for candidate in ["Data Used", "Used", "used"]:
            if candidate in (self.headers or []):
                return candidate
        return None

    def _read_all_rows_from_csv(self) -> Tuple[List[str], List[Dict[str, str]]]:
        with open(self.data_file, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            rows = list(reader)
        return fieldnames, rows

    def _write_all_rows_to_csv(self, fieldnames: List[str], rows: List[Dict[str, str]]):
        tmp_path = f"{self.data_file}.tmp"
        with open(tmp_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(rows)
        os.replace(tmp_path, self.data_file)

    def get_next_available_row_by_type(self, data_type: str) -> Tuple[Optional[Dict], int]:
        """Get next unused row filtered by Scenario Type and Data Used flag."""
        if not self.data_exists():
            return None, -1

        if not self.rows:
            self._load_data()

        data_type_norm = (data_type or "positive").strip().lower()
        if data_type_norm == "mixed":
            data_type_norm = "any"

        used_col = self._get_used_flag_column()

        used_rows = set(self.usage_data.get("used_rows", []))
        for idx, row in enumerate(self.rows):
            if idx in used_rows:
                continue

            if used_col and self._to_bool(row.get(used_col)):
                continue

            scenario_type = self._scenario_type_normalized(row.get('Scenario Type', ''))
            if data_type_norm == "any":
                pass
            elif data_type_norm == "positive" and scenario_type != "positive":
                continue
            elif data_type_norm == "negative" and scenario_type != "negative":
                continue

            self.current_row = row
            self.current_row_index = idx
            return row, idx

        return None, -1
    
    def _load_usage(self):
        """Load usage tracking data"""
        if Path(self.usage_file).exists():
            try:
                with open(self.usage_file, 'r') as f:
                    self.usage_data = json.load(f)
            except:
                self.usage_data = {"used_rows": [], "last_used_index": -1}
    
    def _save_usage(self):
        """Save usage tracking data"""
        with open(self.usage_file, 'w') as f:
            json.dump(self.usage_data, f, indent=2)
    
    def get_next_available_row(self) -> Tuple[Optional[Dict], int]:
        """
        Get the next unused row from data.csv.
        Returns (row_data, row_index) or (None, -1) if no rows available.
        """
        if not self.rows:
            return None, -1
        
        used_rows = set(self.usage_data.get("used_rows", []))
        
        # Find first unused row
        for idx, row in enumerate(self.rows):
            if idx not in used_rows:
                self.current_row = row
                self.current_row_index = idx
                return row, idx
        
        # All rows used - reset and start over
        print("⚠️ All data rows used. Resetting usage tracking...")
        self.usage_data = {"used_rows": [], "last_used_index": -1}
        self._save_usage()
        
        if self.rows:
            self.current_row = self.rows[0]
            self.current_row_index = 0
            return self.rows[0], 0
        
        return None, -1
    
    def mark_row_as_used(self, row_index: int = None):
        """Mark a row as used"""
        if row_index is None:
            row_index = self.current_row_index
        
        if row_index >= 0:
            if row_index not in self.usage_data["used_rows"]:
                self.usage_data["used_rows"].append(row_index)
            self.usage_data["last_used_index"] = row_index
            self.usage_data["last_used_time"] = datetime.now().isoformat()
            self._save_usage()

            # Also persist the used marker into the CSV, if column exists.
            try:
                if self.data_exists():
                    fieldnames, rows = self._read_all_rows_from_csv()
                    used_col = None
                    for candidate in ["Data Used", "Used", "used"]:
                        if candidate in fieldnames:
                            used_col = candidate
                            break
                    if used_col and 0 <= row_index < len(rows):
                        rows[row_index][used_col] = "True"
                        self._write_all_rows_to_csv(fieldnames, rows)
                        self._load_data()
            except Exception as e:
                print(f"⚠️ Failed to update Data Used flag in CSV: {e}")

            print(f"✓ Marked row {row_index + 1} as used")

    def reset_used_flags_in_csv(self):
        """Reset the CSV used marker column to False for all rows."""
        if not self.data_exists():
            return

        try:
            fieldnames, rows = self._read_all_rows_from_csv()
            used_col = None
            for candidate in ["Data Used", "Used", "used"]:
                if candidate in fieldnames:
                    used_col = candidate
                    break
            if not used_col:
                return
            for row in rows:
                row[used_col] = "False"
            self._write_all_rows_to_csv(fieldnames, rows)
            self._load_data()
        except Exception as e:
            print(f"⚠️ Failed to reset used flags in CSV: {e}")
    
    def generate_data_if_needed(self, num_rows: int = 100) -> bool:
        """
        Generate data.csv if it doesn't exist.
        Returns True if data is available (existing or newly generated).
        """
        if self.data_exists():
            if not self.rows:
                self._load_data()
            return len(self.rows) > 0
        
        print("📝 data.csv not found. Generating test data...")

        # This project generates data.csv via DatasetGenerator.extract_schema_output_csv()
        # at runtime when placeholders are encountered (because it requires a live Playwright page).
        # DataConsumer does not have access to a page instance, so it cannot generate data by itself.
        print("⚠️ Automatic generation from DataConsumer is not supported (no page context).")
        print("   Run a test with placeholders to trigger DatasetGenerator, or generate data via your schema extraction workflow.")
        return False
    
    def has_placeholder(self, text: str) -> bool:
        """Check if text contains placeholders"""
        return bool(PLACEHOLDER_PATTERN.search(text))
    
    def get_placeholders(self, text: str) -> List[str]:
        """Extract all placeholders from text"""
        return PLACEHOLDER_PATTERN.findall(text)
    
    def find_matching_field(self, placeholder: str) -> Optional[str]:
        """Find matching header for a placeholder"""
        def normalize(s: str) -> str:
            s = (s or "").lower().strip()
            s = re.sub(r"[^a-z0-9]+", " ", s)
            s = " ".join(s.split())
            return s

        stopwords = {
            "a", "an", "and", "or", "the", "of", "on", "in", "to", "for", "per", "via", "as", "if", "is", "are"
        }

        def tokenize(s: str) -> set:
            toks = [t for t in normalize(s).split() if t and t not in stopwords]
            return set(toks)

        placeholder_norm = normalize(placeholder)
        placeholder_tokens = tokenize(placeholder)

        if not placeholder_norm:
            return None

        # Exact normalized match
        for header in self.headers:
            if normalize(header) == placeholder_norm:
                return header

        # Strong fuzzy match (choose best score, require high confidence)
        best_header = None
        best_score = 0.0

        for header in self.headers:
            header_norm = normalize(header)
            if not header_norm:
                continue

            header_tokens = tokenize(header)
            union = placeholder_tokens | header_tokens
            jaccard = (len(placeholder_tokens & header_tokens) / len(union)) if union else 0.0
            seq = difflib.SequenceMatcher(None, placeholder_norm, header_norm).ratio()

            # Weighted score prefers token-level agreement to avoid false positives from common words
            score = (0.7 * jaccard) + (0.3 * seq)
            if score > best_score:
                best_score = score
                best_header = header

        # Require a strong match; otherwise treat as missing so new data can be generated
        if best_header is not None and best_score >= 0.75:
            return best_header

        return None
    
    def replace_placeholders(self, text: str, data_row: Dict = None) -> str:
        """
        Replace placeholders in text with actual data values.
        Uses current_row if data_row not provided.
        """
        if data_row is None:
            data_row = self.current_row
        
        if not data_row:
            return text
        
        result = text
        placeholders = self.get_placeholders(text)
        
        for placeholder in placeholders:
            matching_field = self.find_matching_field(placeholder)
            if matching_field and matching_field in data_row:
                value = data_row[matching_field]
                if value and str(value).lower() not in ['n/a', 'na', '']:
                    cleaned = str(value).strip()
                    if (cleaned.startswith("'") and cleaned.endswith("'")) or (cleaned.startswith('"') and cleaned.endswith('"')):
                        cleaned = cleaned[1:-1]
                    result = result.replace(f"%{placeholder}%", cleaned)
        
        return result
    
    def process_step(self, step: str) -> Tuple[str, bool]:
        """
        Process a test step, replacing placeholders with data.
        
        Returns:
            (processed_step, had_placeholders)
        """
        if not self.has_placeholder(step):
            return step, False
        
        # Ensure we have data
        if not self.current_row:
            row, idx = self.get_next_available_row()
            if not row:
                # Try to generate data
                if self.generate_data_if_needed():
                    row, idx = self.get_next_available_row()
            
            if not row:
                print(f"⚠️ No data available for placeholders in: {step[:50]}...")
                return step, True
        
        processed = self.replace_placeholders(step)
        return processed, True
    
    def get_usage_summary(self) -> Dict:
        """Get summary of data usage"""
        total_rows = len(self.rows)

        used_col = self._get_used_flag_column()
        if used_col:
            used_count = sum(1 for r in (self.rows or []) if self._to_bool(r.get(used_col)))
        else:
            used_count = len(self.usage_data.get("used_rows", []))
        
        return {
            "total_rows": total_rows,
            "used_rows": used_count,
            "available_rows": total_rows - used_count,
            "last_used_index": self.usage_data.get("last_used_index", -1),
            "last_used_time": self.usage_data.get("last_used_time", None)
        }


# Singleton instance for shared access
_data_consumer: Optional[DataConsumer] = None


def get_data_consumer() -> DataConsumer:
    """Get or create the singleton DataConsumer instance"""
    global _data_consumer
    if _data_consumer is None:
        _data_consumer = DataConsumer()
    return _data_consumer


def reset_data_consumer():
    """Reset the singleton instance (useful for testing)"""
    global _data_consumer
    _data_consumer = None
