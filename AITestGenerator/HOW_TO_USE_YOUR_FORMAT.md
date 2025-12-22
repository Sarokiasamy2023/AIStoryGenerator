# How to Use Your CBD-SHCP Test Case Format with AI Test Generator

## 🎯 Quick Start - Generate Test Cases in Your Format

### **Method 1: Use the Template in the UI (5 minutes)**

1. **Start the application:**
   ```bash
   cd AITestGenerator
   npm start
   ```

2. **Open in browser:** http://localhost:3000

3. **Navigate to "User Story → Test Cases" tab**

4. **Enter your user story** in the main text area

5. **Copy and paste the template** into the "Example Test Cases (Optional)" field:

   ```
   Test Case ID: CBD_TC_001
   Test Role: Grantee
   Bureau/Program: CBD-SHCP
   Module/Section: Performance Reports
   Test Case Description: Verify Counties Served Field accepts valid input

   Test Steps:
   1. Login as PO/VC
   2. Navigate to CBD Performance Reports
   3. Click on "In Progress Reports"
   4. Click on the Report "CBD-01361"
   5. Click on "Form1: Demographics"

   User enters valid alphanumeric text in the field "Counties Served"

   Expected Result:
   Field accepts input and saves successfully.
   User should able to Navigate to the Form
   ```

6. **Click "Generate Test Cases"**

7. **AI will generate test cases in your exact format!**

---

## 📁 Files Created for You

### 1. **cbd-shcp-formatted-testcases.md**
   - **21 complete test cases** in your organization's format
   - Ready to copy into your test management tool
   - Covers all three fields with positive, negative, and edge cases

### 2. **cbd-shcp-template.txt**
   - Template file with your format
   - Includes 3 examples (positive, negative, edge)
   - Use this in the "Examples" field of the UI

### 3. **cbd-shcp-test-steps.md**
   - Detailed step-by-step execution instructions
   - 6 fully documented test cases
   - Includes setup and teardown steps

---

## 🎨 Your Test Case Format

### Structure:
```
Test Case ID: CBD_TC_XXX
Test Role: Grantee
Bureau/Program: CBD-SHCP
Module/Section: Performance Reports
Test Case Description: [What is being tested]

Test Steps:
1. Login as PO/VC
2. Navigate to CBD Performance Reports
3. Click on "In Progress Reports"
4. Click on the Report "CBD-01361"
5. Click on "Form1: Demographics"

[User action with the field being tested]

Expected Result:
[Success message or error message]
User should able to Navigate to the Form
```

---

## 📊 Test Cases Generated for Your User Story

### Counties Served Field (Text - 2000 characters)
| Test Case ID | Description | Type |
|--------------|-------------|------|
| CBD_TC_010 | Accepts valid alphanumeric input | Positive |
| CBD_TC_011 | Accepts maximum 2000 characters | Positive |
| CBD_TC_012 | Rejects more than 2000 characters | Negative |
| CBD_TC_022 | Accepts special characters | Positive |
| CBD_TC_025 | Boundary value 1999 characters | Edge |
| CBD_TC_026 | Empty input validation | Edge |

### Full Patient Panel Field (Numeric - 10 digits)
| Test Case ID | Description | Type |
|--------------|-------------|------|
| CBD_TC_013 | Accepts valid whole numbers | Positive |
| CBD_TC_014 | Accepts maximum 10 digits | Positive |
| CBD_TC_015 | Rejects decimal values | Negative |
| CBD_TC_016 | Rejects more than 10 digits | Negative |
| CBD_TC_023 | Rejects negative numbers | Negative |
| CBD_TC_024 | Rejects alphabetic characters | Negative |
| CBD_TC_027 | Accepts zero value | Positive |
| CBD_TC_028 | Leading zeros handling | Edge |

### Target Population Measures Field (Dropdown)
| Test Case ID | Description | Type |
|--------------|-------------|------|
| CBD_TC_017 | Displays all dropdown options | Positive |
| CBD_TC_018 | Select "Yes" option | Positive |
| CBD_TC_019 | Select "No" option | Positive |
| CBD_TC_020 | Select "N/A" option | Positive |
| CBD_TC_021 | Rejects manual text entry | Negative |
| CBD_TC_030 | No selection validation | Edge |

### Integration Test
| Test Case ID | Description | Type |
|--------------|-------------|------|
| CBD_TC_029 | All fields at boundary values | Integration |

**Total: 21 Test Cases**

---

## 🚀 How to Generate More Test Cases

### For New User Stories:

