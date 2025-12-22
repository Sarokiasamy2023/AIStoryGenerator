# Textarea Troubleshooting Guide

## Common Issue: Unable to Enter Text in LWC Textarea

### Problem Description
Salesforce Lightning Web Component (LWC) textareas often have:
- Dynamic IDs (e.g., `textareaId-360`)
- Dynamic `lwc-` attributes
- `slds-textarea` class
- Nested in `div.slds-form-element__control`
- Label text above the field (not always in a `<label>` tag)

### Solution

#### Step 1: Identify the Label Text
Look at the text above or near the textarea. For example:
- "*Please specify the names of the counties served."
- "Comments"
- "Description"

#### Step 2: Use the Label Text in Your Test
```json
{
  "steps": [
    "Fill textarea \"Please specify the names of the counties served\" with \"Your text here\""
  ]
}
```

#### Step 3: If Full Label Doesn't Work, Use Partial Text
```json
{
  "steps": [
    "Fill textarea \"counties served\" with \"Your text here\""
  ]
}
```

## How the System Finds Your Textarea

The framework tries multiple strategies in order:

### 1. Direct Attribute Matching
- `textarea.slds-textarea[aria-label='your-label']`
- `textarea.slds-textarea[placeholder='your-label']`

### 2. Lightning Component Selectors
- `lightning-textarea[data-label='your-label'] >> textarea`
- `lightning-textarea >> textarea[aria-label='your-label']`

### 3. XPath with normalize-space (HIGHEST PRIORITY - Most Reliable)
- `xpath=//*[normalize-space(text())='your-label']//following::textarea[1]`
- `xpath=//*[contains(normalize-space(text()), 'your-label')]//following::textarea[1]`

**Why normalize-space?** It handles whitespace variations (spaces, tabs, newlines) that are common in Salesforce HTML.

### 4. Label-Based Selectors (Fallback)
- `*:has-text('your-label') >> xpath=following-sibling::div >> textarea`
- `*:has-text('your-label') >> xpath=following::textarea.slds-textarea[1]`
- `div.slds-form-element:has-text('your-label') >> textarea`

### 4. Fallback
- `textarea.slds-textarea` (finds any SLDS textarea)

## How the System Fills the Textarea

The framework tries 3 strategies automatically:

### Strategy 1: Standard Playwright Fill
```javascript
await element.click();
await element.fill('');
await element.fill(value);
```

### Strategy 2: Character-by-Character Typing
```javascript
await element.click();
await page.keyboard.press('Control+A');
await page.keyboard.press('Backspace');
await element.type(value, delay=10);
```

### Strategy 3: JavaScript Injection with LWC Events
```javascript
el.value = "your text";
el.focus();
el.dispatchEvent(new Event("input", { bubbles: true, composed: true }));
el.dispatchEvent(new Event("change", { bubbles: true, composed: true }));
el.dispatchEvent(new Event("blur", { bubbles: true, composed: true }));
el.dispatchEvent(new CustomEvent("valuechange", { 
    detail: { value: el.value },
    bubbles: true,
    composed: true
}));
```

## Special Handling

### Readonly/Disabled Fields
The system automatically detects and removes readonly/disabled attributes:
```javascript
if (is_readonly) {
    el.readOnly = false;
    el.setAttribute("aria-readonly", "false");
}
if (is_disabled) {
    el.disabled = false;
}
```

### Long Labels
For labels longer than 30 characters, the system uses partial matching:
```javascript
text=/Please specify the names/i >> xpath=following::textarea[1]
```

## Example Test Cases

### Example 1: Full Label Text
```json
{
  "test_name": "Counties Form - Full Label",
  "steps": [
    "Wait for 2 seconds",
    "Fill textarea \"Please specify the names of the counties served\" with \"El Dorado County, Sacramento County, Placer County\"",
    "Wait for 1 second",
    "Click \"Next\""
  ]
}
```

### Example 2: Partial Label Text
```json
{
  "test_name": "Counties Form - Partial Label",
  "steps": [
    "Wait for 2 seconds",
    "Fill textarea \"counties served\" with \"El Dorado County, Sacramento County\"",
    "Wait for 1 second",
    "Click \"Next\""
  ]
}
```

### Example 3: Generic Field Name
```json
{
  "test_name": "Comments Field",
  "steps": [
    "Fill textarea \"Comments\" with \"This is my comment text\""
  ]
}
```

## Debugging Tips

### Check the Logs
The system provides detailed logging:
- ✅ `Found upload button: button:has-text('Upload Files')`
- ✅ `Filled textarea "counties served" with: El Dorado County...`
- ⚠️ `Standard fill failed: ..., trying alternative method`
- ⚠️ `Textarea is readonly, attempting to remove readonly attribute`
- ❌ `Could not find textarea: counties served`

### If Textarea Still Not Found

1. **Check the exact label text** - Copy it from the UI
2. **Try a shorter version** - Use just the distinctive part
3. **Check for special characters** - Remove asterisks (*) or other symbols
4. **Use the fallback** - If there's only one textarea on the page, use a generic name

### If Textarea Found But Fill Fails

The system tries 3 strategies automatically. Check the logs to see which one succeeded or if all failed.

Common reasons for failure:
- JavaScript framework preventing input
- Field is truly disabled/readonly
- Custom validation blocking input
- Shadow DOM isolation (rare in Salesforce)

## Quick Reference

| Scenario | Test Step Example |
|----------|------------------|
| Full label text | `Fill textarea "Please specify the names of the counties served" with "Text"` |
| Partial label | `Fill textarea "counties served" with "Text"` |
| Short label | `Fill textarea "Comments" with "Text"` |
| Generic (single textarea) | `Fill textarea "Description" with "Text"` |

## Need More Help?

See the main guide: `UPLOAD_AND_TEXTAREA_GUIDE.md`

For general test syntax: `QUICK_START.md`
