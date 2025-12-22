# Data Generation Integration with Placeholder Detection

## Overview

This integration enables automatic data generation when test steps contain placeholders (e.g., `Type "%Number of people on listserv%" into "Number of people on listserv"`). The system detects placeholders, generates appropriate test data based on user-specified positive/negative scenario counts, and uses the generated data during test execution.

## Features

### 1. UI Controls (Real Test Dashboard)

Three new controls have been added to the test execution dashboard:

- **Positive Scenarios** (textbox): Number of positive test data rows to generate (default: 5)
- **Negative Scenarios** (textbox): Number of negative test data rows to generate (default: 5)
- **Data Type for Execution** (dropdown): Select which type of data to use during execution
  - `Use Positive Data`: Only use rows marked as positive scenarios
  - `Use Negative Data`: Only use rows marked as negative scenarios
  - `Use Mixed Data`: Use both positive and negative scenarios

### 2. Automatic Data Generation Flow

When test execution begins:

1. **Placeholder Detection**: The system scans all test steps for placeholders using the pattern `%Field Name%`
2. **Data Check**: Checks if `outputs/data.csv` exists and contains data for the detected placeholders
3. **Schema Extraction & Data Generation** (if needed):
   - Extracts all unique placeholders from test steps
   - Creates a simple schema for each placeholder field
   - Uses `DataGenerator.py` to generate realistic data:
     - **Positive scenarios**: Valid data that meets field requirements
     - **Negative scenarios**: Invalid data for testing error handling
   - Outputs to `outputs/data.csv` with columns: `Scenario Type`, `Data Used`, and one column per placeholder
4. **Data Selection**: Based on the "Data Type for Execution" setting, selects an appropriate unused row
5. **Placeholder Replacement**: During execution, replaces placeholders with actual values from the selected data row
6. **Execution**: Continues test execution with the replaced values

### 3. Data.csv Format

```csv
Scenario Type,Data Used,Number of people on listserv,Field Name 2,...
'Positive','False','26','Value1',...
'Positive','False','42','Value2',...
'Negative','False','abc','InvalidValue',...
```

- **Scenario Type**: 'Positive' or 'Negative'
- **Data Used**: 'False' initially, marked 'True' after use (prevents reuse)
- **Field columns**: One column per placeholder, containing generated data

## Modified Files

### 1. `ui/real_test_dashboard.html`
- Added data generation settings UI section with 3 controls
- Updated `runTest()` and `runTestWithAI()` functions to send data generation parameters to API

### 2. `ui_real_test_server.py`
- Updated `/api/execute-test` endpoint to accept:
  - `positive_scenarios` (int)
  - `negative_scenarios` (int)
  - `data_type` (string: 'positive', 'negative', or 'mixed')
- Modified `run_test_with_updates()` to pass parameters to executor
- Calls `executor.set_data_generation_params()` to configure the executor

### 3. `enhanced_test_executor.py`
- Added instance variables:
  - `positive_scenarios`, `negative_scenarios`, `data_type`
  - `all_test_steps` (for context when generating data)
- Added methods:
  - `set_data_generation_params()`: Configure data generation settings
  - `generate_data_for_current_page()`: Generate data.csv when placeholders are detected
  - `_get_next_row_by_type()`: Filter data rows based on data_type preference
- Modified `process_step_placeholders_async()`:
  - Detects missing placeholder data
  - Triggers data generation if data.csv doesn't exist
  - Reloads data consumer after generation
- Modified `initialize_data_for_execution()`:
  - Respects data_type setting when selecting rows
  - Logs which scenario type is being used

### 4. `DataGenerator.py` (existing, used by integration)
- `generate_correct()`: Generates valid data for positive scenarios
- `generate_incorrect()`: Generates invalid data for negative scenarios

## Usage Example

### Test Steps with Placeholders
```
Wait for 2 seconds
Type "%Username%" into "Username"
Type "%Password%" into "Password"
Type "%Number of people on listserv%" into "Number of people on listserv"
Click "Submit"
```

