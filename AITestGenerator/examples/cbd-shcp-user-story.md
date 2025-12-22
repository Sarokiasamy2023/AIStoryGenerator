# User Story: CBD-SHCP Program Form Demographics Update

## User Story

**As a** Grantee,  
**I want** the fields in Form 1: Demographics of the CBD-SHCP Program to be updated  
**so that** the system can accept expanded data ranges and additional data formats.

## Acceptance Criteria

### 1. Counties Served – Text Field

- The field "Please specify the names of the counties served." must accept alphanumeric characters (including spaces and punctuation).
- The field must allow up to 2000 characters.
- If the user exceeds the limit, the system must display an error message: "Maximum limit is 2000 characters."

### 2. Full Patient Panel – Numeric Field

- The field "Number of people in the Full Patient Panel" must accept whole numbers only.
- It must accept values up to 10 digits (e.g., 0 to 9,999,999,999).
- If the user enters a decimal value, the system must display an error message: "Allows whole numbers up to 10 digits."
- If the user enters more than 10 digits, the system must show the same error message.

### 3. Target Population Measures – Dropdown

- The field "Changes to Target Population Measures" must be a dropdown list.
- The dropdown must contain only the following three values:
  - Yes
  - No
  - N/A

---

## Generated Test Cases

### POSITIVE TEST CASES

#### TC001: Verify Counties Served field accepts valid alphanumeric input
- **Type:** Positive
- **Priority:** High
- **Module:** Form 1 - Demographics
- **Description:** Verify that the Counties Served field accepts alphanumeric characters with spaces and punctuation
- **Preconditions:**
  - User is logged in as Grantee
  - Form 1: Demographics is accessible
  - Counties Served field is visible and enabled
- **Test Data:**
  - Input: "Los Angeles, Orange County, San Diego & Riverside"
- **Expected Result:** 
  - Input is accepted without error
  - Text is displayed correctly in the field
  - Character count is updated (if visible)

#### TC002: Verify Counties Served field accepts maximum 2000 characters
- **Type:** Positive
- **Priority:** High
- **Module:** Form 1 - Demographics
- **Description:** Verify that the Counties Served field accepts exactly 2000 characters
- **Preconditions:**
  - User is logged in as Grantee
  - Form 1: Demographics is accessible
- **Test Data:**
  - Input: String with exactly 2000 characters (alphanumeric with spaces and punctuation)
- **Expected Result:**
  - All 2000 characters are accepted
  - No error message is displayed
  - Field displays the complete text

#### TC003: Verify Full Patient Panel accepts valid whole numbers
- **Type:** Positive
- **Priority:** High
- **Module:** Form 1 - Demographics
- **Description:** Verify that Full Patient Panel field accepts whole numbers up to 10 digits
- **Preconditions:**
  - User is logged in as Grantee
  - Form 1: Demographics is accessible
- **Test Data:**
  - Input: 1234567890 (10 digits)
- **Expected Result:**
  - Number is accepted without error
  - Value is displayed correctly in the field
  - No decimal places are shown

#### TC004: Verify Full Patient Panel accepts minimum value (0)
- **Type:** Positive
- **Priority:** Medium
- **Module:** Form 1 - Demographics
- **Description:** Verify that Full Patient Panel field accepts zero as valid input
- **Preconditions:**
  - User is logged in as Grantee
  - Form 1: Demographics is accessible
- **Test Data:**
  - Input: 0
- **Expected Result:**
  - Zero is accepted
  - No error message is displayed

#### TC005: Verify Target Population Measures dropdown displays all options
- **Type:** Positive
- **Priority:** High
- **Module:** Form 1 - Demographics
- **Description:** Verify that Target Population Measures dropdown contains all three required values
- **Preconditions:**
  - User is logged in as Grantee
  - Form 1: Demographics is accessible
- **Test Data:**
  - N/A
- **Expected Result:**
  - Dropdown displays exactly three options: "Yes", "No", "N/A"
  - Options are in the correct order
  - All options are selectable

#### TC006: Verify selecting "Yes" in Target Population Measures dropdown
- **Type:** Positive
- **Priority:** High
- **Module:** Form 1 - Demographics
- **Description:** Verify that user can select "Yes" from Target Population Measures dropdown
- **Preconditions:**
  - User is logged in as Grantee
  - Form 1: Demographics is accessible
- **Test Data:**
  - Selection: "Yes"
- **Expected Result:**
  - "Yes" is selected and displayed in the dropdown
  - Selection is saved when form is submitted

#### TC007: Verify Counties Served accepts special characters
- **Type:** Positive
- **Priority:** Medium
- **Module:** Form 1 - Demographics
- **Description:** Verify that Counties Served field accepts various punctuation marks
- **Preconditions:**
  - User is logged in as Grantee
  - Form 1: Demographics is accessible
