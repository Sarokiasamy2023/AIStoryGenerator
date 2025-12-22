# CBD-SHCP Program Form Test Cases - Your Format

## Test Cases Matching Your Organization's Format

| Test Case ID | Test Role (PO) / Grantee | Bureau - Program | Module/Section | Test Case Description | Test Steps | Expected Result |
|--------------|-------------------------|------------------|----------------|----------------------|------------|-----------------|
| CBD_TC_010 | Grantee | CBD-SHCP | Performance Reports | Verify Counties Served Field in Form 1: Demographics accepts valid alphanumeric input | 1. Login as PO/VC<br>2. Navigate to CBD Performance Reports<br>3. Click on "In Progress Reports"<br>4. Click on the Report "CBD-01361"<br>5. Click on "Form1: Demographics"<br><br>User enters valid alphanumeric text with spaces and punctuation in the field "Counties Served" (e.g., "Los Angeles, Orange County & San Diego") | Field accepts input and saves successfully.<br>User should able to Navigate to the Form |
| CBD_TC_011 | Grantee | CBD-SHCP | Performance Reports | Verify Counties Served Field in Form 1: Demographics accepts maximum 2000 characters | 1. Login as PO/VC<br>2. Navigate to CBD Performance Reports<br>3. Click on "In Progress Reports"<br>4. Click on the Report "CBD-01361"<br>5. Click on "Form1: Demographics"<br><br>User enters exactly 2000 characters for the field "Counties Served" | Field accepts input with no error.<br>User should able to Navigate to the Form |
| CBD_TC_012 | Grantee | CBD-SHCP | Performance Reports | Verify Counties Served Field in Form 1: Demographics rejects more than 2000 characters | 1. Login as PO/VC<br>2. Navigate to CBD Performance Reports<br>3. Click on "In Progress Reports"<br>4. Click on the Report "CBD-01361"<br>5. Click on "Form1: Demographics"<br><br>User enters more than 2000 characters for the System shows error: "Maximum limit is field "Counties Served" | 2000 characters."<br>User should able to Navigate to the Form |
| CBD_TC_013 | Grantee | CBD-SHCP | Performance Reports | Verify Full Patient Panel Field in Form 1: Demographics accepts valid whole numbers | 1. Login as PO/VC<br>2. Navigate to CBD Performance Reports<br>3. Click on "In Progress Reports"<br>4. Click on the Report "CBD-01361"<br>5. Click on "Form1: Demographics"<br><br>User enters a whole number lower than 10 digits for the field "Full Patient Panel" | Field accepts and saves successfully.<br>User should able to Navigate to the Form |
| CBD_TC_014 | Grantee | CBD-SHCP | Performance Reports | Verify Full Patient Panel Field in Form 1: Demographics accepts maximum 10 digits | 1. Login as PO/VC<br>2. Navigate to CBD Performance Reports<br>3. Click on "In Progress Reports"<br>4. Click on the Report "CBD-01361"<br>5. Click on "Form1: Demographics"<br><br>User enters exactly a 10-digit number (e.g., 9999999999) for the field "Full Patient Panel" | Field accepts input with no error.<br>User should able to Navigate to the Form |
| CBD_TC_015 | Grantee | CBD-SHCP | Performance Reports | Verify Full Patient Panel Field in Form 1: Demographics rejects decimal values | 1. Login as PO/VC<br>2. Navigate to CBD Performance Reports<br>3. Click on "In Progress Reports"<br>4. Click on the Report "CBD-01361"<br>5. Click on "Form1: Demographics"<br><br>User enters a decimal or more than 10 digits for the field "Full Patient Panel" | System shows error: "Allows whole numbers up to 10 digits"<br>User should able to Navigate to the Form |
| CBD_TC_016 | Grantee | CBD-SHCP | Performance Reports | Verify Full Patient Panel Field in Form 1: Demographics rejects more than 10 digits | 1. Login as PO/VC<br>2. Navigate to CBD Performance Reports<br>3. Click on "In Progress Reports"<br>4. Click on the Report "CBD-01361"<br>5. Click on "Form1: Demographics"<br><br>User enters more than 10 digits (e.g., 12345678901) for the field "Full Patient Panel" | System shows error: "Allows whole numbers up to 10 digits"<br>User should able to Navigate to the Form |
| CBD_TC_017 | Grantee | CBD-SHCP | Performance Reports | Verify Changes to Target Population Measures Field in Form 1: Demographics displays dropdown options | 1. Login as PO/VC<br>2. Navigate to CBD Performance Reports<br>3. Click on "In Progress Reports"<br>4. Click on the Report "CBD-01361"<br>5. Click on "Form1: Demographics"<br><br>User clicks on the dropdown for the field "Changes to Target Population Measures" | Dropdown displays exactly three options: "Yes", "No", and "N/A"<br>User should able to Navigate to the Form |
| CBD_TC_018 | Grantee | CBD-SHCP | Performance Reports | Verify Changes to Target Population Measures Field in Form 1: Demographics accepts "Yes" selection | 1. Login as PO/VC<br>2. Navigate to CBD Performance Reports<br>3. Click on "In Progress Reports"<br>4. Click on the Report "CBD-01361"<br>5. Click on "Form1: Demographics"<br><br>User selects "Yes" from the dropdown for the field "Changes to Target Population Measures" | Selection is accepted and saved.<br>User should able to Navigate to the Form |
| CBD_TC_019 | Grantee | CBD-SHCP | Performance Reports | Verify Changes to Target Population Measures Field in Form 1: Demographics accepts "No" selection | 1. Login as PO/VC<br>2. Navigate to CBD Performance Reports<br>3. Click on "In Progress Reports"<br>4. Click on the Report "CBD-01361"<br>5. Click on "Form1: Demographics"<br><br>User selects "No" from the dropdown for the field "Changes to Target Population Measures" | Selection is accepted and saved.<br>User should able to Navigate to the Form |
| CBD_TC_020 | Grantee | CBD-SHCP | Performance Reports | Verify Changes to Target Population Measures Field in Form 1: Demographics accepts "N/A" selection | 1. Login as PO/VC<br>2. Navigate to CBD Performance Reports<br>3. Click on "In Progress Reports"<br>4. Click on the Report "CBD-01361"<br>5. Click on "Form1: Demographics"<br><br>User selects "N/A" from the dropdown for the field "Changes to Target Population Measures" | Selection is accepted and saved.<br>User should able to Navigate to the Form |
| CBD_TC_021 | Grantee | CBD-SHCP | Performance Reports | Verify Changes to Target Population Measures Field in Form 1: Demographics rejects manual text entry | 1. Login as PO/VC<br>2. Navigate to CBD Performance Reports<br>3. Click on "In Progress Reports"<br>4. Click on the Report "CBD-01361"<br>5. Click on "Form1: Demographics"<br><br>User tries to enter or type a value not in the dropdown for the field "Changes to Target Population Measures" | Field does not accept the value; only valid options remain available<br>User should able to Navigate to the Form |
| CBD_TC_022 | Grantee | CBD-SHCP | Performance Reports | Verify Counties Served Field in Form 1: Demographics accepts special characters | 1. Login as PO/VC<br>2. Navigate to CBD Performance Reports<br>3. Click on "In Progress Reports"<br>4. Click on the Report "CBD-01361"<br>5. Click on "Form1: Demographics"<br><br>User enters text with special characters (e.g., "County A, County B; County C & County D - Region (1)") in the field "Counties Served" | Field accepts input with special characters and saves successfully.<br>User should able to Navigate to the Form |
| CBD_TC_023 | Grantee | CBD-SHCP | Performance Reports | Verify Full Patient Panel Field in Form 1: Demographics rejects negative numbers | 1. Login as PO/VC<br>2. Navigate to CBD Performance Reports<br>3. Click on "In Progress Reports"<br>4. Click on the Report "CBD-01361"<br>5. Click on "Form1: Demographics"<br><br>User enters a negative number (e.g., -100) for the field "Full Patient Panel" | System shows validation error.<br>Negative values are not accepted.<br>User should able to Navigate to the Form |
| CBD_TC_024 | Grantee | CBD-SHCP | Performance Reports | Verify Full Patient Panel Field in Form 1: Demographics rejects alphabetic characters | 1. Login as PO/VC<br>2. Navigate to CBD Performance Reports<br>3. Click on "In Progress Reports"<br>4. Click on the Report "CBD-01361"<br>5. Click on "Form1: Demographics"<br><br>User enters alphabetic characters (e.g., "ABC123") for the field "Full Patient Panel" | System shows validation error.<br>Alphabetic characters are not accepted.<br>User should able to Navigate to the Form |
| CBD_TC_025 | Grantee | CBD-SHCP | Performance Reports | Verify Counties Served Field in Form 1: Demographics with boundary value 1999 characters | 1. Login as PO/VC<br>2. Navigate to CBD Performance Reports<br>3. Click on "In Progress Reports"<br>4. Click on the Report "CBD-01361"<br>5. Click on "Form1: Demographics"<br><br>User enters exactly 1999 characters for the field "Counties Served" | Field accepts input with no error.<br>User can add one more character.<br>User should able to Navigate to the Form |
| CBD_TC_026 | Grantee | CBD-SHCP | Performance Reports | Verify Counties Served Field in Form 1: Demographics with empty input | 1. Login as PO/VC<br>2. Navigate to CBD Performance Reports<br>3. Click on "In Progress Reports"<br>4. Click on the Report "CBD-01361"<br>5. Click on "Form1: Demographics"<br><br>User leaves the field "Counties Served" empty or blank | System prompts to select Yes or No.<br>Field behavior follows business rules (required or optional).<br>User should able to Navigate to the Form |
| CBD_TC_027 | Grantee | CBD-SHCP | Performance Reports | Verify Full Patient Panel Field in Form 1: Demographics accepts zero value | 1. Login as PO/VC<br>2. Navigate to CBD Performance Reports<br>3. Click on "In Progress Reports"<br>4. Click on the Report "CBD-01361"<br>5. Click on "Form1: Demographics"<br><br>User enters 0 (zero) for the field "Full Patient Panel" | Field accepts zero as valid input and saves successfully.<br>User should able to Navigate to the Form |
| CBD_TC_028 | Grantee | CBD-SHCP | Performance Reports | Verify Full Patient Panel Field in Form 1: Demographics with leading zeros | 1. Login as PO/VC<br>2. Navigate to CBD Performance Reports<br>3. Click on "In Progress Reports"<br>4. Click on the Report "CBD-01361"<br>5. Click on "Form1: Demographics"<br><br>User enters a number with leading zeros (e.g., 0000123) for the field "Full Patient Panel" | Field accepts input; leading zeros are either stripped or retained.<br>Value is treated as valid whole number.<br>User should able to Navigate to the Form |
| CBD_TC_029 | Grantee | CBD-SHCP | Performance Reports | Verify Form 1: Demographics with all fields at boundary values | 1. Login as PO/VC<br>2. Navigate to CBD Performance Reports<br>3. Click on "In Progress Reports"<br>4. Click on the Report "CBD-01361"<br>5. Click on "Form1: Demographics"<br><br>User enters:<br>- Counties Served: 2000 characters<br>- Full Patient Panel: 9999999999<br>- Target Population: "Yes" | Form accepts all boundary values.<br>Form submits successfully.<br>Data is saved correctly.<br>User should able to Navigate to the Form |
| CBD_TC_030 | Grantee | CBD-SHCP | Performance Reports | Verify Changes to Target Population Measures Field in Form 1: Demographics with no selection | 1. Login as PO/VC<br>2. Navigate to CBD Performance Reports<br>3. Click on "In Progress Reports"<br>4. Click on the Report "CBD-01361"<br>5. Click on "Form1: Demographics"<br><br>User leaves the field "Changes to Target Population Measures" unselected | System prompts to select Yes or No.<br>Form validation follows business requirements.<br>User should able to Navigate to the Form |

