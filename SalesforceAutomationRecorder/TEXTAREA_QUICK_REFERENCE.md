# Textarea Quick Reference

## ✅ YES - All These Syntaxes Work!

### For Your Specific Case: "Please specify the names of the counties served."

```json
// Option 1: Standard Type syntax (RECOMMENDED - Simplest)
"Type \"Loudoun\" into \"Please specify the names of the counties served.\""

// Option 2: Shorter label text
"Type \"Loudoun\" into \"counties served\""

// Option 3: Explicit textarea syntax
"Fill textarea \"Please specify the names of the counties served\" with \"Loudoun\""

// Option 4: Explicit textarea with shorter label
"Fill textarea \"counties served\" with \"Loudoun\""
```

## How It Works

### Auto-Detection
When you use `Type "value" into "Field Name"`, the system:
1. ✅ Finds the element using the label text
2. ✅ Checks if it's a `<textarea>` element
3. ✅ If yes, automatically uses enhanced textarea strategies
4. ✅ If no, uses standard input fill

### Enhanced Textarea Strategies
When a textarea is detected, the system automatically:
1. ✅ Removes readonly/disabled attributes if needed
2. ✅ Tries 3 fill methods:
   - Standard Playwright fill
   - Character-by-character typing
   - JavaScript value injection with LWC events
3. ✅ Dispatches proper events for LWC reactivity

## Selector Strategies

The `fill` action now searches for both inputs AND textareas:

```javascript
// Input selectors
input[placeholder='your-label']
lightning-input[data-label='your-label'] >> input
label:has-text('your-label') >> xpath=following::input[1]

// Textarea selectors (automatically included)
textarea.slds-textarea[placeholder='your-label']
textarea[aria-label='your-label']
*:has-text('your-label') >> xpath=following::textarea.slds-textarea[1]
div.slds-form-element:has-text('your-label') >> textarea
```

## Examples

### Simple Case
```json
{
  "steps": [
    "Type \"Loudoun\" into \"counties served\""
  ]
}
```

### With Multiple Counties
```json
{
  "steps": [
    "Type \"Loudoun, Fairfax, Arlington\" into \"counties served\""
  ]
}
```

### Full Label Text
```json
{
  "steps": [
    "Type \"Loudoun County\" into \"Please specify the names of the counties served.\""
  ]
}
```

### Explicit Textarea Syntax
```json
{
  "steps": [
    "Fill textarea \"counties served\" with \"Loudoun, Fairfax\""
  ]
}
```

## Key Takeaway

**You don't need to specify "textarea" in the command!** 

Just use the standard `Type "value" into "Field Name"` syntax, and the system will automatically detect if it's a textarea and handle it appropriately.

## Debugging

If it's not working, check the logs for:
- `Detected textarea element, using enhanced fill strategies` ✅
- `Filled textarea counties served with: Loudoun` ✅
- `Standard fill failed: ..., trying type method` ⚠️
- `Could not find element: counties served` ❌

If you see "Could not find element", try:
1. Using the full label text
2. Using a shorter, distinctive part
3. Checking for typos or special characters
