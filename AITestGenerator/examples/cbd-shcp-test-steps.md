# Detailed Test Steps for CBD-SHCP Program Form

## TC001: Verify Counties Served field accepts valid alphanumeric input

### Setup Steps
1. Open supported browser (Chrome, Firefox, Edge)
2. Navigate to CBD-SHCP application URL
3. Login with valid Grantee credentials
4. Verify successful login and dashboard is displayed
5. Navigate to Form 1: Demographics

### Test Steps

**Step 1: Locate Counties Served field**
- **Action:** Scroll to the "Counties Served" section in Form 1
- **Test Data:** N/A
- **Expected Result:** Field labeled "Please specify the names of the counties served." is visible and enabled

**Step 2: Click on Counties Served text field**
- **Action:** Click inside the Counties Served text field to activate it
- **Test Data:** N/A
- **Expected Result:** 
  - Field is focused (cursor appears)
  - Field border highlights (if applicable)
  - Character counter displays "0/2000" (if visible)

**Step 3: Enter alphanumeric text with spaces**
- **Action:** Type county names with spaces
- **Test Data:** "Los Angeles, Orange County, San Diego"
- **Expected Result:**
  - Text is entered successfully
  - All characters including spaces and commas are accepted
  - Text is displayed correctly in the field

**Step 4: Add punctuation marks**
- **Action:** Continue typing to add more punctuation
- **Test Data:** Add " & Riverside"
- **Expected Result:**
  - Ampersand (&) is accepted
  - Complete text reads: "Los Angeles, Orange County, San Diego & Riverside"
  - Character count updates (if visible)

**Step 5: Verify no error message is displayed**
- **Action:** Check for any error messages below or near the field
- **Test Data:** N/A
- **Expected Result:**
  - No error message is displayed
  - Field border remains normal (not red)
  - No validation warnings appear

**Step 6: Tab out of the field**
- **Action:** Press Tab key or click outside the field
- **Test Data:** N/A
- **Expected Result:**
  - Field loses focus
  - Entered text remains in the field
  - No validation errors appear

**Step 7: Verify data persistence**
- **Action:** Click back into the field
- **Test Data:** N/A
- **Expected Result:**
  - Previously entered text is still present
  - Cursor appears at the end of text or where clicked

### Teardown Steps
1. Clear the Counties Served field
2. Logout from the application
3. Close browser

---

## TC008: Verify Counties Served field rejects input exceeding 2000 characters

### Setup Steps
1. Open supported browser
2. Navigate to CBD-SHCP application URL
3. Login with valid Grantee credentials
4. Navigate to Form 1: Demographics
5. Prepare a text string with exactly 2001 characters in a text editor

### Test Steps

**Step 1: Locate Counties Served field**
- **Action:** Navigate to the Counties Served field in Form 1
- **Test Data:** N/A
- **Expected Result:** Field is visible and enabled

**Step 2: Copy 2001-character text**
- **Action:** Copy the prepared 2001-character string to clipboard
- **Test Data:** String with 2001 characters (alphanumeric with spaces)
- **Expected Result:** Text is copied to clipboard successfully

**Step 3: Paste text into Counties Served field**
- **Action:** Click in the field and paste (Ctrl+V or right-click > Paste)
- **Test Data:** 2001-character string
- **Expected Result:** 
  - One of the following occurs:
    a) Only first 2000 characters are pasted, OR
    b) All 2001 characters are pasted but error appears

**Step 4: Verify error message is displayed**
- **Action:** Observe the field and surrounding area for error messages
- **Test Data:** N/A
- **Expected Result:**
  - Error message is displayed: "Maximum limit is 2000 characters."
  - Error message appears below the field or in a prominent location
  - Error message is in red or error styling

**Step 5: Verify field visual indication**
- **Action:** Check the field border and styling
- **Test Data:** N/A
- **Expected Result:**
  - Field border turns red or shows error state
  - Field may have error icon or indicator
  - Character counter (if present) shows "2001/2000" or similar

