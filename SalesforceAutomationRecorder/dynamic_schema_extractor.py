"""
Dynamic Schema Extractor
========================
Extracts schema from the current page during test execution.
When a placeholder is encountered (e.g., %American Indian or Alaska Native%):
1. Find that specific field on the page
2. Extract its schema (type, options, constraints)
3. Generate appropriate data
4. Save to data.csv
5. Continue execution
"""

import json
import csv
import os
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from DataGenerator import DataGenerator


class DynamicSchemaExtractor:
    """
    Extracts schema from Salesforce pages during test execution.
    Targeted extraction: finds specific fields by label and extracts their schema.
    """
    
    def __init__(self, page, data_file: str = "data.csv", schema_file: str = "fields.json"):
        self.page = page
        self.data_file = data_file
        self.schema_file = schema_file
        self.current_page_num = 0
        self.schema = {}
        self.data_rows = []
        self.current_row = {}
        self.extracted_fields = set()  # Track fields we've already extracted
        
        # Initialize DataGenerator for proper data generation
        self.data_generator = DataGenerator(schema_file)
        
        # Load existing schema if available
        self._load_existing_schema()
        self._load_existing_data()
    
    def _load_existing_schema(self):
        """Load existing schema if available"""
        if Path(self.schema_file).exists():
            try:
                with open(self.schema_file, 'r') as f:
                    self.schema = json.load(f)
                print(f"📋 Loaded existing schema with {len(self.schema)} pages")
            except:
                self.schema = {}
    
    def _load_existing_data(self):
        """Load existing data if available"""
        if Path(self.data_file).exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.data_rows = list(reader)
                    if self.data_rows:
                        self.current_row = self.data_rows[0]
                print(f"📊 Loaded existing data with {len(self.data_rows)} rows")
            except:
                self.data_rows = []
    
    def has_data_for_field(self, field_name: str) -> bool:
        """Check if we have data for a specific field"""
        if not self.current_row:
            return False
        
        # Check exact match
        if field_name in self.current_row:
            return True
        
        # Check case-insensitive match
        field_lower = field_name.lower()
        for key in self.current_row.keys():
            if key.lower() == field_lower:
                return True
            # Partial match
            if field_lower in key.lower() or key.lower() in field_lower:
                return True
        
        return False
    
    def get_field_value(self, field_name: str) -> Optional[str]:
        """Get value for a field from current data row"""
        if not self.current_row:
            return None
        
        # Exact match
        if field_name in self.current_row:
            return self.current_row[field_name]
        
        # Case-insensitive and partial match
        field_lower = field_name.lower()
        for key, value in self.current_row.items():
            if key.lower() == field_lower:
                return value
            if field_lower in key.lower() or key.lower() in field_lower:
                return value
        
        return None
    
    async def extract_current_page_schema(self) -> Dict:
        """
        Extract schema from the current page.
        Returns dict of field_label -> field_info
        """
        print(f"🔍 Extracting schema from current page...")
        page_schema = {}
        
        try:
            # Wait for form fields to be present
            await self.page.wait_for_selector("div.cCenterPanel fieldset", timeout=10000)
            
            # Find all input fields
            fields = await self._extract_input_fields()
            fields.extend(await self._extract_textarea_fields())
            fields.extend(await self._extract_select_fields())
            fields.extend(await self._extract_checkbox_fields())
            
            for field in fields:
                if field.get('label'):
                    page_schema[field['label']] = field
            
            print(f"✓ Extracted {len(page_schema)} fields from current page")
            
            # Update main schema
            self.current_page_num += 1
            self.schema[str(self.current_page_num)] = page_schema
            self._save_schema()
            
            # Generate data for new fields
            self._generate_data_for_page(page_schema)
            
            return page_schema
            
        except Exception as e:
            print(f"⚠️ Error extracting schema: {e}")
            return {}
    
    async def _extract_input_fields(self) -> List[Dict]:
        """Extract input field information"""
        fields = []
        
        try:
            # Find all input elements
            inputs = await self.page.query_selector_all("input:not([type='hidden']):not([type='checkbox']):not([type='radio'])")
            
            for inp in inputs:
                try:
                    # Get field attributes
                    field_info = await inp.evaluate("""
                        el => {
                            // Find label
                            let label = '';
                            const labelEl = el.closest('div')?.querySelector('label, .slds-form-element__label');
                            if (labelEl) {
                                label = labelEl.innerText.replace('*', '').trim();
                            }
                            if (!label) {
                                label = el.placeholder || el.name || el.id || '';
                            }
                            
                            return {
                                label: label,
                                type: el.type === 'number' ? 'number' : 'text',
                                required: el.required || el.hasAttribute('required'),
                                pattern: el.pattern || null,
                                minlength: el.minLength > 0 ? el.minLength : null,
                                maxlength: el.maxLength > 0 ? el.maxLength : null,
                                placeholder: el.placeholder || '',
                                name: el.name || '',
                                options: []
                            };
                        }
                    """)
                    
                    if field_info.get('label'):
                        fields.append(field_info)
                except:
                    continue
                    
        except Exception as e:
            print(f"  Warning extracting inputs: {e}")
        
        return fields
    
    async def _extract_textarea_fields(self) -> List[Dict]:
        """Extract textarea field information"""
        fields = []
        
        try:
            textareas = await self.page.query_selector_all("textarea")
            
            for ta in textareas:
                try:
                    field_info = await ta.evaluate("""
                        el => {
                            let label = '';
                            const labelEl = el.closest('div')?.querySelector('label, .slds-form-element__label');
                            if (labelEl) {
                                label = labelEl.innerText.replace('*', '').trim();
                            }
                            if (!label) {
                                label = el.placeholder || el.name || el.id || '';
                            }
                            
                            return {
                                label: label,
                                type: 'textarea',
                                required: el.required || el.hasAttribute('required'),
                                pattern: null,
                                minlength: el.minLength > 0 ? el.minLength : null,
                                maxlength: el.maxLength > 0 ? el.maxLength : 2000,
                                placeholder: el.placeholder || '',
                                name: el.name || '',
                                options: []
                            };
                        }
                    """)
                    
                    if field_info.get('label'):
                        fields.append(field_info)
                except:
                    continue
                    
        except Exception as e:
            print(f"  Warning extracting textareas: {e}")
        
        return fields
    
    async def _extract_select_fields(self) -> List[Dict]:
        """Extract select/dropdown field information"""
        fields = []
        
        try:
            # Standard selects
            selects = await self.page.query_selector_all("select")
            
            for sel in selects:
                try:
                    field_info = await sel.evaluate("""
                        el => {
                            let label = '';
                            const labelEl = el.closest('div')?.querySelector('label, .slds-form-element__label');
                            if (labelEl) {
                                label = labelEl.innerText.replace('*', '').trim();
                            }
                            if (!label) {
                                label = el.name || el.id || '';
                            }
                            
                            const options = Array.from(el.options).map(o => o.text.trim());
                            
                            return {
                                label: label,
                                type: 'select',
                                required: el.required || el.hasAttribute('required'),
                                pattern: null,
                                minlength: null,
                                maxlength: null,
                                placeholder: '',
                                name: el.name || '',
                                options: options
                            };
                        }
                    """)
                    
                    if field_info.get('label'):
                        fields.append(field_info)
                except:
                    continue
            
            # Lightning comboboxes
            comboboxes = await self.page.query_selector_all("[role='combobox'], lightning-combobox")
            
            for cb in comboboxes:
                try:
                    field_info = await cb.evaluate("""
                        el => {
                            let label = '';
                            const labelEl = el.querySelector('label, .slds-form-element__label');
                            if (labelEl) {
                                label = labelEl.innerText.replace('*', '').trim();
                            }
                            
                            // Get options if dropdown is open
                            const options = Array.from(el.querySelectorAll('[role="option"], lightning-base-combobox-item'))
                                .map(o => o.innerText.trim());
                            
                            return {
                                label: label,
                                type: 'select',
                                required: el.hasAttribute('required'),
                                pattern: null,
                                minlength: null,
                                maxlength: null,
                                placeholder: '',
                                name: '',
                                options: options
                            };
                        }
                    """)
                    
                    if field_info.get('label') and field_info['label'] not in [f.get('label') for f in fields]:
                        fields.append(field_info)
                except:
                    continue
                    
        except Exception as e:
            print(f"  Warning extracting selects: {e}")
        
        return fields
    
    async def _extract_checkbox_fields(self) -> List[Dict]:
        """Extract checkbox/multiselect field information"""
        fields = []
        
        try:
            # Checkbox groups
            checkboxes = await self.page.query_selector_all("input[type='checkbox']")
            
            # Group checkboxes by name
            checkbox_groups = {}
            for cb in checkboxes:
                try:
                    info = await cb.evaluate("""
                        el => {
                            let groupLabel = '';
                            const legend = el.closest('fieldset')?.querySelector('legend');
                            if (legend) {
                                groupLabel = legend.innerText.replace('*', '').trim();
                            }
                            
                            return {
                                name: el.name || '',
                                value: el.value || el.nextSibling?.textContent?.trim() || '',
                                groupLabel: groupLabel,
                                required: el.required
                            };
                        }
                    """)
                    
                    group_key = info.get('groupLabel') or info.get('name')
                    if group_key:
                        if group_key not in checkbox_groups:
                            checkbox_groups[group_key] = {
                                'label': group_key,
                                'type': 'multiselect',
                                'required': info.get('required', False),
                                'pattern': None,
                                'minlength': None,
                                'maxlength': None,
                                'placeholder': '',
                                'name': info.get('name', ''),
                                'options': []
                            }
                        if info.get('value'):
                            checkbox_groups[group_key]['options'].append(info['value'])
                except:
                    continue
            
            fields.extend(checkbox_groups.values())
                    
        except Exception as e:
            print(f"  Warning extracting checkboxes: {e}")
        
        return fields
    
    def _save_schema(self):
        """Save schema to JSON file"""
        os.makedirs(os.path.dirname(self.schema_file) or '.', exist_ok=True)
        with open(self.schema_file, 'w') as f:
            json.dump(self.schema, f, indent=4)
        print(f"💾 Schema saved to {self.schema_file}")
    
    def _generate_data_for_page(self, page_schema: Dict):
        """Generate data for fields in the page schema"""
        from DataGenerator import DataGenerator
        
        try:
            generator = DataGenerator()
        except:
            generator = None
        
        for label, field_info in page_schema.items():
            if label not in self.current_row:
                # Generate appropriate data based on field type
                value = self._generate_field_value(field_info, generator)
                self.current_row[label] = value
        
        # Save updated data
        self._save_data()
    
    def _generate_field_value(self, field_info: Dict, generator=None) -> str:
        """Generate a value for a field based on its type and constraints"""
        field_type = field_info.get('type', 'text')
        label = field_info.get('label', '')
        options = field_info.get('options', [])
        label_lower = label.lower()
        
        # PRIORITY 1: Check for Yes/No type fields (changes, modifications, etc.)
        # These are often comboboxes that get detected as 'text' type
        if self._label_indicates_yes_no(label_lower):
            return random.choice(['Yes', 'No'])
        
        # PRIORITY 2: Check if label indicates this should be a NUMBER field
        # (even if extracted type is 'text')
        if self._label_indicates_number(label_lower):
            return self._generate_number_from_label(label_lower, generator)
        
        # ---- select / multiselect / picklist / dropdown ----
        # IMPORTANT: Only use values from schema options, NEVER random data
        if field_type in ('select', 'multiselect', 'picklist', 'dropdown', 'combobox'):
            # Filter out invalid options
            valid_options = []
            for opt in options:
                if isinstance(opt, str):
                    opt = opt.strip()
                    # Skip empty, clear, and placeholder options
                    if opt and opt not in ('-- Clear --', '--None--', '-- None --', 'Select...', 'Select an Option'):
                        valid_options.append(opt)
            
            if valid_options:
                if field_type in ('select', 'picklist', 'dropdown', 'combobox'):
                    # Single select: pick exactly 1 option
                    return random.choice(valid_options)
                else:
                    # Multiselect: pick 1 to min(5, len) options
                    max_select = min(len(valid_options), 5)
                    num_to_select = random.randint(1, max_select)
                    selected = random.sample(valid_options, min(num_to_select, len(valid_options)))
                    return ', '.join(selected)
            else:
                # No valid options - return N/A, never random text
                print(f"  ⚠️ No valid options for {field_type} field '{label}'")
                return "N/A"
        
        # ---- number ----
        elif field_type == 'number':
            # Use DataGenerator if available
            if generator:
                try:
                    return str(generator._generate_contextual_number(label))
                except:
                    pass
            
            # Context-aware number ranges
            label_lower = label.lower()
            if 'county' in label_lower or 'counties' in label_lower:
                return str(random.randint(1, 25))
            elif 'population' in label_lower:
                return str(random.randint(5000, 150000))
            elif 'patient' in label_lower or 'client' in label_lower:
                return str(random.randint(500, 25000))
            else:
                return str(random.randint(0, 9999))
        
        # ---- text / textarea ----
        elif field_type in ('text', 'textarea'):
            # Use DataGenerator if available
            if generator:
                try:
                    maxlen = field_info.get('maxlength') or 500
                    return generator._generate_contextual_text(label, int(maxlen))
                except:
                    pass
            
            # Fallback: Generate contextual text based on label
            return self._generate_contextual_text_fallback(label, field_info.get('maxlength') or 500)
        
        else:
            # Unknown type - generate based on label context
            return self._generate_contextual_text_fallback(label, 100)
    
    def _generate_contextual_text_fallback(self, label: str, maxlength: int) -> str:
        """Generate contextual text based on field label when DataGenerator is not available"""
        label_lower = label.lower()
        maxlength = int(maxlength)
        
        # County names
        US_COUNTIES = [
            "Los Angeles County", "Cook County", "Harris County", "Maricopa County",
            "San Diego County", "Orange County", "Miami-Dade County", "Dallas County",
            "Kings County", "Clark County", "Queens County", "Riverside County"
        ]
        
        # Check label context - ORDER MATTERS (most specific first)
        
        # Changes/modifications - typically Yes/No
        if 'change' in label_lower and ('measures' in label_lower or 'target' in label_lower):
            return random.choice(["Yes", "No"])
        
        elif 'county' in label_lower or 'counties' in label_lower:
            if 'number' in label_lower or 'how many' in label_lower:
                return str(random.randint(1, 25))
            else:
                # List of county names
                num_counties = random.randint(2, min(6, len(US_COUNTIES)))
                counties = random.sample(US_COUNTIES, num_counties)
                return ", ".join(counties)[:maxlength]
        
        elif ('population' in label_lower or 'people' in label_lower) and 'change' not in label_lower:
            if 'number' in label_lower or 'how many' in label_lower:
                return str(random.randint(5000, 150000))
            else:
                descriptions = [
                    "Rural and underserved populations in the designated service area",
                    "Low-income families and individuals with limited access to healthcare",
                    "Medically underserved communities including elderly and disabled populations",
                ]
                return random.choice(descriptions)[:maxlength]
        
        elif 'patient' in label_lower or 'panel' in label_lower:
            return str(random.randint(500, 25000))
        
        elif 'justification' in label_lower or 'explain' in label_lower or 'describe' in label_lower or 'specify' in label_lower:
            reasons = [
                "Due to changes in the service area demographics and increased demand for services.",
                "Based on feedback from community stakeholders and partner organizations.",
                "In response to emerging health needs identified during the reporting period.",
                "To better align with updated federal guidelines and program objectives.",
            ]
            return random.choice(reasons)[:maxlength]
        
        elif 'change' in label_lower:
            return random.choice(["Yes", "No"])
        
        else:
            # Generic contextual text
            generic = [
                "Data provided as part of the reporting requirements.",
                "Information documented per program guidelines.",
                "Value entered based on current reporting period data.",
            ]
            return random.choice(generic)[:maxlength]
    
    def _label_indicates_yes_no(self, label_lower: str) -> bool:
        """Check if a label indicates the field should be Yes/No"""
        # Common patterns for Yes/No dropdown fields
        yes_no_patterns = [
            ('change', 'measure'),
            ('change', 'target'),
            ('change', 'population'),
            ('modification', ''),
            ('is there', ''),
            ('are there', ''),
            ('do you', ''),
            ('did you', ''),
            ('have you', ''),
            ('was there', ''),
            ('were there', ''),
        ]
        
        for pattern1, pattern2 in yes_no_patterns:
            if pattern1 in label_lower:
                if not pattern2 or pattern2 in label_lower:
                    return True
        
        return False
    
    def _label_indicates_number(self, label_lower: str) -> bool:
        """Check if a label indicates the field should contain a number"""
        number_indicators = [
            'number of',
            'how many',
            '# of',
            'count of',
            'total',
        ]
        
        # Check if label starts with or contains number indicators
        for indicator in number_indicators:
            if indicator in label_lower:
                # But exclude if it's asking for a description/specify
                if 'specify' not in label_lower and 'describe' not in label_lower and 'name' not in label_lower:
                    return True
        
        return False
    
    def _generate_number_from_label(self, label_lower: str, generator=None) -> str:
        """Generate a contextual number based on field label"""
        # Use DataGenerator if available
        if generator:
            try:
                return str(generator._generate_contextual_number(label_lower))
            except:
                pass
        
        # Context-aware number ranges based on label
        if 'county' in label_lower or 'counties' in label_lower:
            return str(random.randint(1, 25))
        elif 'population' in label_lower or 'people in the target' in label_lower:
            return str(random.randint(5000, 150000))
        elif 'patient' in label_lower or 'panel' in label_lower or 'client' in label_lower:
            return str(random.randint(500, 25000))
        elif 'partner' in label_lower or 'site' in label_lower:
            return str(random.randint(1, 15))
        elif 'service' in label_lower or 'encounter' in label_lower:
            return str(random.randint(1000, 50000))
        else:
            return str(random.randint(0, 9999))
    
    def _save_data(self):
        """Save current data row to CSV"""
        if not self.current_row:
            return
        
        # Get all headers
        headers = list(self.current_row.keys())
        
        # Check if file exists and has same headers
        file_exists = Path(self.data_file).exists()
        existing_headers = []
        
        if file_exists:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                existing_headers = next(reader, [])
        
        # Merge headers
        all_headers = existing_headers.copy()
        for h in headers:
            if h not in all_headers:
                all_headers.append(h)
        
        # Ensure current row has all headers
        for h in all_headers:
            if h not in self.current_row:
                self.current_row[h] = ''
        
        # Write data
        rows_to_write = []
        if file_exists and existing_headers:
            # Read existing rows
            with open(self.data_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows_to_write = list(reader)
            
            # Update first row or add new
            if rows_to_write:
                for h in all_headers:
                    if h not in rows_to_write[0] or not rows_to_write[0][h]:
                        rows_to_write[0][h] = self.current_row.get(h, '')
            else:
                rows_to_write.append(self.current_row)
        else:
            rows_to_write = [self.current_row]
        
        # Write all data
        with open(self.data_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=all_headers)
            writer.writeheader()
            writer.writerows(rows_to_write)
        
        print(f"💾 Data saved to {self.data_file}")
    
    async def ensure_data_for_placeholder(self, placeholder: str) -> Optional[str]:
        """
        Ensure we have data for a placeholder.
        1. Check existing data
        2. Try to generate from fields.json schema
        3. Fall back to page extraction
        """
        # Check if we already have data
        value = self.get_field_value(placeholder)
        if value:
            print(f"✓ Found existing data for '{placeholder}': {value}")
            return value
        
        # Skip if already tried to extract this field
        if placeholder in self.extracted_fields:
            print(f"⚠️ Already attempted extraction for '{placeholder}', no data found")
            return None
        
        print(f"📝 No data for '{placeholder}'. Checking schema...")
        
        # PRIORITY 1: Try to generate from fields.json schema using DataGenerator
        value = self._generate_from_schema(placeholder)
        if value:
            self.current_row[placeholder] = value
            self.extracted_fields.add(placeholder)
            self._save_data()
            print(f"✓ Generated from schema for '{placeholder}': {value}")
            return value
        
        # PRIORITY 2: Extract field from page and generate data
        print(f"📝 Field not in schema. Extracting from page...")
        field_info = await self._find_and_extract_field(placeholder)
        
        if field_info:
            print(f"✓ Found field '{placeholder}' on page: type={field_info.get('type')}")
            value = self._generate_field_value(field_info, self.data_generator)
            self.current_row[placeholder] = value
            self.extracted_fields.add(placeholder)
            self._save_data()
            print(f"✓ Generated value for '{placeholder}': {value}")
            return value
        else:
            print(f"⚠️ Could not find field '{placeholder}' on page")
            self.extracted_fields.add(placeholder)
            return None
    
    def _generate_from_schema(self, field_label: str) -> Optional[str]:
        """
        Generate data for a field using the schema from fields.json.
        Matches by label text (case-insensitive, partial match).
        """
        if not self.data_generator or not self.data_generator._schema:
            return None
        
        schema = self.data_generator._schema
        label_lower = field_label.lower().strip()
        
        # Search in schema (handle both flat and paged formats)
        if self.data_generator._is_paged_schema():
            for page_num in schema.keys():
                for key, field_info in schema[page_num].items():
                    schema_label = field_info.get('label', '').lower().replace('*', '').strip()
                    if self._labels_match(label_lower, schema_label):
                        value = self.data_generator.generate_correct(key)
                        if value:
                            return value
        else:
            for key, field_info in schema.items():
                schema_label = field_info.get('label', '').lower().replace('*', '').strip()
                if self._labels_match(label_lower, schema_label):
                    value = self.data_generator.generate_correct(key)
                    if value:
                        return value
        
        return None
    
    def _labels_match(self, label1: str, label2: str) -> bool:
        """Check if two labels match (exact or partial)"""
        if label1 == label2:
            return True
        if label1 in label2 or label2 in label1:
            return True
        # Match first few words
        words1 = label1.split()[:4]
        words2 = label2.split()[:4]
        if words1 and words2 and words1 == words2:
            return True
        return False
    
    async def _find_and_extract_field(self, field_label: str) -> Optional[Dict]:
        """
        Find a specific field on the page by its label.
        Returns field info dict with type, options, constraints.
        """
        try:
            # Wait for page to be stable
            await self.page.wait_for_load_state('networkidle', timeout=5000)
        except:
            pass
        
        # Strategy 1: Find by exact label text in Salesforce OmniScript forms
        field_info = await self._find_field_by_label_text(field_label)
        if field_info:
            return field_info
        
        # Strategy 2: Find by partial label match
        field_info = await self._find_field_by_partial_label(field_label)
        if field_info:
            return field_info
        
        # Strategy 3: Find input/textarea near label text
        field_info = await self._find_field_near_text(field_label)
        if field_info:
            return field_info
        
        return None
    
    async def _find_field_by_label_text(self, label: str) -> Optional[Dict]:
        """Find field by exact label text match"""
        try:
            # JavaScript to find field by label in Salesforce OmniScript
            result = await self.page.evaluate(f'''
                (labelText) => {{
                    // Normalize the label text
                    const normalizedLabel = labelText.trim().toLowerCase();
                    
                    // Find all labels and legend elements
                    const labelElements = document.querySelectorAll('label, legend, .slds-form-element__label, span.nds-form-element__label');
                    
                    for (const labelEl of labelElements) {{
                        const text = labelEl.innerText.replace(/\\*/g, '').trim();
                        if (text.toLowerCase() === normalizedLabel) {{
                            // Found the label, now find the associated field
                            const container = labelEl.closest('.slds-form-element, .nds-form-element, fieldset, div');
                            if (!container) continue;
                            
                            // Check for input
                            const input = container.querySelector('input:not([type="hidden"]):not([type="checkbox"]):not([type="radio"])');
                            if (input) {{
                                return {{
                                    label: text,
                                    type: input.type === 'number' ? 'number' : 'text',
                                    required: input.required || input.hasAttribute('required'),
                                    pattern: input.pattern || null,
                                    maxlength: input.maxLength > 0 ? input.maxLength : null,
                                    options: []
                                }};
                            }}
                            
                            // Check for textarea
                            const textarea = container.querySelector('textarea');
                            if (textarea) {{
                                return {{
                                    label: text,
                                    type: 'textarea',
                                    required: textarea.required,
                                    pattern: null,
                                    maxlength: textarea.maxLength > 0 ? textarea.maxLength : 2000,
                                    options: []
                                }};
                            }}
                            
                            // Check for select
                            const select = container.querySelector('select');
                            if (select) {{
                                const options = Array.from(select.options).map(o => o.text.trim());
                                return {{
                                    label: text,
                                    type: 'select',
                                    required: select.required,
                                    pattern: null,
                                    maxlength: null,
                                    options: options
                                }};
                            }}
                            
                            // Check for checkboxes (multiselect)
                            const checkboxes = container.querySelectorAll('input[type="checkbox"]');
                            if (checkboxes.length > 0) {{
                                const options = [];
                                checkboxes.forEach(cb => {{
                                    const cbLabel = cb.closest('label, .slds-checkbox, .nds-checkbox');
                                    if (cbLabel) {{
                                        options.push(cbLabel.innerText.trim());
                                    }} else if (cb.nextSibling) {{
                                        options.push(cb.nextSibling.textContent?.trim() || cb.value);
                                    }}
                                }});
                                return {{
                                    label: text,
                                    type: 'multiselect',
                                    required: false,
                                    pattern: null,
                                    maxlength: null,
                                    options: options
                                }};
                            }}
                        }}
                    }}
                    return null;
                }}
            ''', label)
            
            return result
        except Exception as e:
            print(f"  Error in _find_field_by_label_text: {e}")
            return None
    
    async def _find_field_by_partial_label(self, label: str) -> Optional[Dict]:
        """Find field by partial label match"""
        try:
            result = await self.page.evaluate(f'''
                (labelText) => {{
                    const normalizedLabel = labelText.trim().toLowerCase();
                    const labelElements = document.querySelectorAll('label, legend, .slds-form-element__label, span.nds-form-element__label');
                    
                    for (const labelEl of labelElements) {{
                        const text = labelEl.innerText.replace(/\\*/g, '').trim();
                        // Partial match
                        if (text.toLowerCase().includes(normalizedLabel) || normalizedLabel.includes(text.toLowerCase())) {{
                            const container = labelEl.closest('.slds-form-element, .nds-form-element, fieldset, div');
                            if (!container) continue;
                            
                            const input = container.querySelector('input:not([type="hidden"]):not([type="checkbox"])');
                            if (input) {{
                                return {{
                                    label: text,
                                    type: input.type === 'number' ? 'number' : 'text',
                                    required: input.required,
                                    pattern: input.pattern || null,
                                    maxlength: input.maxLength > 0 ? input.maxLength : null,
                                    options: []
                                }};
                            }}
                            
                            const textarea = container.querySelector('textarea');
                            if (textarea) {{
                                return {{
                                    label: text,
                                    type: 'textarea',
                                    required: textarea.required,
                                    pattern: null,
                                    maxlength: textarea.maxLength > 0 ? textarea.maxLength : 2000,
                                    options: []
                                }};
                            }}
                        }}
                    }}
                    return null;
                }}
            ''', label)
            
            return result
        except Exception as e:
            print(f"  Error in _find_field_by_partial_label: {e}")
            return None
    
    async def _find_field_near_text(self, label: str) -> Optional[Dict]:
        """Find input/textarea that appears near the label text"""
        try:
            # Try XPath to find input following text
            selectors_to_try = [
                f"xpath=//*[contains(normalize-space(text()), '{label}')]/following::input[1]",
                f"xpath=//*[contains(normalize-space(text()), '{label}')]/following::textarea[1]",
                f"*:has-text('{label}') >> input",
                f"*:has-text('{label}') >> textarea",
            ]
            
            for selector in selectors_to_try:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        tag = await element.evaluate('el => el.tagName.toLowerCase()')
                        input_type = await element.evaluate('el => el.type || ""')
                        
                        return {
                            'label': label,
                            'type': 'number' if input_type == 'number' else ('textarea' if tag == 'textarea' else 'text'),
                            'required': False,
                            'pattern': None,
                            'maxlength': None,
                            'options': []
                        }
                except:
                    continue
            
            return None
        except Exception as e:
            print(f"  Error in _find_field_near_text: {e}")
            return None
    
    def on_page_navigation(self):
        """Called when navigating to a new page (e.g., clicking Next)"""
        print(f"📄 Page navigation. Clearing extracted fields for fresh extraction on new page.")
        # Don't clear extracted_fields - keep data across pages


# Singleton instance
_dynamic_extractor: Optional[DynamicSchemaExtractor] = None


def get_dynamic_extractor(page=None) -> Optional[DynamicSchemaExtractor]:
    """Get or create the dynamic extractor instance"""
    global _dynamic_extractor
    if page is not None:
        _dynamic_extractor = DynamicSchemaExtractor(page)
    return _dynamic_extractor


def reset_dynamic_extractor():
    """Reset the singleton instance"""
    global _dynamic_extractor
    _dynamic_extractor = None
