"""
Generate Test Steps from Field Mapping CSV
Reads field_mapping.csv and generates test step commands
"""

import csv
from pathlib import Path


def generate_test_steps(mapping_file: str = "field_mapping.csv", output_file: str = None):
    """
    Generate test steps from field mapping CSV
    
    CSV Format:
        Field_Name,Field_Type,Data
        
    Field Types:
        - text: Type "value" into "field_name"
        - textarea: Fill textarea "field_name" with "value"
        - dropdown: Select "value" from Dropdown "field_name"
        - checkbox: Check "field_name"
        - date: Type "value" into "field_name"
        - lookup: Type "value" into "field_name"
        - upload: Upload "filepath" to "field_name"
    """
    
    mapping_path = Path(mapping_file)
    if not mapping_path.exists():
        print(f"Error: {mapping_file} not found")
        return None
    
    test_steps = []
    
    with open(mapping_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            field_name = row.get('Field_Name', '').strip()
            field_type = row.get('Field_Type', 'text').strip().lower()
            data = row.get('Data', '').strip()
            
            if not field_name or not data:
                continue
            
            # Skip N/A, n/a, N/a values
            if data.lower() in ['n/a', 'na', '']:
                continue
            
            # Generate step based on field type
            step = generate_step(field_name, field_type, data)
            if step:
                test_steps.append(step)
                # Add wait after each step
                test_steps.append("Wait for 1 seconds")
    
    # Output results
    if output_file:
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(test_steps))
        print(f"Generated {len(test_steps) // 2} test steps to {output_file}")
    else:
        print("\n=== Generated Test Steps ===\n")
        for step in test_steps:
            print(step)
    
    return test_steps


def generate_step(field_name: str, field_type: str, data: str) -> str:
    """Generate a single test step based on field type"""
    
    # Escape quotes in data
    data = data.replace('"', '\\"')
    
    if field_type == 'text' or field_type == 'date' or field_type == 'lookup':
        return f'Type "{data}" into "{field_name}"'
    
    elif field_type == 'textarea':
        return f'Fill textarea "{field_name}" with "{data}"'
    
    elif field_type == 'dropdown':
        return f'Select "{data}" from Dropdown "{field_name}"'
    
    elif field_type == 'checkbox':
        if data.lower() in ['true', 'yes', '1', 'checked']:
            return f'Check "{field_name}"'
        return None  # Don't generate step for unchecked checkboxes
    
    elif field_type == 'upload':
        return f'Upload "{data}" to "{field_name}"'
    
    else:
        # Default to text type
        return f'Type "{data}" into "{field_name}"'


def generate_from_data_csv(data_csv: str, mapping_csv: str, row_number: int = 2, output_file: str = None):
    """
    Generate test steps by combining data.csv values with field_mapping.csv metadata
    
    Args:
        data_csv: Path to data.csv with values
        mapping_csv: Path to field_mapping.csv with field metadata
        row_number: Which data row to use (1-indexed, row 1 is header)
        output_file: Optional output file path
    """
    
    # Load field mapping
    mapping = {}
    with open(mapping_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            field_name = row.get('Field_Name', '').strip()
            field_type = row.get('Field_Type', 'text').strip().lower()
            if field_name:
                mapping[field_name] = field_type
    
    # Load specific data row
    with open(data_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
        
        if row_number >= len(rows):
            print(f"Error: Row {row_number} not found in {data_csv}")
            return None
        
        headers = rows[0]
        data_row = rows[row_number]
    
    test_steps = []
    
    for i, header in enumerate(headers):
        if i >= len(data_row):
            break
        
        data = data_row[i].strip().strip("'\"")
        
        # Skip N/A values
        if data.lower() in ['n/a', 'na', 'n/a', '']:
            continue
        
        # Find matching field name and type from mapping
        field_name = None
        field_type = 'text'
        
        for name, ftype in mapping.items():
            # Match by similarity (field name might be shortened in API name)
            if name.lower().replace(' ', '_')[:20] in header.lower()[:20]:
                field_name = name
                field_type = ftype
                break
        
        if not field_name:
            # Use header as fallback field name
            field_name = header.replace('__c', '').replace('_', ' ').title()
        
        step = generate_step(field_name, field_type, data)
        if step:
            test_steps.append(step)
            test_steps.append("Wait for 1 seconds")
    
    # Output results
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(test_steps))
        print(f"Generated {len(test_steps) // 2} test steps to {output_file}")
    else:
        print("\n=== Generated Test Steps ===\n")
        for step in test_steps:
            print(step)
    
    return test_steps


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Use command line argument as mapping file
        generate_test_steps(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        # Default: use field_mapping.csv
        generate_test_steps("field_mapping.csv", "generated_test.txt")
