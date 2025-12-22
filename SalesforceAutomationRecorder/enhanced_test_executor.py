"""
Enhanced Test Executor - Compatible with Original Test Format
Supports: Click "Text", Type "value" into "Field", Wait for X seconds, Select "option" from Dropdown "Field"

Dynamic Data Generation Flow:
1. When placeholder encountered (e.g., %Number of Counties Served%)
2. If data.csv doesn't exist or doesn't have the field:
   - Crawl current page to extract schema
   - Generate data for extracted fields
   - Save to data.csv
3. Replace placeholder with generated value
4. Continue execution
5. On "Next" button click, repeat extraction for new page
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
from real_test_executor import TestExecutor

# Placeholder pattern: %field_name%
PLACEHOLDER_PATTERN = re.compile(r'%([^%]+)%')


class EnhancedTestExecutor(TestExecutor):
    """Extended executor with dynamic schema extraction and data generation"""
    
    def __init__(self):
        super().__init__()
        self.data_consumer = None
        self.dynamic_extractor = None
        self.data_initialized = False
        self.current_dataset_index = -1
        self.use_dynamic_extraction = True  # Enable dynamic page crawling
        self.positive_scenarios = 5
        self.negative_scenarios = 5
        self.data_type = 'positive'
        self.test_steps_file = None
        self.form_name = None
        self.all_test_steps = []  # Store all test steps for context
        self.current_step_index = -1
    
    def _ensure_data_consumer(self):
        """Initialize data consumer on first use"""
        if self.data_consumer is None:
            from data_consumer import get_data_consumer
            self.data_consumer = get_data_consumer()
    
    def _ensure_dynamic_extractor(self):
        """Initialize dynamic extractor with current page"""
        if self.dynamic_extractor is None and self.page is not None:
            from dynamic_schema_extractor import DynamicSchemaExtractor
            self.dynamic_extractor = DynamicSchemaExtractor(self.page)
            self.log('info', '🔍 Dynamic schema extractor initialized')
    
    def set_data_generation_params(self, positive_scenarios: int, negative_scenarios: int, data_type: str):
        """Set data generation parameters"""
        self.positive_scenarios = positive_scenarios
        self.negative_scenarios = negative_scenarios
        self.data_type = data_type
        self.log('info', f'📊 Data generation params set: {positive_scenarios} positive, {negative_scenarios} negative, using {data_type} data')
    
    async def generate_data_for_current_page(self, test_steps_text: str):
        """
        Generate data for the current page using DatasetGenerator.
        This is called when placeholders are detected and data.csv doesn't have the required fields.
        Uses DatasetGenerator.extract_schema_output_csv() to extract schema from the current page
        and generate/update outputs/data.csv.
        """
        if not self.page:
            self.log('error', 'No page available for data generation')
            return False
        
        try:
            import tempfile
            import os

            from DatasetGenerator import DatasetGenerator

            # Create a temporary file with test steps
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                f.write(test_steps_text)
                temp_steps_file = f.name

            self.log('info', '🔍 Calling DatasetGenerator.extract_schema_output_csv()...')

            dataset_gen = DatasetGenerator(
                test_steps=temp_steps_file,
                positive_cases=self.positive_scenarios,
                negative_cases=self.negative_scenarios,
                page=self.page,
                form_name=self.form_name or "",
                overwrite_csv=False,
            )

            labels = await dataset_gen.extract_schema_output_csv()

            if not labels:
                self.log('error', '❌ DatasetGenerator extracted 0 fields; schema/data not generated for this page')
                os.unlink(temp_steps_file)
                return False

            # Clean up temp file
            os.unlink(temp_steps_file)

            self.log('success', f'✅ DatasetGenerator generated/updated outputs/data.csv for {len(labels)} fields')
            return True
        except Exception as e:
            self.log('error', f'Failed to generate data via DatasetGenerator: {str(e)}')
            import traceback
            traceback.print_exc()
            return False
    
    def has_placeholder(self, text: str) -> bool:
        """Check if text contains placeholders like %field_name%"""
        return bool(PLACEHOLDER_PATTERN.search(text))

    def _extract_placeholders_from_steps(self, steps: list) -> list:
        placeholders = []
        if not steps:
            return placeholders
        for s in steps:
            if not s:
                continue
            placeholders.extend(PLACEHOLDER_PATTERN.findall(str(s)))
        # Preserve order but de-duplicate
        seen = set()
        ordered = []
        for ph in placeholders:
            if ph not in seen:
                ordered.append(ph)
                seen.add(ph)
        return ordered

    def _get_current_page_segment_steps(self, all_steps: list) -> list:
        if not all_steps:
            return []
        idx = self.current_step_index if self.current_step_index is not None else -1
        if idx < 0:
            idx = 0
        if idx >= len(all_steps):
            idx = len(all_steps) - 1

        # Segment boundaries are between "Next"-type clicks.
        prev_next_idx = -1
        for i in range(idx, -1, -1):
            if self._is_next_button_click(str(all_steps[i])):
                prev_next_idx = i
                break

        next_next_idx = len(all_steps)
        for i in range(idx, len(all_steps)):
            if i != idx and self._is_next_button_click(str(all_steps[i])):
                next_next_idx = i
                break

        seg_start = prev_next_idx + 1
        seg_end = next_next_idx
        return all_steps[seg_start:seg_end]
    
    def initialize_data_for_execution(self) -> bool:
        """
        Initialize data for test execution.
        Called once at the start of execution to load next available data row.
        Returns True if data is ready, False otherwise.
        Respects data_type setting (positive, negative, or mixed).
        """
        self._ensure_data_consumer()
        
        # Check if data.csv exists.
        # Data is generated via DatasetGenerator at runtime (requires a live page),
        # so we do not attempt generation here.
        if not self.data_consumer.data_exists():
            self.log('warning', '📝 data.csv not found yet. Will generate when a placeholder is encountered.')
            return False
        
        # Get next available row based on data_type preference
        row, idx = self._get_next_row_by_type()
        if row:
            self.data_initialized = True
            self.current_dataset_index = idx
            scenario_type = row.get('Scenario Type', 'Unknown').strip("'")
            self.log('info', f'📊 Using data row {idx + 1} ({scenario_type} scenario) for this execution')
            return True
        else:
            self.log('error', '❌ No data available matching the selected data type')
            return False
    
    def _get_next_row_by_type(self):
        """
        Get next available row based on data_type setting.
        Returns (row, index) or (None, -1) if no suitable row found.
        """
        if not self.data_consumer or not self.data_consumer.data_exists():
            return None, -1

        try:
            row, idx = self.data_consumer.get_next_available_row_by_type(self.data_type)
            if row:
                return row, idx
            return None, -1
        except Exception as e:
            self.log('error', f'Error selecting data row: {str(e)}')
            return None, -1
    
    def finalize_data_usage(self):
        """Mark current data row as used after successful execution"""
        if self.data_initialized and self.current_dataset_index >= 0:
            self._ensure_data_consumer()
            self.data_consumer.mark_row_as_used(self.current_dataset_index)
            self.log('info', f'✓ Data row {self.current_dataset_index + 1} marked as used')
    
    def process_step_placeholders(self, step_text: str) -> str:
        """
        Replace placeholders in step with actual data values.
        If data not available, dynamically extract schema from current page.
        Returns processed step text.
        """
        if not self.has_placeholder(step_text):
            return step_text
        
        self._ensure_data_consumer()
        
        # Extract placeholders from the step
        placeholders = PLACEHOLDER_PATTERN.findall(step_text)
        self.log('info', f'🔍 Found placeholders: {placeholders}')
        
        # Try to initialize data from existing CSV
        if not self.data_initialized:
            self.initialize_data_for_execution()
        
        # Check if we have data for all placeholders
        missing_placeholders = []
        for ph in placeholders:
            if self.data_consumer and self.data_consumer.current_row:
                value = self.data_consumer.current_row.get(ph)
                if not value:
                    # Try partial match
                    found = False
                    for key in self.data_consumer.current_row.keys():
                        if ph.lower() in key.lower() or key.lower() in ph.lower():
                            found = True
                            break
                    if not found:
                        missing_placeholders.append(ph)
            else:
                missing_placeholders.append(ph)
        
        # If missing placeholders and dynamic extraction is enabled, crawl the page
        if missing_placeholders and self.use_dynamic_extraction:
            self.log('info', f'📝 Missing data for: {missing_placeholders}. Extracting schema from page...')
            # This will be handled asynchronously in execute_step
            return step_text  # Return original, will be processed in async method
        
        # Replace placeholders
        processed, had_placeholders = self.data_consumer.process_step(step_text)
        
        if had_placeholders and processed != step_text:
            self.log('info', f'📝 Replaced placeholders: {step_text[:50]}... → {processed[:50]}...')
        
        return processed
    
    async def process_step_placeholders_async(self, step_text: str, all_steps: list = None) -> str:
        """
        Async version that can dynamically extract schema if needed.
        If data doesn't exist for placeholders, triggers DatasetGenerator to extract schema and generate data.
        """
        if not self.has_placeholder(step_text):
            return step_text
        
        self._ensure_data_consumer()
        
        # Extract placeholders
        placeholders = PLACEHOLDER_PATTERN.findall(step_text)
        
        # Check if we have columns for these placeholders in the CSV.
        # IMPORTANT: empty values are valid for negative scenarios, so we only treat
        # a placeholder as missing if the column itself is missing.
        missing_placeholders = []
        for ph in placeholders:
            matching_field = self.data_consumer.find_matching_field(ph) if self.data_consumer else None
            if not matching_field:
                missing_placeholders.append(ph)

        # If any placeholder is missing, batch-generate all missing placeholders for the current page segment
        batch_missing_placeholders = missing_placeholders
        if missing_placeholders and all_steps:
            try:
                segment_steps = self._get_current_page_segment_steps(all_steps)
                segment_placeholders = self._extract_placeholders_from_steps(segment_steps)
                batch_missing_placeholders = []
                for ph in segment_placeholders:
                    matching_field = self.data_consumer.find_matching_field(ph) if self.data_consumer else None
                    if not matching_field:
                        batch_missing_placeholders.append(ph)
            except Exception:
                batch_missing_placeholders = missing_placeholders
        
        # If we have missing placeholders (new fields for this page), extract schema + append CSV columns
        if batch_missing_placeholders:
            self.log('info', f'📝 Missing data for placeholders: {batch_missing_placeholders}')
            
            self.log('info', '🔍 Triggering DatasetGenerator to extract schema + append outputs/data.csv...')

            # Preserve the current dataset row (don’t switch rows mid-form)
            preserved_row_index = -1
            if self.current_dataset_index is not None and self.current_dataset_index >= 0:
                preserved_row_index = self.current_dataset_index
            elif self.data_consumer and self.data_consumer.current_row_index >= 0:
                preserved_row_index = self.data_consumer.current_row_index

            # Build a minimal temporary "test steps" text containing only the missing placeholders.
            # DatasetGenerator extracts placeholder labels from patterns like "%Label%".
            # NOTE: DatasetGenerator._read_test_steps flips an internal "in_form" flag but does NOT
            # process the line that triggers the flip. If we only provide a single placeholder line,
            # it will be skipped and 0 labels will be extracted. So we always prepend a header line.
            header_line = self.form_name or ""
            placeholder_lines = [f'Type "%{ph}%" into "{ph}"' for ph in batch_missing_placeholders]
            test_steps_text = "\n".join([header_line] + placeholder_lines)

            # Trigger data generation for current page (append new columns/values)
            success = await self.generate_data_for_current_page(test_steps_text)

            if success:
                # Reload data consumer with newly generated/updated data
                from data_consumer import reset_data_consumer, get_data_consumer
                reset_data_consumer()
                self.data_consumer = get_data_consumer()

                # Restore the same row index if possible
                if preserved_row_index >= 0 and preserved_row_index < len(self.data_consumer.rows):
                    self.data_consumer.current_row_index = preserved_row_index
                    self.data_consumer.current_row = self.data_consumer.rows[preserved_row_index]
                    self.current_dataset_index = preserved_row_index
                    self.data_initialized = True
                    self.log('success', f'✅ Data reloaded; preserved row {preserved_row_index + 1} after appending columns')
                else:
                    self.data_initialized = False
                    self.initialize_data_for_execution()
                    self.log('success', '✅ Data reloaded from updated data.csv')
        
        # Now process placeholders with available data
        result = step_text
        for ph in placeholders:
            value = None
            
            # Try from data consumer
            if self.data_consumer and self.data_consumer.current_row:
                matching_field = self.data_consumer.find_matching_field(ph)
                value = self.data_consumer.current_row.get(matching_field) if matching_field else None
            
            # Replace placeholder with value
            if value is not None:
                cleaned = str(value).strip()
                if cleaned.lower() in ['n/a', 'na']:
                    self.log('warning', f'⚠️ Value is N/A for placeholder: {ph}')
                    continue
                if (cleaned.startswith("'") and cleaned.endswith("'")) or (cleaned.startswith('"') and cleaned.endswith('"')):
                    cleaned = cleaned[1:-1]
                result = result.replace(f'%{ph}%', cleaned)
                self.log('info', f'✓ Replaced %{ph}% → {cleaned}')
            else:
                self.log('warning', f'⚠️ No value found for placeholder: {ph}')
        
        return result
    
    def parse_plain_text_step(self, step_text: str):
        """Parse various test step formats"""
        step_text = step_text.strip()
        
        # Wait command: Wait for X seconds
        wait_match = re.search(r'wait\s+for\s+(\d+)\s+seconds?', step_text, re.IGNORECASE)
        if wait_match:
            seconds = int(wait_match.group(1))
            return {'action': 'wait', 'duration': seconds}
        
        # Click with quotes: Click "Button Text"
        click_match = re.search(r'click\s+"([^"]+)"', step_text, re.IGNORECASE)
        if click_match:
            target = click_match.group(1)
            return {'action': 'click', 'target': target}
        
        # Type into: Type "value" into "Field Name" (allow empty value)
        type_match = re.search(r'type\s+"([^"]*)"\s+into\s+"([^"]+)"', step_text, re.IGNORECASE)
        if type_match:
            value = type_match.group(1)
            target = type_match.group(2)
            return {'action': 'fill', 'target': target, 'value': value}
        
        # Fill with:
        # - Preferred (value-first): Fill "value" with "Field Name"  (works for textarea too)
        # - Backward compatible: fill "Field Name" with "value" OR fill FieldName with value
        fill_match = re.search(r'fill\s+(?:"([^"]+)"|(\w+))\s+with\s+(?:"([^"]+)"|(.+))', step_text, re.IGNORECASE)
        if fill_match:
            first = fill_match.group(1) or fill_match.group(2)
            second = fill_match.group(3) or fill_match.group(4)

            # If both sides were quoted, treat as value-first: Fill "value" with "Field"
            if fill_match.group(1) and fill_match.group(3):
                value = first
                target = second
            else:
                target = first
                value = second

            return {'action': 'fill', 'target': target, 'value': value}
        
        # Select from dropdown: Select "option" from Dropdown "Field Name"
        select_match = re.search(r'select\s+"([^"]+)"\s+from\s+dropdown\s+"([^"]+)"', step_text, re.IGNORECASE)
        if select_match:
            value = select_match.group(1)
            target = select_match.group(2)
            return {'action': 'select', 'target': target, 'value': value}
        
        # Checkbox: Select "Field Name" checkbox OR Check "Field Name"
        checkbox_match = re.search(r'(?:select\s+"([^"]+)"\s+checkbox|check\s+"([^"]+)")', step_text, re.IGNORECASE)
        if checkbox_match:
            target = checkbox_match.group(1) or checkbox_match.group(2)
            return {'action': 'checkbox', 'target': target}
        
        # Verify visible: Verify "Text" is visible OR Verify "Text"
        verify_match = re.search(r'verify\s+"([^"]+)"(?:\s+is\s+visible)?', step_text, re.IGNORECASE)
        if verify_match:
            target = verify_match.group(1)
            return {'action': 'verify', 'target': target}
        
        # Upload file: Upload "file_path" to "Field Name" OR Upload file "file_path"
        upload_match = re.search(r'upload\s+(?:file\s+)?"([^"]+)"(?:\s+to\s+"([^"]+)")?', step_text, re.IGNORECASE)
        if upload_match:
            file_path = upload_match.group(1)
            target = upload_match.group(2) if upload_match.group(2) else 'file upload'
            return {'action': 'upload', 'target': target, 'file_path': file_path}
        
        # Textarea:
        # - Type "text" into textarea "Field Name"
        # - Fill textarea "Field Name" with "text" (target-first)
        # - Fill textarea "text" into "Field Name" (value-first)
        # - Fill textarea "text" with "Field Name" (value-first)
        textarea_type_match = re.search(r'type\s+"([^"]*)"\s+into\s+textarea\s+"([^"]+)"', step_text, re.IGNORECASE)
        if textarea_type_match:
            value = textarea_type_match.group(1)
            target = textarea_type_match.group(2)
            return {'action': 'textarea', 'target': target, 'value': value}

        textarea_fill_value_into_match = re.search(r'fill\s+textarea\s+"([^"]*)"\s+into\s+"([^"]+)"', step_text, re.IGNORECASE)
        if textarea_fill_value_into_match:
            value = textarea_fill_value_into_match.group(1)
            target = textarea_fill_value_into_match.group(2)
            return {'action': 'textarea', 'target': target, 'value': value}

        textarea_fill_value_with_match = re.search(r'fill\s+textarea\s+"([^"]*)"\s+with\s+"([^"]+)"', step_text, re.IGNORECASE)
        if textarea_fill_value_with_match:
            value = textarea_fill_value_with_match.group(1)
            target = textarea_fill_value_with_match.group(2)
            return {'action': 'textarea', 'target': target, 'value': value}

        textarea_fill_match = re.search(r'fill\s+textarea\s+"([^"]+)"\s+with\s+"([^"]+)"', step_text, re.IGNORECASE)
        if textarea_fill_match:
            target = textarea_fill_match.group(1)
            value = textarea_fill_match.group(2)
            return {'action': 'textarea', 'target': target, 'value': value}
        
        # Fall back to parent parser for simple format
        return super().parse_plain_text_step(step_text)
    
    def _is_next_button_click(self, step_text: str) -> bool:
        """Check if this step clicks a Next button (triggers page navigation)"""
        step_lower = step_text.lower()
        if 'click' in step_lower:
            next_patterns = ['next', 'continue', 'proceed', 'forward']
            for pattern in next_patterns:
                if pattern in step_lower:
                    return True
        return False
    
    async def _handle_post_next_click(self):
        """Handle schema extraction after clicking Next button"""
        if self.dynamic_extractor and self.use_dynamic_extraction:
            self.log('info', '📄 Page navigation detected. Will extract schema for new page if needed.')
            self.dynamic_extractor.on_page_navigation()
            # Wait for new page to load
            await asyncio.sleep(2)
    
    async def execute_step(self, step_text: str):
        """Execute a single test step with enhanced actions and dynamic placeholder replacement"""
        
        # Process placeholders BEFORE parsing/executing (using async for dynamic extraction)
        original_step = step_text
        if self.has_placeholder(step_text):
            # Use async version for dynamic schema extraction if needed
            step_text = await self.process_step_placeholders_async(step_text, self.all_test_steps)
            if step_text != original_step:
                self.log('info', f'📝 Original: {original_step[:60]}...')
                self.log('info', f'📝 Processed: {step_text[:60]}...')
        
        self.log('info', f'Executing: {step_text}')
        
        # Check if this is a "Next" button click - trigger page extraction after
        is_next_click = self._is_next_button_click(step_text)
        
        parsed = self.parse_plain_text_step(step_text)
        if not parsed:
            self.log('error', f'Could not parse step: {step_text}')
            return False
        
        action = parsed['action']
        target = parsed.get('target')
        
        # Handle wait action
        if action == 'wait':
            duration = parsed['duration']
            self.log('info', f'Waiting for {duration} seconds...')
            await asyncio.sleep(duration)
            self.log('success', f'Waited {duration} seconds')
            return True
        
        # Handle verify action
        if action == 'verify':
            target = parsed['target']
            
            # For very long text (>100 chars), use partial match
            if len(target) > 100:
                # Try to find element with partial text (first 50 chars)
                partial_target = target[:50]
                self.log('info', f'Verifying with partial text: "{partial_target}..."')
                
                # Try multiple strategies for partial text
                selectors_to_try = [
                    f"text=/{partial_target}/i",
                    f"*:has-text('{partial_target}')",
                    f"p:has-text('{partial_target}')",
                    f"div:has-text('{partial_target}')",
                    f"span:has-text('{partial_target}')",
                ]
                
                for selector in selectors_to_try:
                    try:
                        element = await self.page.wait_for_selector(selector, timeout=3000)
                        if element:
                            is_visible = await element.is_visible()
                            if is_visible:
                                self.log('success', f'✅ Verified text is visible (partial match)')
                                return True
                    except:
                        continue
                
                self.log('error', f'Could not verify text visibility')
                return False
            else:
                # For short text, use normal element finding
                element, selector, was_learned = await self.find_element_smart(target, 'click')
                if element:
                    is_visible = await element.is_visible()
                    if is_visible:
                        self.log('success', f'✅ Verified "{target}" is visible')
                        return True
                    else:
                        self.log('error', f'Element "{target}" found but not visible')
                        return False
                else:
                    self.log('error', f'Could not find element: {target}')
                    return False
        
        # Handle checkbox action
        if action == 'checkbox':
            target = parsed['target']
            element, selector, was_learned = await self.find_element_smart(target, 'click')
            if not element:
                self.log('error', f'Could not find checkbox: {target}')
                return False
            
            try:
                # Check element type
                tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
                element_type = await element.evaluate('el => el.type')
                
                # Standard checkbox
                if tag_name == 'input' and element_type == 'checkbox':
                    is_checked = await element.is_checked()
                    if not is_checked:
                        await element.check()
                        self.log('success', f'✅ Checked: {target}', {'selector': selector})
                    else:
                        self.log('info', f'Already checked: {target}')
                    return True
                
                # Custom checkbox (Salesforce Lightning, list items, etc.)
                else:
                    self.log('info', f'Detected custom checkbox (not <input>), using click method')
                    
                    # Check if already selected (aria-checked, class, etc.)
                    is_selected = await element.evaluate('''el => {
                        // Check various indicators
                        if (el.getAttribute('aria-checked') === 'true') return true;
                        if (el.classList.contains('selected')) return true;
                        if (el.classList.contains('checked')) return true;
                        if (el.classList.contains('slds-is-selected')) return true;
                        
                        // Check for checked icon/input inside
                        const input = el.querySelector('input[type="checkbox"]');
                        if (input && input.checked) return true;
                        
                        return false;
                    }''')
                    
                    if not is_selected:
                        await element.click()
                        self.log('success', f'✅ Checked: {target} (custom checkbox)', {'selector': selector})
                    else:
                        self.log('info', f'Already checked: {target}')
                    
                    return True
                    
            except Exception as e:
                self.log('error', f'Checkbox action failed: {str(e)}')
                return False
        
        # Handle upload action
        if action == 'upload':
            target = parsed['target']
            file_path = parsed.get('file_path', '')
            
            if not file_path:
                self.log('error', 'No file path provided for upload')
                return False
            
            # Convert to absolute path if relative
            file_path_obj = Path(file_path)
            if not file_path_obj.is_absolute():
                file_path_obj = Path.cwd() / file_path
            
            if not file_path_obj.exists():
                self.log('error', f'File not found: {file_path_obj}')
                return False
            
            try:
                # Strategy 1: Try to find and click the upload button first (for UIs like "Upload Files" button)
                upload_button_found = False
                upload_button_selectors = [
                    f"button:has-text('{target}')",
                    f"a:has-text('{target}')",
                    "button:has-text('Upload Files')",
                    "button:has-text('Upload')",
                    "a:has-text('Upload Files')",
                    "a:has-text('Upload')",
                    "[role='button']:has-text('Upload')",
                ]
                
                for btn_selector in upload_button_selectors:
                    try:
                        button = await self.page.wait_for_selector(btn_selector, timeout=2000)
                        if button:
                            # Check if button is visible and clickable
                            is_visible = await button.is_visible()
                            if is_visible:
                                self.log('info', f'Found upload button: {btn_selector}')
                                upload_button_found = True
                                
                                # Set up file chooser listener BEFORE clicking the button
                                async with self.page.expect_file_chooser() as fc_info:
                                    await button.click()
                                    file_chooser = await fc_info.value
                                    await file_chooser.set_files(str(file_path_obj))
                                
                                self.log('success', f'Uploaded file via button: {file_path_obj.name}', {'selector': btn_selector, 'file': str(file_path_obj)})
                                return True
                    except Exception as e:
                        continue
                
                # Strategy 2: If no button found, try to find file input directly
                if not upload_button_found:
                    self.log('info', 'No upload button found, trying direct file input')
                    
                    element, selector, was_learned = await self.find_element_smart(target, 'upload')
                    if not element:
                        # Try generic file input selector
                        try:
                            element = await self.page.wait_for_selector('input[type="file"]', timeout=5000)
                            selector = 'input[type="file"]'
                            self.log('info', f'Found file input using generic selector')
                        except:
                            self.log('error', f'Could not find file input element')
                            return False
                    
                    # Use set_input_files to upload the file
                    await element.set_input_files(str(file_path_obj))
                    self.log('success', f'Uploaded file: {file_path_obj.name}', {'selector': selector, 'file': str(file_path_obj)})
                    return True
                    
            except Exception as e:
                self.log('error', f'File upload failed: {str(e)}')
                return False
        
        # Handle textarea action
        if action == 'textarea':
            target = parsed['target']
            value = parsed.get('value', '')
            
            element, selector, was_learned = await self.find_element_smart(target, 'textarea')
            if not element:
                self.log('error', f'Could not find textarea: {target}')
                return False
            
            try:
                # Verify it's a textarea element
                tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
                
                if tag_name != 'textarea':
                    self.log('error', f'Element is not a textarea (found: {tag_name}); refusing to fill to avoid typing into the wrong field')
                    return False
                
                # Check if textarea is readonly or disabled
                is_readonly = await element.evaluate('el => el.readOnly || el.getAttribute("aria-readonly") === "true"')
                is_disabled = await element.evaluate('el => el.disabled')
                
                if is_readonly:
                    self.log('warning', f'Textarea is readonly, attempting to remove readonly attribute')
                    await element.evaluate('el => { el.readOnly = false; el.setAttribute("aria-readonly", "false"); }')
                
                if is_disabled:
                    self.log('warning', f'Textarea is disabled, attempting to enable it')
                    await element.evaluate('el => el.disabled = false')
                
                # Multiple strategies to fill the textarea
                try:
                    # Strategy 1: Standard Playwright fill
                    await element.click()  # Focus the field
                    await asyncio.sleep(0.3)  # Wait for focus
                    await element.fill('')  # Clear existing content
                    await element.fill(value)  # Fill with new value
                    self.log('success', f'Filled textarea "{target}" with: {value[:50]}...', {'selector': selector})
                    return True
                except Exception as e1:
                    self.log('warning', f'Standard fill failed: {str(e1)}, trying alternative method')
                    
                    # Strategy 2: Type character by character
                    try:
                        await element.click()
                        await asyncio.sleep(0.3)
                        # Clear using keyboard
                        await self.page.keyboard.press('Control+A')
                        await self.page.keyboard.press('Backspace')
                        await asyncio.sleep(0.2)
                        # Type the value
                        await element.type(value, delay=10)
                        self.log('success', f'Filled textarea "{target}" using type method', {'selector': selector})
                        return True
                    except Exception as e2:
                        self.log('warning', f'Type method failed: {str(e2)}, trying JavaScript injection')
                        
                        # Strategy 3: Direct JavaScript value setting with comprehensive event triggering
                        try:
                            # More comprehensive event dispatching for LWC components
                            await element.evaluate(f'''el => {{
                                el.value = {json.dumps(value)};
                                el.focus();
                                
                                // Dispatch multiple events to ensure LWC reactivity
                                el.dispatchEvent(new Event("input", {{ bubbles: true, composed: true }}));
                                el.dispatchEvent(new Event("change", {{ bubbles: true, composed: true }}));
                                el.dispatchEvent(new Event("blur", {{ bubbles: true, composed: true }}));
                                
                                // Trigger any custom LWC events
                                el.dispatchEvent(new CustomEvent("valuechange", {{ 
                                    detail: {{ value: el.value }},
                                    bubbles: true,
                                    composed: true
                                }}));
                            }}''')
                            self.log('success', f'Filled textarea "{target}" using JavaScript with LWC events', {'selector': selector})
                            return True
                        except Exception as e3:
                            self.log('error', f'All textarea fill strategies failed: {str(e3)}')
                            return False
                            
            except Exception as e:
                self.log('error', f'Textarea fill failed: {str(e)}')
                return False
        
        # Handle select (dropdown) action
        if action == 'select':
            target = parsed['target']
            value = parsed.get('value', '')
            
            element, selector, was_learned = await self.find_element_smart(target, 'select')
            if not element:
                self.log('error', f'Could not find dropdown: {target}')
                return False
            
            try:
                # Check if it's a standard <select> element
                tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
                
                if tag_name == 'select':
                    # Standard HTML select
                    try:
                        await element.select_option(label=value)
                        self.log('success', f'Selected "{value}" in: {target}', {'selector': selector})
                    except:
                        await element.select_option(value=value)
                        self.log('success', f'Selected "{value}" in: {target}', {'selector': selector})
                else:
                    # Salesforce Lightning combobox or custom dropdown
                    self.log('info', f'Detected custom dropdown (not <select>), using click method')
                    
                    opened = False
                    try:
                        await element.click()
                        opened = True
                    except Exception:
                        try:
                            await element.click(force=True)
                            opened = True
                        except Exception:
                            try:
                                await element.evaluate('el => el.click()')
                                opened = True
                            except Exception:
                                opened = False

                    if not opened:
                        self.log('error', f'Could not open dropdown: {target}')
                        return False

                    await asyncio.sleep(0.5)
                    
                    # Try to find and click the option
                    option_found = False

                    # OmniStudio combobox: scope options to the listbox controlled by this combobox
                    listbox_id = None
                    try:
                        listbox_id = await element.evaluate('''el => {
                            try {
                                const isCb = el.matches && el.matches('input[role="combobox"]');
                                const cbInput = isCb
                                    ? el
                                    : (el.querySelector && el.querySelector('input[role="combobox"]'))
                                        || (el.closest && el.closest('.slds-combobox') && el.closest('.slds-combobox').querySelector('input[role="combobox"]'))
                                        || null;
                                const id = (cbInput && cbInput.getAttribute) ? (cbInput.getAttribute('aria-controls') || '') : '';
                                return id || (el.getAttribute ? (el.getAttribute('aria-controls') || '') : '');
                            } catch (e) {
                                return '';
                            }
                        }''')
                        if listbox_id:
                            listbox_id = str(listbox_id).strip()
                            if not listbox_id:
                                listbox_id = None
                    except Exception:
                        listbox_id = None

                    if listbox_id:
                        try:
                            await self.page.wait_for_selector(f"#{listbox_id}", timeout=2000)
                            listbox = self.page.locator(f"#{listbox_id}")

                            # Prefer exact data-label match (matches OmniStudio markup)
                            opt = listbox.locator(f"[role='option'][data-label=\"{value}\"]").first
                            if await opt.is_visible(timeout=800):
                                await opt.click()
                                self.log('success', f'Selected "{value}" in: {target} (scoped listbox)', {'selector': selector})
                                option_found = True
                            else:
                                opt2 = listbox.locator("[role='option']").filter(has_text=str(value)).first
                                if await opt2.is_visible(timeout=800):
                                    await opt2.click()
                                    self.log('success', f'Selected "{value}" in: {target} (scoped listbox)', {'selector': selector})
                                    option_found = True
                        except Exception:
                            option_found = False

                    # Fallback: global option selectors (kept for non-OmniStudio custom dropdowns)
                    option_selectors = [
                        # LWC combobox options (most specific first)
                        f"[role='listbox'] [role='option']:has-text('{value}')",
                        f"lightning-base-combobox-item:has-text('{value}')",
                        f"[role='option']:has-text('{value}')",
                        # Data attributes
                        f"[data-value='{value}']",
                        f"[data-label='{value}']",
                        # Text-based selectors (more specific to less specific)
                        f"span.slds-listbox__option-text:has-text('{value}')",
                        f"span:has-text('{value}')",
                        f"div.slds-listbox__option:has-text('{value}')",
                        f"div:has-text('{value}')",
                        f"text='{value}'",
                    ]
                    
                    if not option_found:
                        for opt_selector in option_selectors:
                            try:
                                option = await self.page.wait_for_selector(opt_selector, timeout=2000)
                                if option:
                                    await option.click()
                                    self.log('success', f'Selected "{value}" in: {target} (custom dropdown)')
                                    option_found = True
                                    break
                            except:
                                continue
                    
                    if not option_found:
                        try:
                            await element.click()
                        except Exception:
                            try:
                                await element.click(force=True)
                            except Exception:
                                pass

                        try:
                            await asyncio.sleep(0.2)
                            await self.page.keyboard.press('Control+A')
                            await self.page.keyboard.press('Backspace')
                        except Exception:
                            pass

                        try:
                            try:
                                await element.focus()
                            except Exception:
                                pass
                            await self.page.keyboard.type(str(value))
                            await self.page.keyboard.press('Enter')
                            self.log('success', f'Selected "{value}" in: {target} (keyboard fallback)', {'selector': selector})
                        except Exception:
                            self.log('error', f'Could not find option "{value}" in dropdown')
                            return False
                
                await asyncio.sleep(0.5)
                return True
            except Exception as e:
                self.log('error', f'Select action failed: {str(e)}')
                return False
        
        # Handle standard click and fill actions
        target = parsed.get('target')
        if not target:
            self.log('error', f'No target found in step: {step_text}')
            return False
        
        # Find element
        element, selector, was_learned = await self.find_element_smart(target, action)
        
        if not element:
            self.log('error', f'Could not find element: {target}')
            return False
        
        # Perform action
        try:
            if action == 'click':
                # Try multiple click strategies for better reliability
                click_successful = False
                last_error = None
                
                # First, scroll element into view and wait for it to be stable
                try:
                    await element.scroll_into_view_if_needed()
                    await asyncio.sleep(0.3)  # Wait for scroll to complete
                except:
                    pass
                
                # Strategy 1: Standard click
                try:
                    await element.click()
                    self.log('success', f'Clicked: {target}', {'selector': selector})
                    click_successful = True
                except Exception as e1:
                    last_error = e1
                    self.log('warning', f'Standard click failed: {str(e1)}, trying JavaScript click')
                    
                    # Strategy 2: JavaScript click
                    try:
                        await element.evaluate('el => el.click()')
                        self.log('success', f'Clicked: {target} (using JavaScript)', {'selector': selector})
                        click_successful = True
                    except Exception as e2:
                        last_error = e2
                        self.log('warning', f'JavaScript click failed: {str(e2)}, trying force click')
                        
                        # Strategy 3: Force click (ignore actionability checks)
                        try:
                            await element.click(force=True)
                            self.log('success', f'Clicked: {target} (using force click)', {'selector': selector})
                            click_successful = True
                        except Exception as e3:
                            last_error = e3
                            self.log('warning', f'Force click failed: {str(e3)}, trying dispatch click event')
                            
                            # Strategy 4: Dispatch click event
                            try:
                                await element.evaluate('''el => {
                                    el.dispatchEvent(new MouseEvent('click', {
                                        view: window,
                                        bubbles: true,
                                        cancelable: true
                                    }));
                                }''')
                                self.log('success', f'Clicked: {target} (using dispatch event)', {'selector': selector})
                                click_successful = True
                            except Exception as e4:
                                last_error = e4
                                self.log('warning', f'Dispatch event failed: {str(e4)}, trying href navigation')
                                
                                # Strategy 5: For links, navigate directly to href
                                try:
                                    href = await element.evaluate('el => el.href || el.getAttribute("href")')
                                    if href and href.startswith('http'):
                                        await self.page.goto(href)
                                        self.log('success', f'Clicked: {target} (using href navigation)', {'selector': selector})
                                        click_successful = True
                                    else:
                                        # Strategy 6: Focus and Enter key
                                        await element.focus()
                                        await self.page.keyboard.press('Enter')
                                        self.log('success', f'Clicked: {target} (using focus + Enter)', {'selector': selector})
                                        click_successful = True
                                except Exception as e5:
                                    last_error = e5
                                    self.log('error', f'All click strategies failed for: {target}')
                
                if not click_successful and last_error:
                    raise last_error
                
            elif action == 'fill':
                value = parsed.get('value', '')
                
                # Check if the element is a textarea and use enhanced strategies
                try:
                    tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
                    
                    if tag_name == 'textarea':
                        self.log('info', f'Detected textarea element, using enhanced fill strategies')
                        
                        # Check if textarea is readonly or disabled
                        is_readonly = await element.evaluate('el => el.readOnly || el.getAttribute("aria-readonly") === "true"')
                        is_disabled = await element.evaluate('el => el.disabled')
                        
                        if is_readonly:
                            self.log('warning', f'Textarea is readonly, attempting to remove readonly attribute')
                            await element.evaluate('el => { el.readOnly = false; el.setAttribute("aria-readonly", "false"); }')
                        
                        if is_disabled:
                            self.log('warning', f'Textarea is disabled, attempting to enable it')
                            await element.evaluate('el => el.disabled = false')
                        
                        # Try enhanced textarea strategies
                        try:
                            await element.click()
                            await asyncio.sleep(0.3)
                            await element.fill('')
                            await element.fill(value)
                            self.log('success', f'Filled textarea {target} with: {value}', {'selector': selector})
                        except Exception as e1:
                            self.log('warning', f'Standard fill failed: {str(e1)}, trying type method')
                            try:
                                await element.click()
                                await asyncio.sleep(0.3)
                                await self.page.keyboard.press('Control+A')
                                await self.page.keyboard.press('Backspace')
                                await asyncio.sleep(0.2)
                                await element.type(value, delay=10)
                                self.log('success', f'Filled textarea {target} using type method', {'selector': selector})
                            except Exception as e2:
                                self.log('warning', f'Type method failed: {str(e2)}, trying JavaScript')
                                await element.evaluate(f'''el => {{
                                    el.value = {json.dumps(value)};
                                    el.focus();
                                    el.dispatchEvent(new Event("input", {{ bubbles: true, composed: true }}));
                                    el.dispatchEvent(new Event("change", {{ bubbles: true, composed: true }}));
                                    el.dispatchEvent(new Event("blur", {{ bubbles: true, composed: true }}));
                                    el.dispatchEvent(new CustomEvent("valuechange", {{ 
                                        detail: {{ value: el.value }},
                                        bubbles: true,
                                        composed: true
                                    }}));
                                }}''')
                                self.log('success', f'Filled textarea {target} using JavaScript', {'selector': selector})
                    else:
                        # Standard input field
                        await element.click()
                        await element.fill('')
                        await element.fill(value)
                        self.log('success', f'Filled {target} with: {value}', {'selector': selector})
                except Exception as tag_check_error:
                    # Fallback to standard fill if tag check fails
                    await element.click()
                    await element.fill('')
                    await element.fill(value)
                    self.log('success', f'Filled {target} with: {value}', {'selector': selector})
            
            await asyncio.sleep(0.3)  # Small delay between actions
            
            # Handle post-Next-click schema extraction
            if is_next_click:
                await self._handle_post_next_click()
            
            return True
            
        except Exception as e:
            self.log('error', f'Action failed: {str(e)}')
            try:
                file_safe_target = (target or 'action_failure').replace(' ', '_')[:30]
                screenshot_path = f"failure_action_{file_safe_target}.png"
                if 'element' in locals() and element is not None:
                    await element.screenshot(path=screenshot_path)
                elif self.page:
                    await self.page.screenshot(path=screenshot_path)
                self.last_failure_screenshot = screenshot_path
                self.log('info', f'📸 Failure screenshot saved: {screenshot_path}')
            except Exception:
                pass
            return False
    
    def generate_selectors(self, target: str, action: str = 'click'):
        """Generate selectors with enhanced strategies for Salesforce"""
        selectors = super().generate_selectors(target, action)
        
        # Add Salesforce-specific selectors at the beginning
        target_lower = target.lower()
        target_clean = target_lower.replace(' ', '')
        
        salesforce_selectors = []
        
        # Lightning components
        if action == 'click':
            # Escape special regex characters for text matching
            target_escaped = target.replace(':', '\\:')
            
            # Special handling for form actions: try Edit/Start FIRST!
            # For "Form X: Name" patterns, prioritize "Start" and "Edit" links
            if 'form' in target_lower and ':' in target:
                form_name = target.split(':')[0].strip()  # e.g., "Form 1"
                full_form_name = target.split(':')[1].strip() if ':' in target else ''  # e.g., "Demographics"
                form_number = ''.join(filter(str.isdigit, form_name))  # e.g., "1"
                
                # PRIORITY: Find Edit/Start button in the SAME ROW as the form name
                # Structure: Each form row is a div/container with form name + view + Edit/Start
                salesforce_selectors.extend([
                    # STRATEGY 1: Find row containing form name, then get Edit/Start within same row
                    # Using ancestor to find common parent container, then descendant to find action
                    f"xpath=//*[contains(text(), '{form_name}') and contains(text(), '{full_form_name}')]/ancestor::*[.//a[contains(., 'Edit') or contains(., 'Start')]][1]//a[contains(., 'Edit')]",
                    f"xpath=//*[contains(text(), '{form_name}') and contains(text(), '{full_form_name}')]/ancestor::*[.//a[contains(., 'Edit') or contains(., 'Start')]][1]//a[contains(., 'Start')]",
                    
                    # STRATEGY 2: Find div/span containing form text, go to parent row, find Edit/Start
                    f"xpath=//span[contains(., '{form_name}') and contains(., '{full_form_name}')]/ancestor::div[contains(@class, 'row') or contains(@class, 'item') or contains(@class, 'form')][1]//a[normalize-space()='Edit']",
                    f"xpath=//span[contains(., '{form_name}') and contains(., '{full_form_name}')]/ancestor::div[contains(@class, 'row') or contains(@class, 'item') or contains(@class, 'form')][1]//a[normalize-space()='Start']",
                    
                    # STRATEGY 3: Find by text content then navigate to sibling/following Edit link
                    f"xpath=//*[contains(normalize-space(.), '{target}') and not(self::script)]/following-sibling::*//a[normalize-space()='Edit'][1]",
                    f"xpath=//*[contains(normalize-space(.), '{target}') and not(self::script)]/following-sibling::*//a[normalize-space()='Start'][1]",
                    
                    # STRATEGY 4: Use Playwright's has-text with parent container
                    f"div:has-text('{form_name}'):has-text('{full_form_name}') >> a:has-text('Edit')",
                    f"div:has-text('{form_name}'):has-text('{full_form_name}') >> a:has-text('Start')",
                    
                    # STRATEGY 5: Find all Edit/Start links and filter by row content (XPath position)
                    f"xpath=(//a[normalize-space()='Edit'])[{form_number}]",
                    f"xpath=(//a[normalize-space()='Start'])[{form_number}]",
                    
                    # STRATEGY 6: Lightning component specific - look for lightning layout items
                    f"xpath=//lightning-layout-item[contains(., '{form_name}') and contains(., '{full_form_name}')]//a[contains(., 'Edit')]",
                    f"xpath=//lightning-layout-item[contains(., '{form_name}') and contains(., '{full_form_name}')]//a[contains(., 'Start')]",
                    
                    # STRATEGY 7: Find the specific span with Edit/Start text after form name span
                    f"xpath=//span[contains(text(), '{full_form_name}')]/following::a[.//span[text()='Edit']][1]",
                    f"xpath=//span[contains(text(), '{full_form_name}')]/following::a[.//span[text()='Start']][1]",
                    
                    # STRATEGY 8: Table row based (if forms are in a table)
                    f"tr:has-text('{form_name}'):has-text('{full_form_name}') >> a:has-text('Edit')",
                    f"tr:has-text('{form_name}'):has-text('{full_form_name}') >> a:has-text('Start')",
                    
                    # STRATEGY 9: Salesforce specific data attributes
                    f"xpath=//*[@data-label='{target}' or contains(@data-label, '{full_form_name}')]/ancestor::*[1]//a[contains(., 'Edit')]",
                    f"xpath=//*[@data-label='{target}' or contains(@data-label, '{full_form_name}')]/ancestor::*[1]//a[contains(., 'Start')]",
                ])
            
            # Then add general selectors (LOWER PRIORITY)
            salesforce_selectors.extend([
                # Button and link selectors (prioritize clickable elements)
                f"button:has-text('{target}')",
                f"a:has-text('{target}')",
                f"button:has-text('{target.split(':')[0]}')",  # Match before colon
                # Lightning components
                f"lightning-button:has-text('{target}')",
                f"lightning-button[title='{target}']",
                # XPath with normalize-space (HIGHEST PRIORITY - most reliable)
                f"xpath=//span[normalize-space(.)='{target}']",
                f"xpath=//div[normalize-space(.)='{target}']",
                f"xpath=//a[normalize-space(.)='{target}']",
                f"xpath=//button[normalize-space(.)='{target}']",
                # XPath with clickable parent strategies (for nested text elements)
                f"xpath=//div[normalize-space(.)='{target}']/ancestor::a[1]",
                f"xpath=//div[normalize-space(.)='{target}']/ancestor::button[1]",
                f"xpath=//span[normalize-space(.)='{target}']/ancestor::a[1]",
                f"xpath=//span[normalize-space(.)='{target}']/ancestor::button[1]",
                # XPath with contains for partial matches
                f"xpath=//div[contains(normalize-space(.), '{target}') and string-length(normalize-space(.)) = {len(target)}]",
                f"xpath=//*[normalize-space(.)='{target}' and not(self::script) and not(self::style)]",
                # Visible text in specific Salesforce elements
                f"span.slds-page-header__title:has-text('{target}')",
                f"span.slds-truncate:has-text('{target}')",
                f"h1:has-text('{target}')",
                f"h2:has-text('{target}')",
                # List items and menu items (for dropdowns/lists)
                f"li:has-text('{target}')",
                f"[role='option']:has-text('{target}')",
                f"[role='menuitem']:has-text('{target}')",
                f"[role='listitem']:has-text('{target}')",
                # Salesforce list view items
                f"a[title='{target}']",
                f"span[title='{target}']",
                # Text matches (visible text priority)
                f"text='{target}'",
                f"text=/{target}/i",
                f"span:has-text('{target}')",
                f"div:has-text('{target}')",
                # Attribute selectors (LOWER PRIORITY - after visible text)
                f"[title='{target}']",
                f"[aria-label='{target}']",
                f"[data-label='{target}']",
                # Generic fallback (LOWEST PRIORITY)
                f"*:has-text('{target}')",
            ])
        
        if action == 'fill':
            salesforce_selectors.extend([
                # Input fields
                f"input[placeholder='{target}']",
                f"lightning-input[data-label='{target}'] >> input",
                # XPath with normalize-space for input (HIGHEST PRIORITY - most reliable)
                f"xpath=//*[normalize-space(text())='{target}']//following::input[1]",
                f"xpath=//*[contains(normalize-space(text()), '{target}')]//following::input[1]",
                f"label:has-text('{target}') >> xpath=following::input[1]",
                # Textarea fields (also check for textareas in fill action)
                f"textarea.slds-textarea[placeholder='{target}']",
                f"textarea[placeholder='{target}']",
                f"textarea[aria-label='{target}']",
                f"lightning-textarea[data-label='{target}'] >> textarea",
                # XPath with normalize-space for textarea (HIGHEST PRIORITY - most reliable)
                f"xpath=//*[normalize-space(text())='{target}']//following::textarea[1]",
                f"xpath=//*[contains(normalize-space(text()), '{target}')]//following::textarea[1]",
                f"*:has-text('{target}') >> xpath=following-sibling::div >> textarea",
                f"*:has-text('{target}') >> xpath=following::textarea.slds-textarea[1]",
                f"*:has-text('{target}') >> xpath=following::textarea[1]",
                f"div.slds-form-element:has-text('{target}') >> textarea",
                f"label:has-text('{target}') >> xpath=following::textarea[1]",
            ])
        
        if action == 'textarea':
            salesforce_selectors.extend([
                # XPath with normalize-space (HIGHEST PRIORITY - most reliable for Salesforce)
                f"xpath=//*[normalize-space(text())='{target}']//following::textarea[1]",
                f"xpath=//*[normalize-space(text())='{target}']//following::textarea[@class='slds-textarea'][1]",
                f"xpath=//*[contains(normalize-space(text()), '{target}')]//following::textarea[1]",
                # LWC/SLDS textarea selectors
                f"textarea.slds-textarea[aria-label='{target}']",
                f"textarea.slds-textarea[placeholder='{target}']",
                f"lightning-textarea[data-label='{target}'] >> textarea",
                f"lightning-textarea >> textarea[aria-label='{target}']",
                # Generic textarea selectors
                f"textarea[placeholder='{target}']",
                f"textarea[aria-label='{target}']",
                f"textarea[name*='{target_clean}']",
                f"textarea[id*='{target_clean}']",
                # Label-based selectors (with partial text matching)
                f"label:has-text('{target}') >> xpath=following-sibling::textarea",
                f"label:has-text('{target}') >> xpath=following::textarea[1]",
                f"*:has-text('{target}') >> xpath=following-sibling::div >> textarea",
                f"*:has-text('{target}') >> xpath=following-sibling::div >> textarea.slds-textarea",
                f"*:has-text('{target}') >> xpath=following::textarea[1]",
                f"*:has-text('{target}') >> xpath=following::textarea.slds-textarea[1]",
                # Partial text matching (for long labels)
                f"text=/{target[:30]}/i >> xpath=following::textarea[1]" if len(target) > 30 else None,
                # Parent div with slds-form-element__control
                f"div.slds-form-element:has-text('{target}') >> textarea",
                f"div.slds-form-element:has-text('{target}') >> textarea.slds-textarea",
                # Fallback: any SLDS textarea
                f"textarea.slds-textarea",
            ])
            # Remove None values
            salesforce_selectors = [s for s in salesforce_selectors if s is not None]
        
        if action == 'upload':
            salesforce_selectors.extend([
                f"input[type='file'][aria-label='{target}']",
                f"input[type='file'][name*='{target_clean}']",
                f"input[type='file'][id*='{target_clean}']",
                f"label:has-text('{target}') >> xpath=following-sibling::input[@type='file']",
                f"*:has-text('{target}') >> xpath=following::input[@type='file'][1]",
            ])
        
        if action == 'select':
            salesforce_selectors.extend([
                # Standard select
                f"select[aria-label='{target}']",
                f"label:has-text('{target}') >> xpath=following::select[1]",
                # Lightning combobox (custom dropdown)
                f"lightning-combobox[data-label='{target}']",
                f"text='{target}' >> xpath=following::lightning-combobox[1]",
                f"text='{target}' >> xpath=ancestor::*[1] >> lightning-combobox",
                f"text='{target}' >> xpath=ancestor::*[2] >> lightning-combobox",
                # Input-based combobox (LWC combobox) - HIGHER PRIORITY
                f"text='{target}' >> xpath=following::input[@role='combobox'][1]",
                f"text='{target}' >> xpath=ancestor::*[1] >> input[@role='combobox']",
                f"text='{target}' >> xpath=ancestor::*[2] >> input[@role='combobox']",
                f"input[role='combobox'][aria-label*='{target}']",
                # Div-based combobox dropdowns
                f"text='{target}' >> xpath=following::div[@role='combobox'][1]",
                f"text='{target}' >> xpath=ancestor::*[1] >> div[@role='combobox']",
                # Button-based dropdowns (LOWER PRIORITY - only if not combobox)
                f"text='{target}' >> xpath=following::button[1]",
                f"text='{target}' >> xpath=ancestor::*[1] >> button",
                # Generic - find the label text
                f"text='{target}'",
            ])
        
        # Combine: Salesforce-specific first, then generic
        return salesforce_selectors + selectors


# Example usage
async def test_enhanced_format():
    """Test with original format"""
    executor = EnhancedTestExecutor()
    
    test_steps = [
        'Wait for 2 seconds',
        'Type "sarokiasamy2@dmigs.com.dcp.dcpuat" into "Username"',
        'Type "Grantee@123" into "Password"',
        'Click "Log in"',
        'Wait for 2 seconds',
        'Click "I Disagree"',
        'Click "Next"',
    ]
    
    result = await executor.execute_test(
        url="https://hrsa-dcpaas--dcpuat.sandbox.my.site.com/pars/s/login/",
        steps=test_steps,
        headless=False
    )
    
    print(f"\nTest Result: {result['success']}")
    print(f"Steps: {result['successful_steps']}/{result['total_steps']}")


if __name__ == "__main__":
    asyncio.run(test_enhanced_format())
