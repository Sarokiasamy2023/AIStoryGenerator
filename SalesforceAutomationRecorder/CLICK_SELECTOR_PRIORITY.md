# Click Selector Priority Guide

## Issue: Clicking Wrong Element

### Problem
When clicking "Recently Viewed", the system was clicking on:
```html
<element aria-label='Recently Viewed'>
```

Instead of the visible text element:
```html
<span class="slds-page-header__title slds-truncate lst-temp-slds-lineHeight">Recently Viewed</span>
```

### Root Cause
The `[aria-label='Recently Viewed']` selector had higher priority than visible text selectors.

## Solution: Updated Selector Priority

The system now prioritizes **visible text elements** over **aria-label attributes**.

## New Click Selector Priority Order

### 1. Buttons and Links (Highest Priority)
```python
button:has-text('Recently Viewed')
a:has-text('Recently Viewed')
lightning-button:has-text('Recently Viewed')
```

### 2. XPath with normalize-space (HIGHEST PRIORITY)
```python
# Specific element types (most reliable)
xpath=//span[normalize-space(.)='Recently Viewed']
xpath=//div[normalize-space(.)='Recently Viewed']
xpath=//a[normalize-space(.)='Recently Viewed']
xpath=//button[normalize-space(.)='Recently Viewed']

# Generic (any element)
xpath=//*[normalize-space(.)='Recently Viewed' and not(self::script) and not(self::style)]
```

**Why `.` instead of `text()`?**
- `.` gets all text content including from child elements
- `text()` only gets direct text nodes
- More reliable for complex HTML structures

### 3. Visible Text in Salesforce Elements
```python
# Salesforce page headers
span.slds-page-header__title:has-text('Recently Viewed')
span.slds-truncate:has-text('Recently Viewed')

# Headings
h1:has-text('Recently Viewed')
h2:has-text('Recently Viewed')
```

### 3. List Items and Menu Items
```python
li:has-text('Recently Viewed')
[role='option']:has-text('Recently Viewed')
[role='menuitem']:has-text('Recently Viewed')
[role='listitem']:has-text('Recently Viewed')
```

### 4. Salesforce List View Items
```python
a[title='Recently Viewed']
span[title='Recently Viewed']
```

### 5. Generic Text Matches
```python
text='Recently Viewed'
text=/Recently Viewed/i
span:has-text('Recently Viewed')
div:has-text('Recently Viewed')
```

### 6. Attribute Selectors (Lower Priority)
```python
[title='Recently Viewed']
[aria-label='Recently Viewed']  # NOW LOWER PRIORITY
[data-label='Recently Viewed']
```

### 7. Generic Fallback (Lowest Priority)
```python
*:has-text('Recently Viewed')
```

## Why This Order?

### Visible Text First
- ✅ Matches what users see and interact with
- ✅ More intuitive and predictable
- ✅ Aligns with user expectations
- ✅ Better for accessibility testing

### Aria-Label Later
- ⚠️ Often on container elements, not the actual clickable element
- ⚠️ May match multiple elements
- ⚠️ Not always the element users interact with
- ⚠️ Can be on parent/wrapper elements

## Examples

### Example 1: Recently Viewed
```json
{
  "steps": [
    "Click \"Recently Viewed\""
  ]
}
```

**Old Behavior:**
- Clicked: `<div aria-label="Recently Viewed">` (container)

**New Behavior:**
- Clicks: `<span class="slds-page-header__title">Recently Viewed</span>` (visible text)

### Example 2: Page Headers
```json
{
  "steps": [
    "Click \"Accounts\""
  ]
}
```

**Selector Priority:**
1. `button:has-text('Accounts')` - if it's a button
2. `span.slds-page-header__title:has-text('Accounts')` - if it's a header
3. `text='Accounts'` - generic text match
4. `[aria-label='Accounts']` - fallback to aria-label

### Example 3: Navigation Items
```json
{
  "steps": [
    "Click \"Opportunities\""
  ]
}
```

**Selector Priority:**
1. `a:has-text('Opportunities')` - if it's a link
2. `li:has-text('Opportunities')` - if it's a list item
3. `span:has-text('Opportunities')` - if it's a span
4. `[aria-label='Opportunities']` - fallback

## Special Salesforce Selectors

### Page Header Titles
```python
span.slds-page-header__title:has-text('target')
```
Matches Salesforce Lightning page headers like "Recently Viewed", "Accounts", etc.

### Truncated Text
```python
span.slds-truncate:has-text('target')
```
Matches text that may be truncated with ellipsis.

### XPath with normalize-space
```python
xpath=//*[normalize-space(text())='target' and not(self::script) and not(self::style)]
```
- Exact text match with whitespace normalization
- Excludes script and style tags
- Works for any element type

## Debugging

### Check Which Selector Was Used
Look for this in the logs:
```
INFO: Found element using selector: span.slds-page-header__title:has-text('Recently Viewed')
```

### If Wrong Element is Clicked
1. Check the logs to see which selector matched
2. If it's still using aria-label, the visible text element might not exist
3. Try using a more specific selector in your test:
   ```json
   "Click \"span.slds-page-header__title:has-text('Recently Viewed')\""
   ```

## Browser DevTools Testing

Test selectors in browser console:

### Test Visible Text Selector
```javascript
document.querySelector("span.slds-page-header__title")
```

### Test Aria-Label Selector
```javascript
document.querySelector("[aria-label='Recently Viewed']")
```

### Test XPath
```javascript
$x("//*[normalize-space(text())='Recently Viewed' and not(self::script) and not(self::style)]")
```

## Best Practices

### For Test Writers
1. ✅ Use the visible text users see: `Click "Recently Viewed"`
2. ✅ Trust the selector priority - it will find the right element
3. ⚠️ Only use specific selectors if the default doesn't work

### For Developers
1. ✅ Ensure visible text is clickable (not just containers)
2. ✅ Use semantic HTML (buttons for buttons, links for links)
3. ✅ Avoid putting aria-labels on non-interactive elements

## Migration

### No Action Required!
Existing tests will automatically use the new selector priority.

### If Tests Break
If a test that was working now fails:
1. Check if the element structure changed
2. The old selector might have been clicking the wrong element (but it worked)
3. Update the test to click the correct element

## Performance

- **No performance impact**: Selectors are tried in order until one matches
- **Faster in most cases**: Visible text selectors often match first
- **More reliable**: Clicking visible elements is more stable

## Conclusion

This change makes the framework:
- ✅ More intuitive (clicks what users see)
- ✅ More reliable (visible elements are more stable)
- ✅ Better aligned with user expectations
- ✅ Easier to debug (logs show which visible element was clicked)

The system now prioritizes **visible text** over **aria-label attributes** for click actions.
