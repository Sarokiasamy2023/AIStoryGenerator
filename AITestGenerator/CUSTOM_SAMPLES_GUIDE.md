# Using Your Own Samples to Guide AI Generation

This guide shows you how to use your own user stories, test cases, and test steps to customize the AI output for your specific use case.

## 🎯 Three Methods to Use Your Samples

### **Method 1: Use the Examples Field (Easiest - No Code Changes)**

The UI already has "Examples" fields where you can paste your samples.

#### Step 1: Prepare Your Test Case Template

Create a file: `my-test-case-template.txt`

```
TC001: Verify user can login successfully
- Type: Positive
- Priority: P0
- Module: Authentication
- Description: Validate that registered user can login with valid credentials
- Preconditions:
  * User account exists in database
  * User is on login page
  * Browser is Chrome v120+
- Test Data:
  * Username: testuser@mycompany.com
  * Password: SecurePass123!
- Expected Result: User is redirected to dashboard within 2 seconds
- Post-conditions: User session is created

TC002: Verify login fails with invalid password
- Type: Negative
- Priority: P0
- Module: Authentication
- Description: Validate error handling for incorrect password
- Preconditions:
  * User account exists
  * User is on login page
- Test Data:
  * Username: testuser@mycompany.com
  * Password: WrongPassword123
- Expected Result: Error message "Invalid credentials" displayed
- Post-conditions: Login attempt logged in audit table
```

#### Step 2: Prepare Your Test Steps Template

Create a file: `my-test-steps-template.txt`

```
Setup Steps:
1. Launch Chrome browser in incognito mode
2. Clear all cookies and cache
3. Navigate to https://myapp.com
4. Verify application is loaded (check page title)

Test Steps:

Step 1: Navigate to Login Page
- Action: Click on "Login" button in top navigation
- Test Data: N/A
- Expected Result: Login page is displayed with URL /auth/login
- Actual Result: [To be filled during execution]
- Status: [Pass/Fail]

Step 2: Enter Username
- Action: Type username in "Email" input field
- Test Data: testuser@mycompany.com
- Expected Result: Username is displayed in the field
- Actual Result: [To be filled during execution]
- Status: [Pass/Fail]

Step 3: Enter Password
- Action: Type password in "Password" input field
- Test Data: SecurePass123!
- Expected Result: Password is masked with dots
- Actual Result: [To be filled during execution]
- Status: [Pass/Fail]

Step 4: Submit Login Form
- Action: Click "Sign In" button
- Test Data: N/A
- Expected Result: Loading spinner appears briefly
- Actual Result: [To be filled during execution]
- Status: [Pass/Fail]

Step 5: Verify Dashboard Access
- Action: Wait for page load and verify URL
- Test Data: N/A
- Expected Result: Dashboard page loads with URL /dashboard
- Actual Result: [To be filled during execution]
- Status: [Pass/Fail]

Teardown Steps:
1. Logout from application
2. Close browser
3. Clear test data from database
```

#### Step 3: Use in the UI

1. Open the application: http://localhost:3000
2. Go to "User Story → Test Cases" tab
3. Enter your user story
4. In the **"Example Test Cases (Optional)"** field, paste your template
5. Click "Generate Test Cases"

The AI will follow your format!

---

### **Method 2: Create Template Files (Recommended for Teams)**

Create permanent template files that are automatically loaded.

#### Step 1: Create Template Files

Create these files in the project root:

**File: `templates/test-case-template.txt`**
```
[Paste your test case format here - same as Method 1]
```

**File: `templates/test-steps-template.txt`**
```
[Paste your test steps format here - same as Method 1]
```

#### Step 2: Create Template Loader

Create: `services/templateLoader.js`