- **Test Data:**
  - Input: "County A, County B; County C & County D - County E (Region 1)"
- **Expected Result:**
  - All special characters are accepted
  - Text is displayed correctly with all punctuation intact

---

### NEGATIVE TEST CASES

#### TC008: Verify Counties Served field rejects input exceeding 2000 characters
- **Type:** Negative
- **Priority:** High
- **Module:** Form 1 - Demographics
- **Description:** Verify that Counties Served field displays error when input exceeds 2000 characters
- **Preconditions:**
  - User is logged in as Grantee
  - Form 1: Demographics is accessible
- **Test Data:**
  - Input: String with 2001 characters
- **Expected Result:**
  - Error message is displayed: "Maximum limit is 2000 characters."
  - Input is not accepted beyond 2000 characters OR field is truncated at 2000 characters
  - Form cannot be submitted with error present

#### TC009: Verify Full Patient Panel rejects decimal values
- **Type:** Negative
- **Priority:** High
- **Module:** Form 1 - Demographics
- **Description:** Verify that Full Patient Panel field displays error when decimal value is entered
- **Preconditions:**
  - User is logged in as Grantee
  - Form 1: Demographics is accessible
- **Test Data:**
  - Input: 123.45
- **Expected Result:**
  - Error message is displayed: "Allows whole numbers up to 10 digits."
  - Decimal value is not accepted
  - Form cannot be submitted with error present

#### TC010: Verify Full Patient Panel rejects values exceeding 10 digits
- **Type:** Negative
- **Priority:** High
- **Module:** Form 1 - Demographics
- **Description:** Verify that Full Patient Panel field displays error when value exceeds 10 digits
- **Preconditions:**
  - User is logged in as Grantee
  - Form 1: Demographics is accessible
- **Test Data:**
  - Input: 12345678901 (11 digits)
- **Expected Result:**
  - Error message is displayed: "Allows whole numbers up to 10 digits."
  - Value exceeding 10 digits is not accepted
  - Form cannot be submitted with error present

#### TC011: Verify Full Patient Panel rejects negative numbers
- **Type:** Negative
- **Priority:** High
- **Module:** Form 1 - Demographics
- **Description:** Verify that Full Patient Panel field rejects negative values
- **Preconditions:**
  - User is logged in as Grantee
  - Form 1: Demographics is accessible
- **Test Data:**
  - Input: -100
- **Expected Result:**
  - Negative value is rejected
  - Error message is displayed (validation error)
  - Form cannot be submitted

#### TC012: Verify Full Patient Panel rejects alphabetic characters
- **Type:** Negative
- **Priority:** High
- **Module:** Form 1 - Demographics
- **Description:** Verify that Full Patient Panel field rejects non-numeric input
- **Preconditions:**
  - User is logged in as Grantee
  - Form 1: Demographics is accessible
- **Test Data:**
  - Input: "ABC123"
- **Expected Result:**
  - Alphabetic characters are not accepted
  - Field remains empty or shows validation error
  - Error message is displayed

#### TC013: Verify Full Patient Panel rejects special characters
- **Type:** Negative
- **Priority:** Medium
- **Module:** Form 1 - Demographics
- **Description:** Verify that Full Patient Panel field rejects special characters
- **Preconditions:**
  - User is logged in as Grantee
  - Form 1: Demographics is accessible
- **Test Data:**
  - Input: "123@#$"
- **Expected Result:**
  - Special characters are not accepted
  - Only numeric portion (if any) is retained or field shows error
  - Validation error is displayed

#### TC014: Verify Target Population Measures dropdown does not accept manual text entry
- **Type:** Negative
- **Priority:** Medium
- **Module:** Form 1 - Demographics
- **Description:** Verify that Target Population Measures dropdown only accepts predefined values
- **Preconditions:**
  - User is logged in as Grantee
  - Form 1: Demographics is accessible
- **Test Data:**
  - Attempt: Try to type "Maybe" or any custom text
- **Expected Result:**
  - Manual text entry is not possible
  - Only dropdown selection is allowed
  - Field remains empty or shows previous selection

---

### EDGE CASE TEST CASES

#### TC015: Verify Counties Served field with exactly 1999 characters
- **Type:** Edge
- **Priority:** Medium
- **Module:** Form 1 - Demographics
- **Description:** Verify behavior when Counties Served field contains 1999 characters (one below limit)
- **Preconditions:**
  - User is logged in as Grantee
  - Form 1: Demographics is accessible
- **Test Data:**
  - Input: String with exactly 1999 characters
- **Expected Result:**
  - All 1999 characters are accepted
  - No error message is displayed
  - User can add one more character