---

## Test Case Summary

### Coverage by Field:

**Counties Served Field (Text - 2000 char limit):**
- CBD_TC_010: Valid alphanumeric input ✓
- CBD_TC_011: Maximum 2000 characters ✓
- CBD_TC_012: Exceeds 2000 characters ✗
- CBD_TC_022: Special characters ✓
- CBD_TC_025: Boundary value 1999 characters ✓
- CBD_TC_026: Empty input (edge case)

**Full Patient Panel Field (Numeric - 10 digits max):**
- CBD_TC_013: Valid whole numbers ✓
- CBD_TC_014: Maximum 10 digits ✓
- CBD_TC_015: Decimal values ✗
- CBD_TC_016: More than 10 digits ✗
- CBD_TC_023: Negative numbers ✗
- CBD_TC_024: Alphabetic characters ✗
- CBD_TC_027: Zero value ✓
- CBD_TC_028: Leading zeros (edge case)

**Target Population Measures Field (Dropdown):**
- CBD_TC_017: Displays all options ✓
- CBD_TC_018: Select "Yes" ✓
- CBD_TC_019: Select "No" ✓
- CBD_TC_020: Select "N/A" ✓
- CBD_TC_021: Manual text entry ✗
- CBD_TC_030: No selection (edge case)

**Integration Test:**
- CBD_TC_029: All fields at boundary values ✓

### Test Statistics:
- **Total Test Cases:** 21
- **Positive Tests:** 12
- **Negative Tests:** 6
- **Edge Cases:** 3

### Priority:
All test cases are **High Priority** as they validate critical form field validations per acceptance criteria.

---

## Notes:
- Test Case IDs start from CBD_TC_010 to continue your existing sequence
- All test cases follow your exact format with navigation steps
- Report ID "CBD-01361" is used consistently
- Expected results match your organization's standard phrasing
- All tests assume user is logged in as PO/VC (Grantee role)