```javascript
const fs = require('fs');
const path = require('path');

class TemplateLoader {
    constructor() {
        this.templatesDir = path.join(__dirname, '../templates');
        this.testCaseTemplate = null;
        this.testStepsTemplate = null;
        this.loadTemplates();
    }

    loadTemplates() {
        try {
            // Load test case template
            const testCasePath = path.join(this.templatesDir, 'test-case-template.txt');
            if (fs.existsSync(testCasePath)) {
                this.testCaseTemplate = fs.readFileSync(testCasePath, 'utf8');
                console.log('✓ Custom test case template loaded');
            }

            // Load test steps template
            const testStepsPath = path.join(this.templatesDir, 'test-steps-template.txt');
            if (fs.existsSync(testStepsPath)) {
                this.testStepsTemplate = fs.readFileSync(testStepsPath, 'utf8');
                console.log('✓ Custom test steps template loaded');
            }
        } catch (error) {
            console.error('Error loading templates:', error);
        }
    }

    getTestCaseTemplate() {
        return this.testCaseTemplate;
    }

    getTestStepsTemplate() {
        return this.testStepsTemplate;
    }
}

module.exports = new TemplateLoader();
```

#### Step 3: Modify aiService.js

Add this at the top of `services/aiService.js`:

```javascript
const templateLoader = require('./templateLoader');
```

Then modify the `buildTestCasePrompt` method (around line 43):

```javascript
buildTestCasePrompt(userStory, examples) {
    // Load custom template if available
    const customTemplate = templateLoader.getTestCaseTemplate();
    const examplesText = examples || customTemplate || '';
    
    let prompt = `You are an expert QA engineer. Convert the following user story into comprehensive test cases.

Generate test cases for:
1. **Positive Scenarios**: Happy path, expected behavior
2. **Negative Scenarios**: Invalid inputs, error conditions
3. **Edge Cases**: Boundary conditions, unusual but valid scenarios

User Story:
${userStory}
`;

    if (examplesText) {
        prompt += `\nIMPORTANT: Follow this EXACT format for test cases:\n${examplesText}\n`;
    }

    // ... rest of the method
}
```

Similarly for `buildTestStepsPrompt` method.

---

### **Method 3: Fine-Tune OpenAI Model (Advanced)**

For the most customized results, you can fine-tune the OpenAI model with your examples.

#### Requirements:
- OpenAI API access
- At least 10-50 example pairs
- JSONL format training data

#### Step 1: Prepare Training Data

Create: `training-data.jsonl`

```jsonl
{"messages": [{"role": "system", "content": "You are a QA engineer generating test cases."}, {"role": "user", "content": "User Story: As a user, I want to login..."}, {"role": "assistant", "content": "TC001: Verify login with valid credentials\n- Type: Positive\n- Priority: P0..."}]}
{"messages": [{"role": "system", "content": "You are a QA engineer generating test cases."}, {"role": "user", "content": "User Story: As a user, I want to add items to cart..."}, {"role": "assistant", "content": "TC001: Verify adding item to empty cart\n- Type: Positive\n- Priority: P0..."}]}
```

#### Step 2: Fine-Tune via OpenAI

```bash
# Upload training file
openai api fine_tuning.jobs.create \
  -t training-data.jsonl \
  -m gpt-3.5-turbo

# Get your fine-tuned model ID
# e.g., ft:gpt-3.5-turbo:my-org:custom-model:abc123
```

#### Step 3: Update .env

```env
OPENAI_MODEL=ft:gpt-3.5-turbo:my-org:custom-model:abc123
```

---

## 📝 Sample Template Formats

### Your Company's Test Case Format

If your company uses a specific format, create a template like this:

