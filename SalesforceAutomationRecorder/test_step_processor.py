"""
Test Step Processor
Processes test steps with placeholders (%field_name%) and replaces them with actual data from data.csv

When a placeholder is encountered and data.csv doesn't exist:
1. Executes navigation steps from test file using Playwright
2. When placeholder is reached, extracts schema from current form page
3. Generates test data based on schema
4. Replaces placeholders with actual data

Usage:
    python test_step_processor.py [--dataset N] [--all] [--run] [--generate-only]
    
    --dataset N      : Use dataset row N (1-indexed)
    --all            : Generate test files for all datasets
    --run            : Execute test steps in browser (navigate + extract if needed)
    --generate-only  : Only generate processed test file, don't execute
"""

import csv
import re
import os
import sys
import asyncio
from pathlib import Path

# Placeholder pattern: %field_name%
PLACEHOLDER_PATTERN = re.compile(r'%([^%]+)%')


class TestStepProcessor:
    """
    Process test steps, execute navigation, and extract schema when needed
    """
    
    def __init__(self, test_steps_file: str = "Sample Test Steps.txt",
                 data_file: str = "data.csv",
                 schema_file: str = "outputs/fields.json"):
        self.test_steps_file = test_steps_file
        self.data_file = data_file
        self.schema_file = schema_file
        self.page = None
        self.browser = None
        self.playwright = None
        
    def has_placeholder(self, line: str) -> bool:
        """Check if line contains a placeholder"""
        return bool(PLACEHOLDER_PATTERN.search(line))
    
    def get_placeholders(self, line: str) -> list:
        """Extract all placeholders from a line"""
        return PLACEHOLDER_PATTERN.findall(line)
    
    def data_exists(self) -> bool:
        """Check if data.csv exists"""
        return Path(self.data_file).exists()
    
    def schema_exists(self) -> bool:
        """Check if schema file exists"""
        return Path(self.schema_file).exists()
    
    def load_test_steps(self) -> list:
        """Load test steps from file"""
        with open(self.test_steps_file, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    
    def parse_step(self, step: str) -> dict:
        """Parse a test step into action components"""
        step = step.strip()
        
        # Type "value" into "field"
        match = re.match(r'Type\s+"([^"]+)"\s+into\s+"([^"]+)"', step, re.IGNORECASE)
        if match:
            return {'action': 'type', 'value': match.group(1), 'field': match.group(2)}
        
        # Fill textarea "field" with "value"
        match = re.match(r'Fill\s+textarea\s+"([^"]+)"\s+with\s+"([^"]+)"', step, re.IGNORECASE)
        if match:
            return {'action': 'textarea', 'field': match.group(1), 'value': match.group(2)}
        
        # Select "value" from Dropdown "field"
        match = re.match(r'[Ss]elect\s+"([^"]+)"\s+from\s+[Dd]ropdown\s+"([^"]+)"', step, re.IGNORECASE)
        if match:
            return {'action': 'select', 'value': match.group(1), 'field': match.group(2)}
        
        # Click "element"
        match = re.match(r'Click\s+"([^"]+)"', step, re.IGNORECASE)
        if match:
            return {'action': 'click', 'target': match.group(1)}
        
        # Wait for N seconds
        match = re.match(r'Wait\s+for\s+(\d+)\s+[Ss]econds?', step, re.IGNORECASE)
        if match:
            return {'action': 'wait', 'duration': int(match.group(1))}
        
        # Verify "text"
        match = re.match(r'Verify\s+"([^"]+)"', step, re.IGNORECASE)
        if match:
            return {'action': 'verify', 'text': match.group(1)}
        
        # Check "checkbox"
        match = re.match(r'Check\s+"([^"]+)"', step, re.IGNORECASE)
        if match:
            return {'action': 'check', 'field': match.group(1)}
        
        # Upload file "path" to "field"
        match = re.match(r'Upload\s+file\s+"([^"]+)"\s+to\s+"([^"]+)"', step, re.IGNORECASE)
        if match:
            return {'action': 'upload', 'file': match.group(1), 'field': match.group(2)}
        
        return {'action': 'unknown', 'step': step}
    
    def get_executor(self, use_ai: bool = False):
        """
        Get the appropriate executor from ui_real_test_server.py infrastructure.
        Uses EnhancedTestExecutor with learned selectors (shared with UI server).
        """
        from enhanced_test_executor import EnhancedTestExecutor
        
        executor = None
        if use_ai:
            try:
                from gemini_enhanced_executor import GeminiEnhancedExecutor
                from gemini_selector_ai import get_gemini_ai
                gemini_ai = get_gemini_ai()
                if gemini_ai.is_available():
                    executor = GeminiEnhancedExecutor()
                    print("🤖 Using Gemini AI Enhanced Executor (with learned selectors)")
            except Exception as e:
                print(f"⚠️ Gemini AI not available: {e}")
        
        if executor is None:
            executor = EnhancedTestExecutor()
            print("📚 Using Enhanced Executor (with learned selectors)")
        
        return executor
    
    async def execute_navigation_steps_with_executor(self, executor, url: str) -> int:
        """
        Execute test steps until first placeholder using EnhancedTestExecutor.
        Uses learned selectors from test_learning.json (shared with UI server).
        """
        steps = self.load_test_steps()
        
        print("\n=== Executing Navigation Steps (with learned selectors) ===\n")
        print(f"📊 Loaded {len(executor.learned_selectors)} learned selectors")
        
        await executor.start_browser(url, headless=False, browser="edge")
        
        for i, step in enumerate(steps):
            if self.has_placeholder(step):
                print(f"\n>>> Placeholder found at step {i + 1}: {step[:60]}...")
                return i
            
            print(f"Step {i + 1}: {step[:60]}...")
            success = await executor.execute_step(step)
            
            if success:
                # Check if a new selector was learned
                parsed = executor.parse_plain_text_step(step)
                if parsed and 'target' in parsed:
                    target_key = parsed['target'].lower().replace(' ', '_')
                    if target_key in executor.learned_selectors:
                        learned = executor.learned_selectors[target_key]
                        if learned['success_count'] == 1:
                            print(f"    🧠 Learned: {learned['selector'][:50]}...")
            
            await asyncio.sleep(0.5)
        
        return len(steps)
    
    def generate_data(self, num_rows: int = 100):
        """Generate test data from schema"""
        from DataGenerator import DataGenerator
        
        print("\n=== Generating Test Data ===\n")
        
        generator = DataGenerator(self.schema_file)
        generator.generate_all_data(num_rows=num_rows, output_file=self.data_file)
        print(f"✓ Generated {num_rows} rows to {self.data_file}")
    
    async def run_with_extraction(self, num_rows: int = 100, use_ai: bool = False):
        """
        Run test steps using EnhancedTestExecutor (with learned selectors),
        extract schema when placeholder is found, generate data.
        """
        BASE_URL = "https://hrsa-dcpaas--dcpuat.sandbox.my.site.com/pars/s/"
        executor = self.get_executor(use_ai)
        
        try:
            placeholder_index = await self.execute_navigation_steps_with_executor(executor, BASE_URL)
            
            if placeholder_index < len(self.load_test_steps()):
                if not self.data_exists():
                    print("\n>>> Data not found. Extracting schema and generating data...")
                    await asyncio.sleep(2)
                    
                    # Close executor browser, use SchemaExtractor for extraction
                    await executor.stop_browser()
                    self.extract_schema_sync()
                    
                    if self.schema_exists():
                        self.generate_data(num_rows)
                    else:
                        print("✗ Schema extraction failed")
                        return
                
                print("\n✓ Data is ready. You can now process test steps.")
            
            # Show learned selectors summary
            print(f"\n📊 Total learned selectors: {len(executor.learned_selectors)}")
            print(f"📈 Selectors reused: {executor.performance_metrics.get('selectors_reused', 0)}")
            print(f"🧠 New selectors learned: {executor.performance_metrics.get('selectors_learned', 0)}")
            
        finally:
            await executor.stop_browser()
    
    def extract_schema_sync(self):
        """
        Extract schema using SchemaExtractor's built-in navigation.
        Uses the working navigation from SchemaExtractor.navigate_to_form()
        """
        from playwright.sync_api import sync_playwright
        from SchemaExtractor import SchemaExtractor
        
        print("\n=== Running Schema Extraction ===\n")
        
        # Configuration - extract form name from test steps
        BASE_URL = "https://hrsa-dcpaas--dcpuat.sandbox.my.site.com/pars/s/"
        USERNAME = "sarokiasamy2@dmigs.com.dcp.dcpuat"
        PASSWORD = "Grantee@123"
        
        # Try to extract form name from test steps
        FORM_NAME = self._extract_form_name_from_steps()
        print(f"  Form name detected: {FORM_NAME}")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="msedge", headless=False)
            page = browser.new_page()
            
            # Use SchemaExtractor's proven navigation
            extractor = SchemaExtractor(page, BASE_URL, USERNAME, PASSWORD, FORM_NAME)
            
            print("\n  Navigating to form...")
            extractor.navigate_to_form()
            
            print("\n  Extracting schema from all pages...")
            extractor.extract_schema()
            extractor.output_schema()
            
            browser.close()
            print("\n✓ Schema extraction complete")
    
    def _extract_form_name_from_steps(self) -> str:
        """Extract form name (e.g., CBD-01361) from test steps"""
        steps = self.load_test_steps()
        
        for step in steps:
            # Look for Click "XXX-NNNNN" pattern
            match = re.search(r'Click\s+"([A-Z]{2,4}-\d{4,6})"', step, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Default fallback
        return "CBD-01361"
    
    def execute_all_datasets(self, num_rows: int = None, use_ai: bool = False):
        """
        Execute test steps for all datasets using EnhancedTestExecutor with learned selectors.
        Uses the same executor infrastructure as ui_real_test_server.py.
        Generates Final Test steps.txt with all executed steps.
        """
        import asyncio
        
        # Run async execution
        return asyncio.run(self._execute_all_datasets_async(num_rows, use_ai))
    
    async def _execute_all_datasets_async(self, num_rows: int = None, use_ai: bool = False):
        """
        Async execution using EnhancedTestExecutor with learned selectors.
        Uses the same executor infrastructure as ui_real_test_server.py.
        
        Each dataset gets a FRESH browser instance:
        - Launch browser → Execute dataset → Close browser
        - Repeat for each dataset
        """
        # Load data
        headers, rows = load_data_csv(self.data_file)
        if num_rows:
            rows = rows[:num_rows]
        
        total_datasets = len(rows)
        print(f"\n=== Executing {total_datasets} Datasets ===")
        print(f"📋 Each dataset will launch a fresh browser instance")
        
        # Configuration
        BASE_URL = "https://hrsa-dcpaas--dcpuat.sandbox.my.site.com/pars/s/"
        
        all_executed_steps = []
        test_steps = self.load_test_steps()
        
        # Track metrics across all datasets
        total_selectors_reused = 0
        total_selectors_learned = 0
        
        for dataset_idx in range(total_datasets):
            dataset_id = f"Dataset_{dataset_idx + 1:03d}"
            print(f"\n{'='*50}")
            print(f"  {dataset_id} ({dataset_idx + 1}/{total_datasets})")
            print(f"{'='*50}")
            
            # Get FRESH executor for each dataset (loads latest learned selectors)
            executor = self.get_executor(use_ai)
            print(f"  📊 Learned selectors available: {len(executor.learned_selectors)}")
            
            # Get data for this row
            data = rows[dataset_idx]
            
            # Add dataset header to output
            all_executed_steps.append(f"# {'='*40}\n")
            all_executed_steps.append(f"# {dataset_id}\n")
            all_executed_steps.append(f"# {'='*40}\n\n")
            
            try:
                # Launch browser for this dataset
                print(f"\n  🚀 Launching browser for {dataset_id}...")
                await executor.start_browser(BASE_URL, headless=False, browser="edge")
                
                # Execute each step
                for step_idx, step in enumerate(test_steps):
                    # Replace placeholders with data
                    processed_step = step.strip()
                    placeholders = PLACEHOLDER_PATTERN.findall(step)
                    
                    for placeholder in placeholders:
                        matching_field = find_matching_field(placeholder, headers)
                        if matching_field and matching_field in data:
                            value = data[matching_field]
                            if value and value.lower() not in ['n/a', 'na', '']:
                                processed_step = processed_step.replace(f"%{placeholder}%", value)
                    
                    # Skip empty lines and comments
                    if not processed_step or processed_step.startswith('#'):
                        continue
                    
                    # Execute the step using EnhancedTestExecutor (with learned selectors)
                    print(f"    {step_idx + 1}. {processed_step[:60]}...")
                    success = await executor.execute_step(processed_step)
                    
                    status = "✓" if success else "✗"
                    print(f"       {status}")
                    
                    # Check if selector was learned
                    parsed = executor.parse_plain_text_step(processed_step)
                    if parsed and 'target' in parsed:
                        target_key = parsed['target'].lower().replace(' ', '_')
                        if target_key in executor.learned_selectors:
                            learned = executor.learned_selectors[target_key]
                            if learned['success_count'] == 1:
                                print(f"       🧠 Learned: {learned['selector'][:50]}...")
                    
                    # Log the step
                    all_executed_steps.append(f"{processed_step}\n")
                    
                    if not success:
                        print(f"       ⚠️ Step failed, continuing...")
                    
                    await asyncio.sleep(0.3)
                
                # Add separator between datasets
                all_executed_steps.append("\n")
                
                # Track metrics
                total_selectors_reused += executor.performance_metrics.get('selectors_reused', 0)
                total_selectors_learned += executor.performance_metrics.get('selectors_learned', 0)
                
                print(f"\n  ✓ {dataset_id} completed")
                print(f"    📈 Selectors reused: {executor.performance_metrics.get('selectors_reused', 0)}")
                print(f"    🧠 New selectors learned: {executor.performance_metrics.get('selectors_learned', 0)}")
                
            finally:
                # Close browser after each dataset
                print(f"  🛑 Closing browser for {dataset_id}...")
                await executor.stop_browser()
                await asyncio.sleep(1)  # Brief pause between datasets
        
        # Save all executed steps to Final Test steps.txt
        final_output = "Final Test steps.txt"
        with open(final_output, 'w', encoding='utf-8') as f:
            f.writelines(all_executed_steps)
        
        # Load final executor to get total learned selectors count
        final_executor = self.get_executor(False)
        
        # Show summary
        print(f"\n{'='*50}")
        print(f"✓ All {total_datasets} datasets executed!")
        print(f"✓ Final output saved to: {final_output}")
        print(f"{'='*50}")
        print(f"📊 Total learned selectors: {len(final_executor.learned_selectors)}")
        print(f"📈 Total selectors reused: {total_selectors_reused}")
        print(f"🧠 Total new selectors learned: {total_selectors_learned}")
        print(f"{'='*50}")
        
        return final_output
    
    def _find_form_steps_start(self, steps: list) -> int:
        """Find where form data entry steps begin (after navigation)"""
        for i, step in enumerate(steps):
            # Form steps typically start after waiting for the form to load
            # Look for first placeholder or after "Wait for 20 seconds"
            if self.has_placeholder(step):
                return i
            if "Wait for 20 seconds" in step:
                return i + 1
        return 0


def load_data_csv(data_file: str = "data.csv") -> tuple:
    """Load data from CSV file"""
    with open(data_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        rows = list(reader)
    return headers, rows


def find_matching_field(placeholder: str, headers: list) -> str:
    """Find matching field header for a placeholder"""
    placeholder_clean = placeholder.lower().strip()
    
    # Exact match (case-insensitive)
    for header in headers:
        if header.lower().strip() == placeholder_clean:
            return header
    
    # Partial match - placeholder contained in header
    for header in headers:
        if placeholder_clean in header.lower():
            return header
    
    # Partial match - header contained in placeholder
    for header in headers:
        if header.lower().strip() in placeholder_clean:
            return header
    
    return None


def process_test_steps(test_steps_file: str,
                       data_file: str = "data.csv",
                       dataset_row: int = 0,
                       output_file: str = None) -> list:
    """Process test steps file and replace placeholders with data"""
    headers, rows = load_data_csv(data_file)
    
    if dataset_row >= len(rows):
        print(f"Error: Dataset row {dataset_row + 1} not found. Only {len(rows)} rows available.")
        return []
    
    data = rows[dataset_row]
    dataset_id = f"Dataset_{dataset_row + 1:03d}"
    
    with open(test_steps_file, 'r', encoding='utf-8') as f:
        test_steps = f.readlines()
    
    processed_steps = []
    
    # Add dataset identifier
    processed_steps.append(f"# ========================================\n")
    processed_steps.append(f"# {dataset_id}\n")
    processed_steps.append(f"# ========================================\n")
    processed_steps.append(f"\n")
    
    for line in test_steps:
        processed_line = line
        placeholders = PLACEHOLDER_PATTERN.findall(line)
        
        for placeholder in placeholders:
            matching_field = find_matching_field(placeholder, headers)
            
            if matching_field:
                value = data.get(matching_field, '')
                value = str(value).strip().strip("'\"")
                processed_line = processed_line.replace(f'%{placeholder}%', value)
            else:
                print(f"  Warning: No data found for placeholder '%{placeholder}%'")
        
        processed_steps.append(processed_line)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(processed_steps)
        print(f"✓ Processed test steps saved to: {output_file}")
    
    return processed_steps


def process_all_datasets(test_steps_file: str,
                         data_file: str = "data.csv",
                         output_file: str = "processed_test_steps.txt") -> str:
    """Process test steps for all datasets"""
    headers, rows = load_data_csv(data_file)
    all_processed = []
    
    for i in range(len(rows)):
        print(f"Processing Dataset {i + 1}/{len(rows)}...")
        steps = process_test_steps(test_steps_file, data_file, i, output_file=None)
        all_processed.extend(steps)
        all_processed.append("\n")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(all_processed)
    
    print(f"\n✓ All {len(rows)} datasets processed to: {output_file}")
    return output_file


def main():
    TEST_STEPS_FILE = "Sample Test Steps.txt"
    DATA_FILE = "data.csv"
    SCHEMA_FILE = "outputs/fields.json"
    OUTPUT_FILE = "processed_test_steps.txt"
    
    # Parse arguments
    dataset_row = 0
    process_all = False
    run_browser = False
    generate_only = False
    execute_tests = False
    use_ai = False
    num_rows = 100
    execute_rows = None  # Number of rows to execute
    
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--dataset" and i + 1 < len(args):
            dataset_row = int(args[i + 1]) - 1
            i += 2
        elif args[i] == "--all":
            process_all = True
            i += 1
        elif args[i] == "--run":
            run_browser = True
            i += 1
        elif args[i] == "--execute":
            execute_tests = True
            run_browser = True
            i += 1
        elif args[i] == "--ai":
            use_ai = True
            i += 1
        elif args[i] == "--generate-only":
            generate_only = True
            i += 1
        elif args[i] == "--rows" and i + 1 < len(args):
            num_rows = int(args[i + 1])
            execute_rows = int(args[i + 1])
            i += 2
        elif args[i] == "--help":
            print("""
Test Step Processor - Dynamic Test Generation and Execution
Uses EnhancedTestExecutor with LEARNED SELECTORS (same as ui_real_test_server.py)

Usage:
  python test_step_processor.py [options]

Options:
  --run              Navigate browser, extract schema, and generate data if data.csv missing
  --execute          Execute all test steps in browser using learned selectors
  --ai               Use Gemini AI Enhanced Executor for intelligent selector generation
  --rows N           Number of data rows to generate/execute (default: 100)
  --dataset N        Process only dataset N (1-indexed)
  --all              Process all datasets to single output file
  --generate-only    Only generate processed files, don't execute
  --help             Show this help message

Features:
  - Uses learned selectors from test_learning.json (shared with ui_real_test_server.py)
  - Auto-learns new selectors when they work
  - Supports Gemini AI for intelligent selector generation (--ai flag)
  - Generates Final Test steps.txt with all executed datasets

Examples:
  python test_step_processor.py --execute --rows 2              # Execute 2 datasets with learned selectors
  python test_step_processor.py --execute --rows 2 --ai         # Execute with Gemini AI
  python test_step_processor.py --run --rows 5 --execute        # Generate data and execute
  python test_step_processor.py --dataset 1                     # Process dataset 1 only
            """)
            return
        else:
            i += 1
    
    if not Path(TEST_STEPS_FILE).exists():
        print(f"Error: Test steps file not found: {TEST_STEPS_FILE}")
        return
    
    processor = TestStepProcessor(TEST_STEPS_FILE, DATA_FILE, SCHEMA_FILE)
    
    # Check if we need to extract schema and generate data
    if not processor.data_exists():
        print(f"✗ Data file not found: {DATA_FILE}")
        
        if run_browser:
            print("\n>>> Running browser to navigate and extract schema...")
            processor.extract_schema_sync()
            
            if processor.schema_exists():
                processor.generate_data(num_rows)
            else:
                print("✗ Schema extraction failed. Cannot generate data.")
                return
        else:
            print("\nOptions:")
            print("  1. Run with --run flag to navigate and extract schema automatically")
            print("  2. Run 'python main.py' to extract schema manually")
            print("\nExample: python test_step_processor.py --run --rows 100")
            return
    
    # Execute tests in browser if --execute flag is set
    if execute_tests:
        print(f"\n>>> Executing test steps in browser using learned selectors...")
        if use_ai:
            print("🤖 Gemini AI mode enabled")
        processor.execute_all_datasets(num_rows=execute_rows, use_ai=use_ai)
        return
    
    if generate_only or not run_browser:
        # Just process the test steps file
        print(f"\nProcessing test steps from: {TEST_STEPS_FILE}")
        print(f"Using data from: {DATA_FILE}")
        print("-" * 50)
        
        if process_all:
            process_all_datasets(TEST_STEPS_FILE, DATA_FILE, OUTPUT_FILE)
        else:
            output = f"processed_test_dataset_{dataset_row + 1:03d}.txt"
            process_test_steps(TEST_STEPS_FILE, DATA_FILE, dataset_row, output)
        
        print("\nDone!")


if __name__ == "__main__":
    main()