1. **Open the AI Test Generator** (http://localhost:3000)

2. **Enter your new user story**

3. **Paste the template** from `templates/cbd-shcp-template.txt` into the Examples field

4. **Generate** - AI will create test cases in your format

### For Different Forms:

Simply update the template with:
- Different Report ID (instead of "CBD-01361")
- Different Form name (instead of "Form1: Demographics")
- Different field names

Example:
```
Test Steps:
1. Login as PO/VC
2. Navigate to CBD Performance Reports
3. Click on "In Progress Reports"
4. Click on the Report "CBD-02468"
5. Click on "Form2: Clinical Data"

User enters [action for new field]
```

---

## 📋 Copy-Paste Ready Test Cases

### Example: Copy this into Jira/TestRail

```
Test Case ID: CBD_TC_010
Test Role: Grantee
Bureau/Program: CBD-SHCP
Module/Section: Performance Reports

Test Case Description:
Verify Counties Served Field in Form 1: Demographics accepts valid alphanumeric input

Test Steps:
1. Login as PO/VC
2. Navigate to CBD Performance Reports
3. Click on "In Progress Reports"
4. Click on the Report "CBD-01361"
5. Click on "Form1: Demographics"

User enters valid alphanumeric text with spaces and punctuation in the field "Counties Served" (e.g., "Los Angeles, Orange County & San Diego")

Expected Result:
Field accepts input and saves successfully.
User should able to Navigate to the Form
```

---

## 🎯 Validation Rules Covered

### Counties Served Field:
✅ Alphanumeric characters  
✅ Spaces and punctuation  
✅ Maximum 2000 characters  
✅ Error message: "Maximum limit is 2000 characters."  
✅ Special characters (commas, ampersands, hyphens, parentheses)  
✅ Boundary values (1999, 2000, 2001 characters)  

### Full Patient Panel Field:
✅ Whole numbers only  
✅ Up to 10 digits (0 to 9,999,999,999)  
✅ Error message: "Allows whole numbers up to 10 digits."  
✅ Rejects decimals  
✅ Rejects more than 10 digits  
✅ Rejects negative numbers  
✅ Rejects alphabetic characters  
✅ Accepts zero  
✅ Leading zeros handling  

### Target Population Measures Field:
✅ Dropdown with exactly 3 options  
✅ Options: "Yes", "No", "N/A"  
✅ No manual text entry allowed  
✅ Selection persistence  
✅ Required field validation  

---

## 💡 Tips for Your Team

### 1. Consistent Test Case IDs
Start numbering from your last test case. If your last test was CBD_TC_009, start with CBD_TC_010.

### 2. Report ID
Update "CBD-01361" to match your actual report ID in the system.

### 3. Navigation Steps
The first 5 steps are always the same - this ensures consistency across all test cases.

### 4. Expected Results Format
- **Success:** "Field accepts input and saves successfully."
- **Error:** "System shows error: '[exact error message]'"
- **Validation:** "System prompts to select Yes or No."

### 5. Always End With
"User should able to Navigate to the Form"

---

## 📤 Export Options

### To Excel/CSV:
1. Open `cbd-shcp-formatted-testcases.md`
2. Copy the table
3. Paste into Excel
4. Save as CSV

### To Jira:
1. Copy individual test cases
2. Paste into Jira test case fields
3. Map columns to Jira fields

### To TestRail:
1. Use TestRail's CSV import
2. Map columns: Test Case ID → Case ID, Description → Title, etc.

---

## 🎓 Training the AI with Your Format

### Current Approach (Recommended):
Use the template in the "Examples" field - this works immediately and requires no code changes.

### Advanced Approach:
If you want the AI to **always** use your format without pasting the template:

1. **Create permanent template file** (already done):
   - `templates/cbd-shcp-template.txt`

2. **Modify aiService.js** to auto-load your template:
   ```javascript
   // Add at top of aiService.js
   const fs = require('fs');
   const path = require('path');
   
   // In buildTestCasePrompt method
   const templatePath = path.join(__dirname, '../templates/cbd-shcp-template.txt');
   const customTemplate = fs.readFileSync(templatePath, 'utf8');
   ```

3. **Restart server** - all generations now use your format automatically!

---

## ✅ Ready to Use!

You now have:
- ✅ 21 test cases in your exact format
- ✅ Template for generating more
- ✅ Detailed test steps for execution
- ✅ AI tool configured for your format

**Start generating test cases for your other forms and user stories!**

---

## 📞 Need More Test Cases?

Simply:
1. Enter a new user story
2. Paste the template
3. Click Generate
4. Get test cases in your format!

**Happy Testing!** 🎯
