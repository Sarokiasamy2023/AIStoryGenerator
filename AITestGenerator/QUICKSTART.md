# Quick Start Guide

Get up and running with AI Test Generator in 5 minutes!

## ⚡ Fast Setup

### 1. Install Dependencies (1 minute)

```bash
cd AITestGenerator
npm install
```

### 2. Configure API Key (1 minute)

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

**Don't have an API key?** Get one at: https://platform.openai.com/api-keys

### 3. Start the Server (30 seconds)

```bash
npm start
```

You should see:
```
🚀 AI Test Generator Server running on http://localhost:3000
📝 Open http://localhost:3000 in your browser
```

### 4. Open in Browser (30 seconds)

Navigate to: **http://localhost:3000**

### 5. Try a Sample (2 minutes)

1. Click **"View Samples"** button in the header
2. Click **"Use This Sample"** on the Login Feature
3. Click **"Generate Test Cases"**
4. Wait 10-20 seconds
5. Review the generated test cases! 🎉

## 🎯 Your First Generation

### Generate Test Cases from User Story

**Example User Story:**
```
Title: User Login Feature

User Story:
As a registered user, I want to log in to my account 
so that I can access my personalized dashboard.

Acceptance Criteria:
- User can log in with valid email and password
- System displays error for invalid credentials
- Account locks after 5 failed attempts
```

**What You'll Get:**
- ✅ 3-5 Positive test cases (happy path)
- ❌ 3-5 Negative test cases (error scenarios)
- 🔄 2-3 Edge cases (boundary conditions)

### Generate Test Steps from Test Case

**Example Test Case:**
```
ID: TC001
Title: Verify successful login with valid credentials
Type: Positive
Priority: High
Description: Verify that a user can successfully log in 
with valid email and password
```

**What You'll Get:**
- 🔧 Setup steps (preconditions)
- 📝 Detailed test steps with:
  - Action to perform
  - Test data to use
  - Expected result
- 🧹 Teardown steps (cleanup)

## 📊 Understanding the Output

### Test Case Structure

```
TC001: Verify successful login with valid credentials
├── Type: Positive
├── Priority: High
├── Description: Full description of what to test
├── Preconditions: 
│   ├── User account exists
│   └── User is on login page
└── Expected Result: User is redirected to dashboard
```

### Test Steps Structure

```
Step 1: Navigate to login page
├── Action: Open browser and go to login URL
├── Test Data: URL: https://example.com/login
└── Expected Result: Login page is displayed

Step 2: Enter credentials
├── Action: Enter email and password
├── Test Data: Email: test@example.com, Password: Test@123
└── Expected Result: Credentials are entered successfully
```

## 🎨 UI Overview

### Main Tabs

1. **User Story → Test Cases**
   - Input: User story text
   - Output: Comprehensive test cases

2. **Test Case → Test Steps**
   - Input: Test case details
   - Output: Detailed test steps

3. **History**
   - View all previous generations
   - Re-load and export

### Key Features

- 🎯 **Generate Button**: Creates test cases/steps using AI
- 💾 **Export CSV**: Download results for use in other tools
- 📚 **View Samples**: Pre-built examples to learn from
- 🔄 **Generate Steps**: Quick link from test case to steps

## 💡 Pro Tips

### 1. Better User Stories = Better Test Cases

**Good:**
```
As a customer, I want to add items to my cart 
so that I can purchase multiple items at once.

Acceptance Criteria:
- User can add items from product page
- Cart displays total price
- Maximum 10 items per product
```

**Not as Good:**
```
User should be able to add to cart
```

### 2. Use Examples for Consistency

If you have a specific format you want, provide 1-2 examples in the "Examples" field.

### 3. Review and Refine

AI is smart but not perfect:
- ✅ Review generated content
- ✅ Adjust priorities as needed
- ✅ Add domain-specific details
- ✅ Verify test data is realistic

### 4. Export and Integrate

Export to CSV and import into:
- Jira
- TestRail
- Azure DevOps
- Excel/Google Sheets
- Your test management tool

## 🔧 Common Adjustments

### Change AI Model

In `.env`:
```env
# For faster, cheaper responses
OPENAI_MODEL=gpt-4o-mini

# For best quality (default)
OPENAI_MODEL=gpt-4o
```

### Adjust Creativity

In `.env`:
```env
# More consistent (0.0 - 0.5)
TEMPERATURE=0.3

# More creative (0.6 - 1.0)
TEMPERATURE=0.8
```

### Change Port

In `.env`:
```env
PORT=3001
```

Then access at: http://localhost:3001

## 📱 Workflow Examples

### Workflow 1: New Feature Testing

1. Product owner writes user story
2. Paste into AI Test Generator
3. Generate test cases
4. Review with team
5. Generate test steps for each case
6. Export to test management tool
7. Execute tests

### Workflow 2: Regression Testing

1. Load historical user story from History tab
2. Review existing test cases
3. Generate additional edge cases
4. Update test steps as needed
5. Export updated test suite

### Workflow 3: Bug Fix Verification

1. Create user story describing the bug fix
2. Generate negative test cases
3. Focus on edge cases
4. Generate detailed test steps
5. Use for regression testing

## 🎓 Learning Resources

### Sample Files

Check the `samples/` directory:
- `sample-user-stories.md` - 10 complete user stories
- `sample-test-cases.md` - Full test case examples
- `sample-test-steps.md` - Detailed test step examples

### In-App Samples

Click "View Samples" to see:
- Login Feature example
- Shopping Cart example
- Use these to learn the format

## ⚠️ Troubleshooting Quick Fixes

### "Failed to generate test cases"

```bash
# Check your API key
cat .env | grep OPENAI_API_KEY

# Should show: OPENAI_API_KEY=sk-...
```

### Server won't start

```bash
# Check if port is in use
netstat -ano | findstr :3000  # Windows
lsof -i :3000                 # Mac/Linux

# Use different port
echo "PORT=3001" >> .env
```

### Slow generation

- Normal: 10-30 seconds
- If longer: Check internet connection
- If very slow: Try gpt-3.5-turbo model

## 🚀 Next Steps

Now that you're set up:

1. ✅ Generate test cases for your actual user stories
2. ✅ Customize the examples to match your format
3. ✅ Integrate with your test management tool
4. ✅ Share with your QA team
5. ✅ Provide feedback for improvements

## 📞 Need Help?

1. Check `README.md` for detailed documentation
2. Review `samples/` directory for examples
3. Check browser console for errors (F12)
4. Check server logs in terminal

## 🎉 Success Checklist

- [ ] Server running on http://localhost:3000
- [ ] Sample test cases generated successfully
- [ ] Test steps generated from a test case
- [ ] CSV export working
- [ ] History tab showing saved items
- [ ] Ready to use with real user stories!

---

**You're all set! Start generating comprehensive test cases with AI! 🚀**

**Estimated time to first generation: 5 minutes**
**Estimated time to master: 30 minutes**

Happy Testing! 🎯
