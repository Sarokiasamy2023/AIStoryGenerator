"""
Generate Test Steps from fields.json and data.csv
Combines field metadata with test data to create executable test steps
"""

import json
import csv
from pathlib import Path


def load_fields_json(fields_file: str = "fields.json") -> dict:
    """Load field definitions from fields.json"""
    with open(fields_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_all_data_csv(data_file: str = "data.csv") -> tuple:
    """
    Load all data from CSV file
    Returns:
        Tuple of (headers, list of data rows as dicts)
    """
    with open(data_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
        
        headers = rows[0]
        all_data = []
        
        for row_idx, data_row in enumerate(rows[1:], start=1):
            data = {}
            for i, header in enumerate(headers):
                if i < len(data_row):
                    # Clean value (remove quotes)
                    value = data_row[i].strip().strip("'\"")
                    data[header] = value
            all_data.append(data)
        
        return headers, all_data


def load_data_csv(data_file: str = "data.csv", row_number: int = 0) -> dict:
    """
    Load single data row from CSV file
    Args:
        data_file: Path to CSV file
        row_number: Data row to use (0 = first data row after header)
    Returns:
        Dictionary mapping API name to value
    """
    headers, all_data = load_all_data_csv(data_file)
    if row_number < len(all_data):
        return all_data[row_number]
    return {}


def clean_label(label: str) -> str:
    """Clean field label by removing asterisks and extra whitespace"""
    # Remove asterisks and clean up
    cleaned = label.replace('*', '').strip()
    # Remove leading/trailing whitespace
    cleaned = ' '.join(cleaned.split())
    return cleaned


def get_field_type_for_test(field_type: str) -> str:
    """Map field type to test step type"""
    type_mapping = {
        'text': 'text',
        'textarea': 'textarea',
        'select': 'dropdown',
        'checkbox': 'checkbox',
        'date': 'text',
        'number': 'text'
    }
    return type_mapping.get(field_type.lower(), 'text')


def generate_test_step(label: str, field_type: str, value: str) -> str:
    """Generate a test step based on field type"""
    
    # Skip empty or N/A values
    if not value or value.lower() in ['n/a', 'na', '']:
        return None
    
    if field_type == 'text':
        return f'Type "{value}" into "{label}"'
    elif field_type == 'textarea':
        return f'Fill textarea "{label}" with "{value}"'
    elif field_type == 'dropdown':
        return f'Select "{value}" from Dropdown "{label}"'
    elif field_type == 'checkbox':
        if value.lower() in ['true', 'yes', '1', 'checked']:
            return f'Check "{label}"'
        return None
    else:
        return f'Type "{value}" into "{label}"'


def merge_field_mapping_with_all_data(fields_file: str = "fields.json",
                                       data_file: str = "data.csv",
                                       output_file: str = "field_mapping_all_data.csv"):
    """
    Merge fields.json metadata with ALL data rows from data.csv
    Creates a comprehensive CSV with Dataset_ID, Field_API_Name, Field_Label, Field_Type, Value
    """
    fields = load_fields_json(fields_file)
    headers, all_data = load_all_data_csv(data_file)
    
    rows = []
    
    for dataset_idx, data in enumerate(all_data, start=1):
        dataset_id = f"Dataset_{dataset_idx:03d}"
        
        for api_name, field_info in fields.items():
            label = clean_label(field_info.get('label', api_name))
            field_type = get_field_type_for_test(field_info.get('type', 'text'))
            value = data.get(api_name, '')
            
            rows.append({
                'Dataset_ID': dataset_id,
                'Field_API_Name': api_name,
                'Field_Label': label,
                'Field_Type': field_type,
                'Value': value
            })
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Dataset_ID', 'Field_API_Name', 'Field_Label', 'Field_Type', 'Value'])
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Merged {len(all_data)} datasets with {len(fields)} fields = {len(rows)} rows")
    print(f"Output: {output_file}")
    return rows


def generate_test_steps_for_dataset(fields: dict, data: dict, dataset_id: str, add_waits: bool = True) -> list:
    """Generate test steps for a single dataset"""
    test_steps = []
    
    for api_name, field_info in fields.items():
        label = clean_label(field_info.get('label', api_name))
        field_type = get_field_type_for_test(field_info.get('type', 'text'))
        value = data.get(api_name, '')
        
        # Clean value
        value = value.strip().strip("'\"")
        
        step = generate_test_step(label, field_type, value)
        if step:
            test_steps.append(step)
            if add_waits:
                test_steps.append("Wait for 1 seconds")
    
    return test_steps


def generate_all_tests_single_file(fields_file: str = "fields.json",
                                    data_file: str = "data.csv",
                                    output_file: str = "generated_test.txt",
                                    add_waits: bool = True):
    """
    Generate test steps for ALL datasets in a single file with identifiers
    """
    fields = load_fields_json(fields_file)
    headers, all_data = load_all_data_csv(data_file)
    
    all_test_steps = []
    
    for dataset_idx, data in enumerate(all_data, start=1):
        dataset_id = f"Dataset_{dataset_idx:03d}"
        
        # Add dataset header/identifier
        all_test_steps.append(f"")
        all_test_steps.append(f"# ========================================")
        all_test_steps.append(f"# {dataset_id}")
        all_test_steps.append(f"# ========================================")
        all_test_steps.append(f"")
        
        # Generate steps for this dataset
        steps = generate_test_steps_for_dataset(fields, data, dataset_id, add_waits)
        all_test_steps.extend(steps)
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_test_steps))
    
    print(f"Generated test steps for {len(all_data)} datasets to {output_file}")
    return all_test_steps


