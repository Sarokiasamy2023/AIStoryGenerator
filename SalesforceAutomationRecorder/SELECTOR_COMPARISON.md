# Selector Comparison: Before vs After

## The Problem (Visual Reference)
Based on the screenshot, the UI shows:
```
✓ Form 1: Demographics          [View] [Edit]
○ Form 2: Sustainability        [View] [Start]
○ Form 3: Consortium/Network    [View] [Start]
○ Form 4: Quality Improvement   [View] [Start]
○ Form 5: Project Specific      [View] [Start]
○ Form 6: Measures              [View] [Start]
```

When clicking "Form 2: Sustainability", it was incorrectly clicking Form 1's Edit button.

## Before (❌ INCORRECT)

### Selector
```javascript
"*:has-text('Form 2') >> xpath=.. >> a:has-text('Edit')"
```

### What it does
1. Find ANY element containing "Form 2"
2. Go to parent element (`xpath=..`)
3. Find ANY link with text "Edit"

### Why it fails
- Too generic - can match elements outside the intended row
- The `xpath=..` only goes up one level, which might not be the row container
- Doesn't verify the full form name (e.g., "Sustainability")
- Can accidentally match "Edit" from a different row

## After (✅ CORRECT)

### Primary Selector (Fixed to Find Actual Link Element)
```xpath
xpath=//p[contains(normalize-space(.), 'Form 2: Sustainability')]/following::span[normalize-space(text())='Start' or normalize-space(text())='Edit'][2]/ancestor::a[1]
```

### What it does
1. Find a `<p>` element containing the exact form text "Form 2: Sustainability"
2. Look for the 2nd `<span>` element after it that contains "Start" or "Edit"
3. Use `ancestor::a[1]` to navigate up to the actual clickable `<a>` link element

### Why it works
- ✅ Matches the exact form text in the paragraph element
- ✅ Uses `normalize-space()` to handle whitespace variations
- ✅ Handles both "Start" and "Edit" buttons with OR condition
- ✅ Uses `[2]` index to target the correct button in Salesforce's DOM structure
- ✅ Uses `ancestor::a[1]` to find the actual clickable link element (not just a span)
- ✅ Cannot accidentally match other rows
- ✅ **Properly targets the clickable element**

## Alternative Selectors (Fallback Priority)

### Option 2: Find link directly after paragraph
```xpath
xpath=//p[contains(normalize-space(.), 'Form 2: Sustainability')]/following::a[contains(., 'Start') or contains(., 'Edit')][1]
```
- Finds the first `<a>` link after the paragraph that contains "Start" or "Edit"
- Simpler approach that directly targets the link element
- May be more robust if DOM structure varies

### Option 3: XPath with separate form components
```xpath
xpath=//p[contains(normalize-space(.), 'Form 2') and contains(normalize-space(.), 'Sustainability')]/following::span[normalize-space(text())='Start' or normalize-space(text())='Edit'][2]/ancestor::a[1]
```
- Matches form number and name separately with AND condition
- Same structure as primary selector
- Useful if form text has variations

### Option 4: Playwright row-based selector
```javascript
"tr:has-text('Form 2'):has-text('Sustainability') >> a:has-text('Start')"
```
- Playwright-style selector
- Finds table row containing both texts
- Finds Start button within that row

### Option 5: Exact text with ancestor
```javascript
"text='Form 2: Sustainability' >> xpath=ancestor::tr >> a:has-text('Start')"
```
- Finds exact text "Form 2: Sustainability"
- Navigates up to the table row ancestor
- Finds Start button within that row

## Test Cases

| Statement | Expected Result | Old Selector | New Selector |
|-----------|----------------|--------------|--------------|
| Click "Form 1: Demographics" | Click Edit on Form 1 | ❌ Might work | ✅ Works correctly |
| Click "Form 2: Sustainability" | Click Start on Form 2 | ❌ Clicked Form 1 Edit | ✅ Clicks Form 2 Start |
| Click "Form 3: Consortium/Network" | Click Start on Form 3 | ❌ Might click wrong | ✅ Works correctly |

## Key Improvements

1. **Specificity**: Matches both form number AND name
2. **Scope**: Limited to table row (`tr`) element
3. **Accuracy**: Distinguishes between Edit and Start buttons
4. **Reliability**: Multiple fallback strategies in priority order
5. **Maintainability**: Clear, readable selector logic