**Step 6: Attempt to submit form**
- **Action:** Click the Submit or Save button
- **Test Data:** N/A
- **Expected Result:**
  - Form submission is blocked
  - Error message persists or is highlighted
  - Focus returns to the Counties Served field

**Step 7: Reduce text to 2000 characters**
- **Action:** Delete 1 character from the field
- **Test Data:** Remove 1 character to make it exactly 2000
- **Expected Result:**
  - Error message disappears
  - Field border returns to normal
  - Character counter shows "2000/2000"

**Step 8: Verify form can now be submitted**
- **Action:** Click Submit or Save button
- **Test Data:** N/A
- **Expected Result:**
  - Form submission is allowed
  - No error messages appear
  - Success message or next page is displayed

### Teardown Steps
1. Verify data was saved (if form submitted)
2. Clear test data from the system
3. Logout from application
4. Close browser

---

## TC009: Verify Full Patient Panel rejects decimal values

### Setup Steps
1. Open supported browser
2. Navigate to CBD-SHCP application URL
3. Login with valid Grantee credentials
4. Navigate to Form 1: Demographics

### Test Steps

**Step 1: Locate Full Patient Panel field**
- **Action:** Scroll to the "Full Patient Panel" section
- **Test Data:** N/A
- **Expected Result:** Field labeled "Number of people in the Full Patient Panel" is visible

**Step 2: Click on Full Patient Panel field**
- **Action:** Click inside the numeric field
- **Test Data:** N/A
- **Expected Result:**
  - Field is focused
  - Cursor appears in the field
  - Field is ready for input

**Step 3: Enter decimal value**
- **Action:** Type a number with decimal places
- **Test Data:** 123.45
- **Expected Result:** One of the following occurs:
  - a) Decimal point is not accepted (only "12345" appears), OR
  - b) Decimal is accepted but validation error appears

**Step 4: Tab out or click outside field**
- **Action:** Press Tab key or click outside the field to trigger validation
- **Test Data:** N/A
- **Expected Result:**
  - Field validation is triggered
  - Error message appears

**Step 5: Verify error message content**
- **Action:** Read the error message displayed
- **Test Data:** N/A
- **Expected Result:**
  - Error message states: "Allows whole numbers up to 10 digits."
  - Message is displayed below the field or in error area
  - Message is styled as error (red text or error icon)

**Step 6: Verify field visual state**
- **Action:** Observe the field styling
- **Test Data:** N/A
- **Expected Result:**
  - Field border is red or shows error state
  - Error icon may appear next to field
  - Field value may be highlighted

**Step 7: Attempt to submit form with error**
- **Action:** Click Submit or Save button
- **Test Data:** N/A
- **Expected Result:**
  - Form submission is prevented
  - Error message remains visible or is highlighted
  - User is notified to correct the error

**Step 8: Clear the field**
- **Action:** Select all text and delete, or clear the field
- **Test Data:** N/A
- **Expected Result:**
  - Field is cleared
  - Error message may disappear or remain until valid input

**Step 9: Enter valid whole number**
- **Action:** Type a valid whole number
- **Test Data:** 12345
- **Expected Result:**
  - Number is accepted
  - Error message disappears
  - Field border returns to normal

**Step 10: Verify form can be submitted**
- **Action:** Click Submit or Save button
- **Test Data:** N/A
- **Expected Result:**
  - Form submits successfully
  - No error messages
  - Success confirmation is displayed

### Teardown Steps
1. Clear test data if needed
2. Logout from application
3. Close browser

---

## TC010: Verify Full Patient Panel rejects values exceeding 10 digits

### Setup Steps
1. Open supported browser
2. Navigate to CBD-SHCP application URL
3. Login with valid Grantee credentials
4. Navigate to Form 1: Demographics

### Test Steps

**Step 1: Navigate to Full Patient Panel field**
- **Action:** Locate and click on the "Number of people in the Full Patient Panel" field
- **Test Data:** N/A
- **Expected Result:** Field is focused and ready for input

**Step 2: Enter 11-digit number**
- **Action:** Type an 11-digit number
- **Test Data:** 12345678901
- **Expected Result:** One of the following:
  - a) Only first 10 digits are accepted (12345678901 becomes 1234567890), OR
  - b) All 11 digits are entered but validation error appears