### Execution Flow

1. User sets:
   - Positive Scenarios: 5
   - Negative Scenarios: 5
   - Data Type: "Use Positive Data"

2. User clicks "Run Test" button

3. System detects placeholders: `Username`, `Password`, `Number of people on listserv`

4. If `outputs/data.csv` doesn't exist:
   - Generates 5 positive rows with valid data
   - Generates 5 negative rows with invalid data
   - Saves to `outputs/data.csv`

5. Selects first unused positive scenario row (based on "Use Positive Data" setting)

6. During execution:
   - `Type "%Username%" into "Username"` becomes `Type "john.doe@example.com" into "Username"`
   - `Type "%Number of people on listserv%" into "Number of people on listserv"` becomes `Type "26" into "Number of people on listserv"`

7. After successful execution, marks the data row as used

## Data Type Selection Behavior

### Positive Data
- Only uses rows where `Scenario Type = 'Positive'`
- Best for happy path testing
- Data meets all field validation requirements

### Negative Data
- Only uses rows where `Scenario Type = 'Negative'`
- Best for error handling and validation testing
- Data intentionally violates field requirements

### Mixed Data
- Uses both positive and negative rows
- Alternates between valid and invalid data
- Comprehensive testing approach

## Integration with Existing DatasetGenerator

The current implementation uses a **simplified data generation approach** that:
- Extracts placeholders from test steps
- Creates basic text field schemas
- Generates data using `DataGenerator.py`

For **full schema extraction** from the actual page (using `DatasetGenerator.py`):
- The page needs to be navigated to the form
- `DatasetGenerator.extract_schema_output_csv()` can be called
- This extracts actual field types, patterns, min/max lengths from the DOM
- More accurate data generation based on real field constraints

**Note**: The full `DatasetGenerator` integration requires synchronous Playwright API, while the test executor uses async API. The simplified approach works around this limitation.

## Future Enhancements

1. **Full Schema Extraction**: Integrate with `DatasetGenerator.extract_schema_output_csv()` to extract real field schemas from the page
2. **Field Type Detection**: Automatically detect field types (text, number, select, etc.) from the page
3. **Data Persistence**: Option to save/load data sets for reuse across test runs
4. **Data Validation**: Validate generated data against actual page constraints before execution
5. **Multi-Page Support**: Generate data for multi-page forms with "Next" button navigation

## Troubleshooting

### Issue: Placeholders not being replaced
- **Check**: Ensure placeholder format is exactly `%Field Name%` with percent signs
- **Check**: Verify `outputs/data.csv` exists and contains the field columns
- **Check**: Look for log messages indicating data generation status

### Issue: No data available error
- **Check**: Verify positive/negative scenario counts are > 0
- **Check**: Ensure data_type selection matches available data (e.g., don't select "Use Positive Data" if only negative scenarios were generated)
- **Check**: Reset data usage via `/api/reset-data-usage` endpoint if all rows are marked as used

### Issue: Data generation fails
- **Check**: Browser console and server logs for error messages
- **Check**: Ensure `outputs/` directory is writable
- **Check**: Verify `DataGenerator.py` is accessible and has no import errors

## API Endpoints

### POST /api/execute-test
```json
{
  "url": "https://example.com",
  "steps": ["Type \"%Field%\" into \"Field\""],
  "positive_scenarios": 5,
  "negative_scenarios": 5,
  "data_type": "positive"
}
```

### GET /api/data-status
Returns current data consumption status

### POST /api/reset-data-usage
Resets all data rows to unused state

## Logs and Debugging

The system provides detailed logging during execution:
- `📊 Data generation params set`: Confirms parameters received
- `🔍 Extracting schema and generating data`: Data generation started
- `✅ Data generated successfully`: Data generation completed
- `📊 Using data row X (Positive/Negative scenario)`: Shows which row is being used
- `✓ Replaced %Field% → value`: Shows placeholder replacement

Check the Live Execution Log in the dashboard for real-time updates.
