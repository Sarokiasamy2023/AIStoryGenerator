# Test Files Directory

This directory contains sample files for testing the file upload functionality.

## Files

- **sample_document.pdf**: A simple PDF document for testing file uploads

## Usage

These files are referenced in the example tests. You can add your own test files here and reference them in your test steps using relative paths:

```json
{
  "steps": [
    "Upload \"test_files/sample_document.pdf\" to \"Document Field\""
  ]
}
```

## Adding Your Own Files

Simply place any files you want to use for testing in this directory and reference them by their relative path from the project root.
