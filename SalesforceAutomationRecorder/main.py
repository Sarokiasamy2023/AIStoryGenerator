from SchemaExtractor import SchemaExtractor
from DataGenerator import DataGenerator
from playwright.sync_api import sync_playwright
import sys
from pathlib import Path

BASE_URL = "https://hrsa-dcpaas--dcpuat.sandbox.my.site.com/pars/s/"
USERNAME = "sarokiasamy2@dmigs.com.dcp.dcpuat"
PASSWORD = "Grantee@123"
FORM_NAME = "CBD-01361"

def main(skip_navigation: bool = False, generate_data: bool = True, num_rows: int = 100):
    """
    Main entry point for schema extraction and data generation
    
    Args:
        skip_navigation: If True, skip navigation (assumes form is already open via test steps)
        generate_data: If True, generate data.csv after schema extraction
        num_rows: Number of data rows to generate
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=False)
        print("OPENING THE BROWSER")
        page = browser.new_page()

        schemaExtractor = SchemaExtractor(page, BASE_URL, USERNAME, PASSWORD, FORM_NAME)

        if not skip_navigation:
            print("\nNAVIGATING TO FORM")
            schemaExtractor.navigate_to_form()
        else:
            print("\nSKIPPING NAVIGATION (form should be open via test steps)")

        print("\nEXTRACTING SCHEMA")
        schemaExtractor.extract_schema()

        print("\nOUTPUTTING SCHEMA")
        schemaExtractor.output_schema()
        
        browser.close()
    
    # Generate data if requested
    if generate_data:
        schema_file = "outputs/fields.json"
        if Path(schema_file).exists():
            print("\nGENERATING TEST DATA")
            try:
                generator = DataGenerator(schema_file)
                generator.generate_all_data(num_rows=num_rows, output_file="data.csv")
                print(f"✓ Generated {num_rows} rows of test data to data.csv")
            except Exception as e:
                print(f"✗ Error generating data: {e}")
        else:
            print(f"✗ Schema file not found: {schema_file}")


if __name__ == "__main__":
    # Parse command line arguments
    skip_nav = "--skip-nav" in sys.argv or "--skip-navigation" in sys.argv
    no_data = "--no-data" in sys.argv
    
    # Get num_rows if specified
    num_rows = 100
    for i, arg in enumerate(sys.argv):
        if arg == "--rows" and i + 1 < len(sys.argv):
            num_rows = int(sys.argv[i + 1])
    
    if "--help" in sys.argv:
        print("""
Usage: python main.py [options]

Options:
    --skip-nav, --skip-navigation   Skip form navigation (use when form is already open)
    --no-data                       Don't generate data.csv after schema extraction
    --rows N                        Number of data rows to generate (default: 100)
    --help                          Show this help message
        """)
    else:
        main(skip_navigation=skip_nav, generate_data=not no_data, num_rows=num_rows)