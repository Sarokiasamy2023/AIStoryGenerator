# Gherkin to Test Steps Integration with AITestGenerator

## Overview

This integration connects the SalesforceAutomationRecorder with the AITestGenerator project to provide AI-powered conversion of Gherkin scenarios into executable test steps.

## Architecture

```
┌─────────────────────────────────────┐
│  SalesforceAutomationRecorder       │
│  (Python FastAPI - Port 8888)       │
│                                     │
│  - UI Dashboard                     │
│  - Test Execution Engine            │
│  - Gherkin Conversion Endpoint      │
└──────────────┬──────────────────────┘
               │
               │ HTTP Request
               │ POST /api/gherkin-to-steps
               ▼
┌─────────────────────────────────────┐
│  AITestGenerator                    │
│  (Node.js Express - Port 3000)      │
│                                     │
│  - OpenAI GPT-4 Integration         │
│  - Gherkin Parser                   │
│  - Test Step Generator              │
└─────────────────────────────────────┘
```

## Features

### 1. AI-Powered Gherkin Conversion
- Converts Gherkin scenarios (Given/When/Then/And) into automation-ready test steps
- Uses OpenAI GPT-4 for intelligent parsing and step generation
- Supports parameter placeholders (e.g., `%Username%`, `%Password%`)

### 2. Automatic Fallback
- If AITestGenerator service is unavailable, falls back to local GherkinStepGenerator
- Ensures continuous operation even if AI service is down

### 3. Seamless UI Integration
- Gherkin input section in the main dashboard
- One-click conversion with "Generate Test Steps from Gherkin" button
- Real-time feedback and logging

## Setup Instructions

### Prerequisites

1. **Node.js** (v14 or higher) - for AITestGenerator
2. **Python** (v3.8 or higher) - for SalesforceAutomationRecorder
3. **OpenAI API Key** - for AI-powered conversion

### Step 1: Configure AITestGenerator

1. Navigate to the AITestGenerator directory:
   ```bash
   cd "C:\Test Automation\Integration\AI Story Generator Integrated\AITestGenerator"
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure environment variables in `.env`:
   ```env
   PORT=3000
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4o-mini
   MAX_TOKENS=2000
   TEMPERATURE=0.7
   ```

### Step 2: Configure SalesforceAutomationRecorder

1. Navigate to the SalesforceAutomationRecorder directory:
   ```bash
   cd "C:\Test Automation\Integration\AI Story Generator Integrated\SalesforceAutomationRecorder"
   ```

2. Create/activate virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements_ai.txt
   ```

### Step 3: Start Both Services

**Option A: Use the startup script (Recommended)**
```bash
start_with_ai_generator.bat
```

**Option B: Start manually**

Terminal 1 - AITestGenerator:
```bash
cd "C:\Test Automation\Integration\AI Story Generator Integrated\AITestGenerator"
node server.js
```

Terminal 2 - SalesforceAutomationRecorder:
```bash
cd "C:\Test Automation\Integration\AI Story Generator Integrated\SalesforceAutomationRecorder"
venv\Scripts\activate
python ui_real_test_server.py
```

## Usage

### 1. Access the Dashboard
Open your browser and navigate to:
```
http://localhost:8888
```

### 2. Enter Gherkin Scenario
In the "Gherkin Scenario Input" section, paste your Gherkin text:

```gherkin
Given the user is on the login page
When the user enters "admin" into "Username"
And the user enters "password123" into "Password"
And the user clicks "Log in"
Then the user should see "Dashboard"
```

### 3. Generate Test Steps
1. Check "Use parameter placeholders" if you want `%Username%` instead of hardcoded values
2. Click "Generate Test Steps from Gherkin"
3. Wait for AI processing (typically 5-15 seconds)

### 4. Review Generated Steps
The test steps will be automatically populated in the "Test Steps" textarea:

```
Type "%Username%" into "Username"
Wait for 1 seconds
Type "%Password%" into "Password"
Wait for 1 seconds
Click "Log in"
Wait for 1 seconds
```

### 5. Execute Tests
1. Enter the website URL
2. Select browser
3. Click "Run Test" to execute the generated steps

## API Endpoint Details

### POST /api/convert-gherkin-steps

**Request:**
```json
{
  "gherkin_text": "Given the user is on the login page\nWhen the user enters \"admin\" into \"Username\"",
  "use_parameters": true
}
```