**Step 3: Trigger field validation**
- **Action:** Press Tab or click outside the field
- **Test Data:** N/A
- **Expected Result:**
  - Validation is triggered
  - Error state is activated

**Step 4: Verify error message**
- **Action:** Check for error message near the field
- **Test Data:** N/A
- **Expected Result:**
  - Error message displays: "Allows whole numbers up to 10 digits."
  - Message is clearly visible
  - Message is styled as error

**Step 5: Verify character limit enforcement**
- **Action:** Try to type additional digits
- **Test Data:** Try adding more digits
- **Expected Result:**
  - Additional digits are not accepted if limit is enforced at input level
  - Field remains at maximum allowed length

**Step 6: Test with copy-paste of 11-digit number**
- **Action:** Clear field, copy 11-digit number, and paste
- **Test Data:** 98765432109 (pasted)
- **Expected Result:**
  - Either truncated to 10 digits OR full number pasted with error
  - Error message appears
  - Validation prevents form submission

**Step 7: Attempt form submission**
- **Action:** Click Submit button while error is present
- **Test Data:** N/A
- **Expected Result:**
  - Form does not submit
  - Error is highlighted
  - User is prompted to fix the error

**Step 8: Correct to valid 10-digit number**
- **Action:** Edit the field to contain exactly 10 digits
- **Test Data:** 1234567890
- **Expected Result:**
  - Error message disappears
  - Field returns to normal state
  - Form can be submitted

### Teardown Steps
1. Clear the field or reset form
2. Logout from application
3. Close browser

---

## TC018: Verify Full Patient Panel with maximum valid value (9,999,999,999)

### Setup Steps
1. Open supported browser
2. Navigate to CBD-SHCP application URL
3. Login with valid Grantee credentials
4. Navigate to Form 1: Demographics

### Test Steps

**Step 1: Navigate to Full Patient Panel field**
- **Action:** Click on the "Number of people in the Full Patient Panel" field
- **Test Data:** N/A
- **Expected Result:** Field is active and ready for input

**Step 2: Enter maximum 10-digit value**
- **Action:** Type the maximum allowed value
- **Test Data:** 9999999999
- **Expected Result:**
  - All 10 digits are entered successfully
  - Field displays: 9999999999 (or formatted as 9,999,999,999)
  - No error appears during entry

**Step 3: Verify character count**
- **Action:** Count the digits in the field
- **Test Data:** N/A
- **Expected Result:**
  - Exactly 10 digits are present
  - No truncation has occurred

**Step 4: Tab out of field**
- **Action:** Press Tab key to move to next field
- **Test Data:** N/A
- **Expected Result:**
  - Field validation passes
  - No error message appears
  - Field border remains normal (not red)

**Step 5: Verify no error message**
- **Action:** Check below and around the field for any error messages
- **Test Data:** N/A
- **Expected Result:**
  - No error message is displayed
  - No warning messages appear
  - Field is in valid state

**Step 6: Click back into field to verify value**
- **Action:** Click back into the Full Patient Panel field
- **Test Data:** N/A
- **Expected Result:**
  - Value 9999999999 is still present
  - No data loss occurred
  - Cursor appears in the field

**Step 7: Fill remaining required fields**
- **Action:** Complete other required fields in the form
- **Test Data:**
  - Counties Served: "Test County"
  - Target Population Measures: "Yes"
- **Expected Result:**
  - All fields accept valid data
  - No errors on any field

**Step 8: Submit the form**
- **Action:** Click Submit or Save button
- **Test Data:** N/A
- **Expected Result:**
  - Form submits successfully
  - Success message is displayed
  - No validation errors occur

**Step 9: Verify data persistence**
- **Action:** Navigate back to the form or reload the page
- **Test Data:** N/A
- **Expected Result:**
  - Full Patient Panel field shows 9999999999
  - Value was saved correctly in the database
  - No data corruption or truncation