#### TC016: Verify Counties Served field with empty input
- **Type:** Edge
- **Priority:** Medium
- **Module:** Form 1 - Demographics
- **Description:** Verify behavior when Counties Served field is left empty
- **Preconditions:**
  - User is logged in as Grantee
  - Form 1: Demographics is accessible
- **Test Data:**
  - Input: Empty/blank
- **Expected Result:**
  - Field accepts empty value OR displays required field error (based on business rules)
  - Form submission behavior follows business requirements

#### TC017: Verify Counties Served field with only spaces
- **Type:** Edge
- **Priority:** Low
- **Module:** Form 1 - Demographics
- **Description:** Verify behavior when Counties Served field contains only whitespace
- **Preconditions:**
  - User is logged in as Grantee
  - Form 1: Demographics is accessible
- **Test Data:**
  - Input: "     " (multiple spaces)
- **Expected Result:**
  - System either accepts spaces OR trims and treats as empty
  - Validation behavior is consistent with business rules

#### TC018: Verify Full Patient Panel with maximum valid value (9,999,999,999)
- **Type:** Edge
- **Priority:** High
- **Module:** Form 1 - Demographics
- **Description:** Verify that Full Patient Panel accepts the maximum 10-digit value
- **Preconditions:**
  - User is logged in as Grantee
  - Form 1: Demographics is accessible
- **Test Data:**
  - Input: 9999999999
- **Expected Result:**
  - Maximum value is accepted
  - No error message is displayed
  - Value is stored and displayed correctly

#### TC019: Verify Full Patient Panel with leading zeros
- **Type:** Edge
- **Priority:** Low
- **Module:** Form 1 - Demographics
- **Description:** Verify behavior when Full Patient Panel has leading zeros
- **Preconditions:**
  - User is logged in as Grantee
  - Form 1: Demographics is accessible
- **Test Data:**
  - Input: 0000123
- **Expected Result:**
  - Leading zeros are either stripped (displays as 123) OR accepted as is
  - Value is treated as valid whole number
  - No error message is displayed

#### TC020: Verify Target Population Measures dropdown with no selection
- **Type:** Edge
- **Priority:** Medium
- **Module:** Form 1 - Demographics
- **Description:** Verify behavior when Target Population Measures dropdown is not selected
- **Preconditions:**
  - User is logged in as Grantee
  - Form 1: Demographics is accessible
- **Test Data:**
  - Action: Leave dropdown unselected
- **Expected Result:**
  - Form either accepts empty dropdown OR displays required field error
  - Validation follows business requirements

#### TC021: Verify form behavior with all fields at boundary values
- **Type:** Edge
- **Priority:** High
- **Module:** Form 1 - Demographics
- **Description:** Verify form submission with all fields at their maximum/boundary values
- **Preconditions:**
  - User is logged in as Grantee
  - Form 1: Demographics is accessible
- **Test Data:**
  - Counties Served: 2000 characters
  - Full Patient Panel: 9999999999
  - Target Population Measures: "Yes"
- **Expected Result:**
  - Form accepts all boundary values
  - Form submits successfully
  - Data is saved correctly in the system

#### TC022: Verify Counties Served with Unicode characters
- **Type:** Edge
- **Priority:** Low
- **Module:** Form 1 - Demographics
- **Description:** Verify behavior when Counties Served contains Unicode/international characters
- **Preconditions:**
  - User is logged in as Grantee
  - Form 1: Demographics is accessible
- **Test Data:**
  - Input: "São Paulo, Zürich, Москва, 北京"
- **Expected Result:**
  - Unicode characters are either accepted OR rejected with clear error
  - System behavior is consistent and documented

#### TC023: Verify Full Patient Panel with copy-paste of formatted number
- **Type:** Edge
- **Priority:** Medium
- **Module:** Form 1 - Demographics
- **Description:** Verify behavior when formatted number is pasted into Full Patient Panel
- **Preconditions:**
  - User is logged in as Grantee
  - Form 1: Demographics is accessible
- **Test Data:**
  - Input: "1,234,567" (with commas) pasted from clipboard
- **Expected Result:**
  - System either strips formatting and accepts 1234567 OR rejects with error
  - Behavior is consistent and user-friendly

---

## Test Summary

- **Total Test Cases:** 23
- **Positive:** 7
- **Negative:** 7
- **Edge Cases:** 9

## Priority Breakdown

- **High Priority:** 14 test cases
- **Medium Priority:** 7 test cases
- **Low Priority:** 2 test cases

## Coverage

✅ Counties Served field - Character limits, special characters, boundary values  
✅ Full Patient Panel field - Numeric validation, digit limits, data types  
✅ Target Population Measures - Dropdown functionality, value restrictions  
✅ Form-level validations and integrations  
✅ Error message validations  
✅ Edge cases and boundary conditions