**Response (Success):**
```json
{
  "steps": [
    "Type \"%Username%\" into \"Username\"",
    "Wait for 1 seconds",
    "Click \"Log in\"",
    "Wait for 1 seconds"
  ],
  "total_steps": 4,
  "source": "AITestGenerator"
}
```

**Response (Fallback):**
```json
{
  "steps": [...],
  "total_steps": 4,
  "source": "GherkinStepGenerator"
}
```

## Gherkin Conversion Rules

The AI follows these rules when converting Gherkin to test steps:

### 1. Text Input Fields
```gherkin
When the user enters "value" into "FieldName"
```
→ 
```
Type "%FieldName%" into "FieldName"
Wait for 1 seconds
```

### 2. Dropdown/Select Fields
```gherkin
And the user selects "Option" for "DropdownName"
```
→
```
Select "%DropdownName%" from Dropdown "DropdownName"
Wait for 1 seconds
```

### 3. Textarea Fields
```gherkin
And the user enters "text" into textarea "TextareaName"
```
→
```
Fill textarea "%TextareaName%" with "TextareaName"
Wait for 1 seconds
```

### 4. Button Clicks
```gherkin
And the user clicks "ButtonName"
```
→
```
Click "ButtonName"
Wait for 1 seconds
```

### 5. Navigation
```gherkin
Given the user navigates to "PageName"
```
→
```
Click "PageName"
Wait for 1 seconds
```

## Troubleshooting

### Issue: "AITestGenerator service not reachable"

**Cause:** AITestGenerator Node.js service is not running

**Solution:**
1. Check if Node.js service is running on port 3000
2. Start the service: `node server.js` in AITestGenerator directory
3. Verify: Open `http://localhost:3000` in browser

### Issue: "Failed to convert Gherkin"

**Cause:** Invalid Gherkin syntax or AI service error

**Solution:**
1. Check Gherkin syntax (must use Given/When/Then/And)
2. Verify OpenAI API key is valid in `.env`
3. Check console logs for detailed error messages

### Issue: Generated steps are incorrect

**Cause:** AI interpretation issue

**Solution:**
1. Use more explicit Gherkin syntax
2. Include field types in Gherkin (e.g., "into textarea", "from dropdown")
3. Review and manually edit generated steps if needed

### Issue: Port conflicts

**Cause:** Ports 3000 or 8888 already in use

**Solution:**
1. Change AITestGenerator port in `.env`: `PORT=3001`
2. Update the API endpoint URL in `ui_real_test_server.py`:
   ```python
   ai_test_generator_url = "http://localhost:3001/api/gherkin-to-steps"
   ```

## Advanced Configuration

### Customize AI Behavior

Edit `AITestGenerator/services/aiService.js` to modify:
- Temperature (creativity): Default 0.7
- Max tokens (response length): Default 2000
- Model: Default gpt-4o-mini

### Add Custom Gherkin Patterns

Extend the AI prompt in `aiService.js` `convertGherkinToSteps()` method to handle custom patterns.

## Benefits

1. **Speed**: Convert Gherkin scenarios to test steps in seconds
2. **Consistency**: AI ensures consistent formatting across all test steps
3. **Accuracy**: GPT-4 understands context and generates appropriate actions
4. **Flexibility**: Supports parameter placeholders for data-driven testing
5. **Fallback**: Continues working even if AI service is unavailable

## Example Workflow

1. **Write Gherkin** in your BDD tool (Cucumber, SpecFlow, etc.)
2. **Copy Gherkin** to the dashboard
3. **Generate Steps** with one click
4. **Execute Tests** immediately
5. **Learn Selectors** on first run
6. **Reuse Selectors** on subsequent runs

## Integration Points

### Files Modified
- `ui_real_test_server.py`: Added `/api/convert-gherkin-steps` endpoint
- `real_test_dashboard.html`: Already has `generateTestStepsFromGherkin()` function

### Dependencies Added
- `httpx`: For HTTP requests to AITestGenerator service

### New Files
- `start_with_ai_generator.bat`: Startup script for both services
- `GHERKIN_AI_INTEGRATION.md`: This documentation

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review console logs in both services
3. Verify OpenAI API key and quota
4. Test AITestGenerator independently at `http://localhost:3000/gherkin`

---

**Last Updated:** December 2024
**Version:** 1.0.0
