# File Upload and Textarea Guide

This guide explains how to use the new file upload and textarea functionality in the Salesforce Automation Recorder.

## File Upload

### Syntax Options

```
Upload "path/to/file.pdf" to "Document Upload"
Upload file "path/to/file.pdf" to "Attachment Field"
Upload "C:\Documents\resume.pdf"
```

### Examples

#### Example 1: Upload with Field Label
```json
{
  "test_name": "Upload Document Test",
  "steps": [
    "Click \"Upload Documents\"",
    "Upload \"test_files/sample.pdf\" to \"Resume Upload\"",
    "Click \"Submit\""
  ]
}
```

#### Example 2: Upload with Absolute Path
```json
{
  "test_name": "Upload Image Test",
  "steps": [
    "Click \"Add Attachment\"",
    "Upload file \"C:\\Users\\Documents\\photo.jpg\" to \"Profile Picture\"",
    "Wait for 2 seconds",
    "Click \"Save\""
  ]
}
```

#### Example 3: Upload with Relative Path
```json
{
  "test_name": "Bulk Upload Test",
  "steps": [
    "Click \"Import Data\"",
    "Upload \"data/customers.csv\" to \"CSV File\"",
    "Click \"Process\""
  ]
}
```

#### Example 4: Upload Files Button (Common in Salesforce)
For UIs with an "Upload Files" button that opens a file chooser:
```json
{
  "test_name": "File Attachments Upload",
  "steps": [
    "Wait for 2 seconds",
    "Upload \"test_files/sample_document.pdf\" to \"Upload Files\"",
    "Wait for 2 seconds",
    "Click \"Next\""
  ]
}
```
**Note**: The system automatically detects "Upload Files" buttons and handles the file chooser dialog.

### How It Works

1. **Path Resolution**: The system automatically converts relative paths to absolute paths based on the current working directory
2. **File Validation**: Checks if the file exists before attempting upload
3. **Two-Strategy Approach**:
   - **Strategy 1 (Button-based)**: Looks for "Upload Files" or "Upload" buttons, clicks them, and handles the file chooser dialog
   - **Strategy 2 (Direct input)**: If no button found, directly finds and fills the file input element
4. **Smart Element Finding**: Uses multiple strategies to locate upload elements:
   - By button text matching "Upload Files", "Upload", or custom target
   - By aria-label matching the target field name
   - By name/id containing the field name
   - By label text followed by file input
   - Generic `input[type="file"]` as fallback

### Supported File Types

All file types are supported as long as the web application accepts them:
- Documents: `.pdf`, `.doc`, `.docx`, `.txt`
- Images: `.jpg`, `.png`, `.gif`, `.svg`
- Data: `.csv`, `.xlsx`, `.json`, `.xml`
- Archives: `.zip`, `.rar`

---

## Textarea

### Syntax Options

**Option 1: Explicit Textarea Syntax**
```
Type "long text content" into textarea "Description"
Fill textarea "Comments" with "This is a multi-line comment"
```

**Option 2: Standard Type/Fill Syntax (Auto-detects Textareas)**
```
Type "long text content" into "Description"
Fill "Comments" with "This is a multi-line comment"
```

**Note**: Both syntaxes work! The system automatically detects if the target element is a textarea and uses enhanced fill strategies with LWC event dispatching.

### Examples

#### Example 1: Fill Textarea with Description
```json
{
  "test_name": "Case Creation Test",
  "steps": [
    "Click \"New Case\"",
    "Type \"John Doe\" into \"Customer Name\"",
    "Fill textarea \"Description\" with \"Customer reported issue with login functionality. Unable to access account after password reset.\"",
    "Click \"Save\""
  ]
}
```

#### Example 2: Multi-line Content
```json
{
  "test_name": "Feedback Form Test",
  "steps": [
    "Click \"Submit Feedback\"",
    "Type \"Product Review\" into \"Subject\"",
    "Type \"Great product! Works as expected. Would recommend to others.\" into textarea \"Comments\"",
    "Click \"Submit\""
  ]
}
```

#### Example 3: Long Text Entry
```json
{
  "test_name": "Notes Entry Test",
  "steps": [
    "Click \"Add Notes\"",
    "Fill textarea \"Meeting Notes\" with \"Discussed Q4 objectives. Key points: 1) Increase sales by 20%, 2) Launch new product line, 3) Expand to new markets.\"",
    "Click \"Save Notes\""
  ]
}
```

#### Example 4: Textarea with Long Label (Salesforce LWC)
For textareas with long label text like "*Please specify the names of the counties served.":

**Using standard Type syntax (Recommended - simpler):**
```json
{
  "test_name": "Counties Form - Standard Syntax",
  "steps": [
    "Wait for 2 seconds",
    "Type \"Loudoun\" into \"Please specify the names of the counties served.\"",
    "Click \"Next\""
  ]
}
```

**Using explicit textarea syntax:**
```json
{
  "test_name": "Counties Form - Explicit Syntax",
  "steps": [
    "Wait for 2 seconds",
    "Fill textarea \"Please specify the names of the counties served\" with \"El Dorado County, Sacramento County\"",
    "Click \"Next\""
  ]
}
```

**Using shorter label text:**
```json
{
  "steps": [
    "Type \"Loudoun\" into \"counties served\""
  ]
}
```

