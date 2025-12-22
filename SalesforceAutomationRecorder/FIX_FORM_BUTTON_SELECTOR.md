# Fix: Form Button Selector Issue

## Problem
When using the statement "Click Form 2: Sustainability", the automation was incorrectly clicking on "Form 1: Demographics Edit" button instead of "Form 2: Sustainability Start" button.

## Root Cause
The previous selector was too generic:
```
*:has-text('Form 2') >> xpath=.. >> a:has-text('Edit')
```

This selector only matched "Form 2" text and then looked for any Edit/Start button in the parent element. This caused it to match the wrong row when multiple forms were present.

## Solution
Updated the selector generation logic to use a **user-verified XPath** that works on the actual Salesforce page:

### New Selector Strategy (Priority Order)
1. **HIGHEST PRIORITY**: XPath to find the actual clickable link element
   ```xpath
   //p[contains(normalize-space(.), 'Form 2: Sustainability')]/following::span[normalize-space(text())='Start' or normalize-space(text())='Edit'][2]/ancestor::a[1]
   ```
   
   **How it works:**
   - Finds the `<p>` element containing the exact form text "Form 2: Sustainability"
   - Locates the 2nd `<span>` element after it that contains "Start" or "Edit"
   - Uses `ancestor::a[1]` to navigate up to the actual clickable `<a>` link element
   - The `[2]` index ensures we get the correct button in the row structure

2. **Alternative**: Find link directly after paragraph
   ```xpath
   //p[contains(normalize-space(.), 'Form 2: Sustainability')]/following::a[contains(., 'Start') or contains(., 'Edit')][1]
   ```
   
3. **Alternative**: Match with form components separately
   ```xpath
   //p[contains(normalize-space(.), 'Form 2') and contains(normalize-space(.), 'Sustainability')]/following::span[normalize-space(text())='Start' or normalize-space(text())='Edit'][2]/ancestor::a[1]
   ```

4. **Fallback**: Playwright row-based selector
   ```
   tr:has-text('Form 2'):has-text('Sustainability') >> a:has-text('Start')
   ```

## Files Modified

### 1. `enhanced_test_executor.py` (Lines 547-571)
- Updated selector generation logic for form actions
- Added multiple selector strategies that match both form number and name
- Prioritized row-based selectors to ensure correct button is clicked

### 2. `test_learning.json`
When form selectors are learned, they will now use the verified XPath format:

**Example for Form 2: Sustainability:**
```json
{
  "form_2:_sustainability": {
    "selector": "xpath=//p[contains(normalize-space(.), 'Form 2: Sustainability')]/following::span[normalize-space(text())='Start' or normalize-space(text())='Edit'][2]/ancestor::a[1]",
    "target": "Form 2: Sustainability",
    "action": "click"
  }
}
```

## How It Works
The new XPath selector ensures precision by:
1. Finding the `<p>` element containing the exact form text (e.g., "Form 2: Sustainability")
2. Looking for the 2nd `<span>` element following it that contains "Start" or "Edit" text
3. Using `ancestor::a[1]` to navigate up to the actual clickable `<a>` link element
4. The `[2]` index accounts for the Salesforce DOM structure where multiple spans exist

This approach:
- ✅ Matches the exact form by full text
- ✅ Handles both "Start" and "Edit" buttons dynamically
- ✅ Uses `ancestor::a[1]` to find the actual clickable link element (not just a span)
- ✅ Uses the correct index to target the right button in the row
- ✅ Prevents clicking buttons from other form rows

## Testing
To test the fix, use these statements:
- `Click "Form 1: Demographics"` → Should click Edit button on Form 1 row
- `Click "Form 2: Sustainability"` → Should click Start button on Form 2 row
- `Click "Form 3: Consortium/Network"` → Should click Start button on Form 3 row

## Benefits
- ✅ More precise element targeting
- ✅ Prevents clicking wrong form buttons
- ✅ Works with both "Edit" and "Start" buttons
- ✅ Handles all form variations (Form 1-6)
- ✅ More robust against UI changes

## Enhanced Click Strategies (Added)

When clicking on elements like `//div[normalize-space(.)='OAT Performance Reports']`, the system now uses **4 fallback click strategies** to handle difficult-to-click elements:

### Click Strategy Priority Order:
1. **Standard Playwright Click** - Default click method
2. **JavaScript Click** - Uses `element.click()` via JavaScript when standard click fails
3. **Force Click** - Ignores actionability checks (visibility, stability, etc.)
4. **Dispatch Click Event** - Manually dispatches a MouseEvent when all else fails

### Enhanced Selector Strategies:
Added XPath selectors to find clickable parent elements:
- `xpath=//div[normalize-space(.)='OAT Performance Reports']/ancestor::a[1]` - Finds clickable link parent
- `xpath=//div[normalize-space(.)='OAT Performance Reports']/ancestor::button[1]` - Finds clickable button parent
- `xpath=//span[normalize-space(.)='OAT Performance Reports']/ancestor::a[1]` - Finds link parent of span
- `xpath=//span[normalize-space(.)='OAT Performance Reports']/ancestor::button[1]` - Finds button parent of span

These strategies ensure that even if the text is in a non-clickable `<div>` or `<span>`, the system will find and click the actual clickable parent element.