```
Test Case ID: TC-AUTH-001
Module: Authentication
Feature: User Login
Type: Functional - Positive
Priority: Critical
Severity: High

Test Case Title: Verify successful login with valid credentials

Objective: 
To validate that a registered user can successfully login to the application using valid email and password credentials.

Preconditions:
1. User account exists in the system
2. User is not currently logged in
3. Application is accessible
4. Test environment is stable

Test Data:
- Email: testuser@company.com
- Password: Test@12345
- Browser: Chrome 120+
- OS: Windows 11

Test Steps:
[See test steps section]

Expected Result:
- User is successfully authenticated
- User is redirected to dashboard page
- Welcome message displays user's name
- Session token is created
- Login timestamp is recorded

Actual Result:
[To be filled during execution]

Status: Not Executed
Executed By: [Tester Name]
Execution Date: [Date]
Build Version: [Version]
Comments: [Any observations]
```

### Your Company's Test Steps Format

```
Test Case: TC-AUTH-001
Test Steps for: Verify successful login with valid credentials

Environment Setup:
- Browser: Chrome 120.0.6099.130
- Environment: QA
- Base URL: https://qa.myapp.com
- Database: QA_DB_v2.3

Pre-requisites:
✓ Test user account created
✓ Browser cache cleared
✓ VPN connected to QA network

Execution Steps:

┌─────────────────────────────────────────────────────────────┐
│ Step 1: Launch Application                                  │
├─────────────────────────────────────────────────────────────┤
│ Action: Open Chrome and navigate to base URL               │
│ Input: https://qa.myapp.com                                 │
│ Expected: Homepage loads with login button visible          │
│ Actual: [To be filled]                                      │
│ Screenshot: [Attach if failed]                              │
│ Status: □ Pass  □ Fail  □ Blocked                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Step 2: Navigate to Login                                   │
├─────────────────────────────────────────────────────────────┤
│ Action: Click "Login" button in header                      │
│ Input: N/A                                                   │
│ Expected: Login form appears with email and password fields │
│ Actual: [To be filled]                                      │
│ Screenshot: [Attach if failed]                              │
│ Status: □ Pass  □ Fail  □ Blocked                          │
└─────────────────────────────────────────────────────────────┘

[Continue for all steps...]

Post-Execution:
- Logout performed: Yes/No
- Test data cleaned: Yes/No
- Defects logged: [Defect IDs if any]

Test Summary:
- Total Steps: 8
- Passed: [Count]
- Failed: [Count]
- Blocked: [Count]
- Overall Result: Pass/Fail
```

---

## 🚀 Quick Implementation

### Option A: Use UI Examples Field (5 minutes)

1. Copy your test case format
2. Paste in "Example Test Cases" field
3. Generate
4. Done!

### Option B: Create Template Files (15 minutes)

1. Create `templates/` folder
2. Add your template files
3. Create `templateLoader.js`
4. Modify `aiService.js` to use templates
5. Restart server
6. All generations now use your format!

### Option C: Fine-Tune Model (2-3 days)

1. Collect 50+ examples
2. Format as JSONL
3. Submit to OpenAI
4. Wait for training
5. Update model ID
6. Perfect customization!

---

## 💡 Pro Tips

### 1. Start with Method 1
Test with the UI examples field first to see if the format works.

### 2. Be Specific
The more detailed your template, the better the AI matches it.

### 3. Include Multiple Examples
Provide 2-3 examples covering different scenarios.

### 4. Use Consistent Terminology
If you use "Pre-requisites" instead of "Preconditions", be consistent.

### 5. Test and Iterate
Generate a few times and refine your template based on results.

---

## 📊 Comparison

| Method | Setup Time | Consistency | Cost | Best For |
|--------|-----------|-------------|------|----------|
| UI Examples | 5 min | Good | Free | Quick testing |
| Template Files | 15 min | Excellent | Free | Team use |
| Fine-Tuning | 2-3 days | Perfect | $$$ | Enterprise |

---

## 🎯 Next Steps

1. **Prepare your samples** - Gather 2-3 examples of your format
2. **Choose a method** - Start with Method 1 or 2
3. **Test it out** - Generate a few test cases
4. **Refine** - Adjust your template based on results
5. **Share with team** - Document your custom format

---

**Need help?** Share your test case format and I can help you create the perfect template!