### Teardown Steps
1. Delete or archive the test record
2. Clear test data from database
3. Logout from application
4. Close browser

---

## TC005: Verify Target Population Measures dropdown displays all options

### Setup Steps
1. Open supported browser
2. Navigate to CBD-SHCP application URL
3. Login with valid Grantee credentials
4. Navigate to Form 1: Demographics

### Test Steps

**Step 1: Locate Target Population Measures dropdown**
- **Action:** Scroll to the "Changes to Target Population Measures" field
- **Test Data:** N/A
- **Expected Result:**
  - Dropdown field is visible
  - Field is labeled "Changes to Target Population Measures"
  - Field appears as a dropdown (down arrow visible)

**Step 2: Click on the dropdown**
- **Action:** Click on the dropdown field or the dropdown arrow
- **Test Data:** N/A
- **Expected Result:**
  - Dropdown menu expands
  - List of options is displayed
  - Dropdown is fully visible (not cut off)

**Step 3: Verify "Yes" option is present**
- **Action:** Look for "Yes" in the dropdown list
- **Test Data:** N/A
- **Expected Result:**
  - "Yes" option is visible in the list
  - Text is clearly readable
  - Option is selectable (not disabled)

**Step 4: Verify "No" option is present**
- **Action:** Look for "No" in the dropdown list
- **Test Data:** N/A
- **Expected Result:**
  - "No" option is visible in the list
  - Text is clearly readable
  - Option is selectable (not disabled)

**Step 5: Verify "N/A" option is present**
- **Action:** Look for "N/A" in the dropdown list
- **Test Data:** N/A
- **Expected Result:**
  - "N/A" option is visible in the list
  - Text is clearly readable
  - Option is selectable (not disabled)

**Step 6: Verify only three options exist**
- **Action:** Count the total number of options in the dropdown
- **Test Data:** N/A
- **Expected Result:**
  - Exactly 3 options are present
  - No additional options exist
  - No duplicate options

**Step 7: Verify option order**
- **Action:** Note the order of options from top to bottom
- **Test Data:** N/A
- **Expected Result:**
  - Options appear in order: "Yes", "No", "N/A" (or as per requirements)
  - Order is consistent with specifications

**Step 8: Select "Yes" option**
- **Action:** Click on "Yes" in the dropdown
- **Test Data:** Selection: "Yes"
- **Expected Result:**
  - "Yes" is selected
  - Dropdown closes
  - Selected value "Yes" is displayed in the field

**Step 9: Reopen dropdown and select "No"**
- **Action:** Click dropdown again and select "No"
- **Test Data:** Selection: "No"
- **Expected Result:**
  - Previous selection changes to "No"
  - Dropdown closes
  - "No" is now displayed in the field

**Step 10: Reopen dropdown and select "N/A"**
- **Action:** Click dropdown again and select "N/A"
- **Test Data:** Selection: "N/A"
- **Expected Result:**
  - Selection changes to "N/A"
  - Dropdown closes
  - "N/A" is displayed in the field

**Step 11: Verify selection persistence**
- **Action:** Click outside the dropdown and then click back on it
- **Test Data:** N/A
- **Expected Result:**
  - Last selected value ("N/A") is still displayed
  - Selection persists
  - Dropdown still shows all three options

### Teardown Steps
1. Clear the form or reset selections
2. Logout from application
3. Close browser

---

## Test Execution Notes

### Environment Requirements
- **Browsers:** Chrome (latest), Firefox (latest), Edge (latest)
- **Screen Resolution:** 1920x1080 or higher
- **Network:** Stable internet connection
- **User Role:** Grantee with form access permissions

### Test Data Requirements
- Valid Grantee login credentials
- Access to Form 1: Demographics
- Text editor for preparing 2000+ character strings
- Calculator for verifying 10-digit numbers

### Common Issues to Watch For
1. Browser auto-fill interfering with test data
2. Copy-paste formatting issues
3. Network latency affecting validation timing
4. Browser-specific validation behavior differences

### Reporting
- Screenshot all error messages
- Note exact error message text
- Record browser and version for any failures
- Document any unexpected behavior