def generate_test_steps(fields_file: str = "fields.json",
                        data_file: str = "data.csv", 
                        row_number: int = 0,
                        output_file: str = None,
                        add_waits: bool = True):
    """
    Generate test steps from fields.json and data.csv for a single dataset
    
    Args:
        fields_file: Path to fields.json
        data_file: Path to data.csv
        row_number: Which data row to use (0 = first data row)
        output_file: Optional output file for test steps
        add_waits: Add wait steps between actions
    """
    fields = load_fields_json(fields_file)
    data = load_data_csv(data_file, row_number)
    
    dataset_id = f"Dataset_{row_number + 1:03d}"
    test_steps = generate_test_steps_for_dataset(fields, data, dataset_id, add_waits)
    
    # Output
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(test_steps))
        print(f"Generated {len([s for s in test_steps if not s.startswith('Wait')])} test steps to {output_file}")
    else:
        print("\n=== Generated Test Steps ===\n")
        for step in test_steps:
            print(step)
    
    return test_steps


def generate_all_test_rows(fields_file: str = "fields.json",
                           data_file: str = "data.csv",
                           output_dir: str = "generated_tests"):
    """
    Generate separate test files for each data row
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    headers, all_data = load_all_data_csv(data_file)
    row_count = len(all_data)
    
    print(f"Generating tests for {row_count} data rows...")
    
    for i in range(row_count):
        output_file = output_path / f"test_dataset_{i+1:03d}.txt"
        generate_test_steps(fields_file, data_file, i, str(output_file), add_waits=True)
    
    print(f"\nGenerated {row_count} test files in {output_dir}/")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--merge":
            # Merge field mapping with all data
            merge_field_mapping_with_all_data()
        elif sys.argv[1] == "--all":
            # Generate all datasets in single file
            generate_all_tests_single_file()
        elif sys.argv[1] == "--separate":
            # Generate separate files for each dataset
            generate_all_test_rows()
        elif sys.argv[1].isdigit():
            # Generate single test for specified row
            row = int(sys.argv[1])
            generate_test_steps(row_number=row, output_file=f"test_dataset_{row+1:03d}.txt")
        else:
            print("Usage:")
            print("  python generate_test_from_fields.py           # Generate test for first dataset")
            print("  python generate_test_from_fields.py --merge   # Merge all data into field_mapping_all_data.csv")
            print("  python generate_test_from_fields.py --all     # Generate all datasets in single file")
            print("  python generate_test_from_fields.py --separate # Generate separate files per dataset")
            print("  python generate_test_from_fields.py 5         # Generate test for dataset 6 (0-indexed)")
    else:
        # Default: merge data and generate all tests
        merge_field_mapping_with_all_data()
        generate_all_tests_single_file()