**All three syntaxes work!** The system automatically detects textareas and applies enhanced fill strategies.

### How It Works

1. **Element Detection**: Specifically looks for `<textarea>` elements
2. **Smart Selector Generation**: Uses multiple strategies in priority order:
   - **XPath with normalize-space()** (HIGHEST PRIORITY - handles whitespace variations)
     - `xpath=//*[normalize-space(text())='label']//following::textarea[1]`
   - By placeholder text
   - By aria-label
   - By name/id attributes
   - By associated label text
3. **Content Handling**:
   - Clicks to focus the textarea
   - Clears existing content
   - Fills with new content
4. **Validation**: Warns if the element is not actually a textarea but attempts to fill anyway

---

## Complete Test Example

Here's a complete test that uses both file upload and textarea:

```json
{
  "test_name": "Job Application Submission",
  "url": "https://your-salesforce-instance.lightning.force.com/lightning/o/Job_Application__c/new",
  "steps": [
    "Wait for 2 seconds",
    "Type \"Jane Smith\" into \"Applicant Name\"",
    "Type \"jane.smith@email.com\" into \"Email\"",
    "Type \"555-0123\" into \"Phone\"",
    "Select \"Software Engineer\" from Dropdown \"Position\"",
    "Fill textarea \"Cover Letter\" with \"I am excited to apply for this position. I have 5 years of experience in software development and am proficient in Python, JavaScript, and cloud technologies.\"",
    "Upload \"documents/resume.pdf\" to \"Resume Upload\"",
    "Upload \"documents/portfolio.pdf\" to \"Portfolio\"",
    "Check \"Terms and Conditions\"",
    "Click \"Submit Application\"",
    "Verify \"Application Submitted Successfully\" is visible"
  ]
}
```

---

## Tips and Best Practices

### File Upload
- ✅ **Use relative paths** for portability (e.g., `test_files/document.pdf`)
- ✅ **Verify file exists** before running tests
- ✅ **Use descriptive field names** that match the UI labels
- ⚠️ **Wait after upload** if the application processes the file asynchronously
- ⚠️ **Check file size limits** of the target application

### Textarea
- ✅ **Use specific field names** to avoid ambiguity
- ✅ **Keep text readable** in test files (use escape sequences for special characters if needed)
- ✅ **Test with various text lengths** to ensure proper handling
- ⚠️ **Be aware of character limits** in the target field
- ⚠️ **Consider line breaks** - the framework handles them automatically

### Error Handling
Both features include comprehensive error handling:
- File not found errors
- Element not found errors
- Upload failures
- Fill operation failures

Check the test execution logs for detailed error messages if something goes wrong.

---

## Troubleshooting

### File Upload Issues

**Problem**: "File not found" error
- **Solution**: Check the file path is correct and the file exists
- **Solution**: Use absolute paths if relative paths aren't working

**Problem**: "Could not find file input element"
- **Solution**: Verify the field name matches the UI label exactly
- **Solution**: Try using a more generic target like "file upload" or "upload"

**Problem**: Upload succeeds but file doesn't appear
- **Solution**: Add a wait step after upload to allow processing time
- **Solution**: Check if the application requires additional confirmation

### Textarea Issues

**Problem**: "Could not find textarea"
- **Solution**: Verify the field name matches the label in the UI
- **Solution**: Check if it's actually a textarea or a rich text editor (which may need different handling)
- **Solution**: For LWC textareas without labels, use a generic target like "Comments" or "Description"

**Problem**: Text is truncated
- **Solution**: Check the character limit of the field
- **Solution**: Verify no special characters are causing issues

**Problem**: Element found but fill fails (especially with LWC textareas)
- **Solution**: The system now tries 3 strategies automatically:
  1. Standard Playwright fill
  2. Character-by-character typing
  3. Direct JavaScript value injection
- **Solution**: Add a small wait before the fill operation
- **Solution**: The system automatically handles readonly/disabled attributes

**Problem**: Lightning Web Component (LWC) textarea not responding
- **Solution**: The framework now specifically targets `textarea.slds-textarea` elements
- **Solution**: Uses event dispatching to trigger LWC change detection
- **Solution**: Automatically removes readonly attributes if needed

---

## Advanced Usage

### Multiple File Uploads
```json
{
  "steps": [
    "Upload \"file1.pdf\" to \"Document 1\"",
    "Wait for 1 second",
    "Upload \"file2.pdf\" to \"Document 2\"",
    "Wait for 1 second",
    "Upload \"file3.pdf\" to \"Document 3\""
  ]
}
```

### Dynamic File Paths
You can use environment variables or generate file paths programmatically in your test setup.

### Textarea with Special Characters
The framework handles special characters automatically, but for complex formatting, ensure your JSON is properly escaped:
```json
{
  "steps": [
    "Fill textarea \"Notes\" with \"Line 1\\nLine 2\\nLine 3\""
  ]
}
```

---

## API Reference

### Upload Action
- **Action**: `upload`
- **Required**: `file_path` (string)
- **Optional**: `target` (string, defaults to "file upload")
- **Returns**: `True` on success, `False` on failure

### Textarea Action
- **Action**: `textarea`
- **Required**: `target` (string), `value` (string)
- **Returns**: `True` on success, `False` on failure
