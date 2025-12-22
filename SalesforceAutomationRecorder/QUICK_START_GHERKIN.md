# Quick Start: Gherkin to Test Steps

## 🚀 Get Started in 3 Minutes

### Step 1: Start the Services (30 seconds)

Double-click the startup script:
```
start_with_ai_generator.bat
```

This will:
- ✅ Start AITestGenerator on port 3000
- ✅ Start SalesforceAutomationRecorder on port 8888
- ✅ Open the dashboard in your browser

### Step 2: Enter Your Gherkin (30 seconds)

In the dashboard, find the **"Gherkin Scenario Input"** section and paste your Gherkin:

```gherkin
Given the user is on the login page
When the user enters "admin" into "Username"
And the user enters "password123" into "Password"
And the user clicks "Log in"
Then the user should see "Dashboard"
```

### Step 3: Generate Test Steps (15 seconds)

1. ✅ Check "Use parameter placeholders" (recommended)
2. Click **"🔄 Generate Test Steps from Gherkin"**
3. Wait 5-15 seconds for AI processing

### Step 4: Run Your Test (2 minutes)

1. Enter your website URL
2. Select browser (Chrome/Edge/Firefox)
3. Click **"▶️ Run Test"**
4. Watch the test execute in real-time!

## 📝 Example Gherkin Scenarios

### Login Test
```gherkin
Given the user is on the login page
When the user enters "admin" into "Username"
And the user enters "password123" into "Password"
And the user clicks "Log in"
Then the user should see "Dashboard"
```

### Form Submission
```gherkin
Given the user is on the registration page
When the user enters "John Doe" into "Full Name"
And the user enters "john@example.com" into "Email"
And the user selects "USA" for "Country"
And the user enters "Test message" into textarea "Comments"
And the user clicks "Submit"
Then the user should see "Success"
```

### Navigation Test
```gherkin
Given the user is on the homepage
When the user clicks "Products"
And the user clicks "Electronics"
And the user clicks "Laptops"
Then the user should see "Product List"
```

## 🎯 Generated Test Steps Format

Your Gherkin will be converted to:

```
Type "%Username%" into "Username"
Wait for 1 seconds
Type "%Password%" into "Password"
Wait for 1 seconds
Click "Log in"
Wait for 1 seconds
```

## ⚙️ Configuration (Optional)

### Set Your OpenAI API Key

Edit `AITestGenerator\.env`:
```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

Get your API key from: https://platform.openai.com/api-keys

## 🔧 Troubleshooting

### Services Won't Start?

**Check Node.js:**
```bash
node --version
```
Should show v14 or higher. Install from https://nodejs.org/

**Check Python:**
```bash
python --version
```
Should show v3.8 or higher.

### AI Not Working?

1. Verify OpenAI API key in `AITestGenerator\.env`
2. Check you have API credits available
3. The system will use fallback generator if AI is unavailable

### Port Already in Use?

Change ports in:
- AITestGenerator: Edit `.env` → `PORT=3001`
- Update endpoint in `ui_real_test_server.py` line 1096

## 📚 Learn More

- Full documentation: `GHERKIN_AI_INTEGRATION.md`
- AITestGenerator docs: `AITestGenerator\README.md`
- Main project docs: `README.md`

## 💡 Tips

1. **Use descriptive field names** in Gherkin for better AI understanding
2. **Check "Use parameter placeholders"** for data-driven testing
3. **Review generated steps** before running (you can edit them)
4. **First run learns selectors**, second run reuses them (faster!)
5. **Use Gemini AI button** for even smarter element detection

---

**Need Help?** Check the full integration guide in `GHERKIN_AI_INTEGRATION.md`
