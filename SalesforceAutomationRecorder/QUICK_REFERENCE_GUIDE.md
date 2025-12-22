# 🚀 Quick Reference Guide

## Start Server
```bash
.\kill_and_start.bat
```

## Open Dashboard
```
http://localhost:8888
```

## Test Step Formats

| Action | Format | Example |
|--------|--------|---------|
| **Fill** | `Type "value" into "Field"` | `Type "john@example.com" into "Email"` |
| **Fill** | `fill Field with value` | `fill search with Playwright` |
| **Click** | `Click "Button"` | `Click "Submit"` |
| **Wait** | `Wait for X seconds` | `Wait for 2 seconds` |
| **Select** | `Select "option" from Dropdown "Field"` | `Select "USA" from Dropdown "Country"` |
| **Check** | `Check "Checkbox"` | `Check "I agree"` |
| **Verify** | `Verify "Text" is visible` | `Verify "Welcome" is visible` |

## Execution Modes

| Button | Mode | When to Use |
|--------|------|-------------|
| ▶️ Green | Standard | First run, learning |
| 🔄 Blue | Enhanced | Re-run, fast |
| 🤖 Purple | Gemini AI | Complex elements |

## Gemini AI Setup

```bash
# 1. Get API key from https://makersuite.google.com/app/apikey
# 2. Set API key
set_api_key.bat

# 3. Verify
python check_gemini_status.py

# 4. Restart server
.\kill_and_start.bat
```

## Common Commands

```bash
# Start server
.\kill_and_start.bat

# Check Gemini status
python check_gemini_status.py

# View logs
python view_gemini_logs.py

# Clear learning data
python clear_learning.py

# Setup credentials
setup_credentials.bat
```

## File Locations

| File | Purpose |
|------|---------|
| `test_learning.json` | Learned selectors |
| `config.json` | Main configuration |
| `gemini_config.json` | Gemini AI settings |
| `ui/real_test_dashboard.html` | Dashboard |
| `ui_real_test_server.py` | Server |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port in use | `netstat -ano \| findstr :8888` then `taskkill /F /PID <PID>` |
| Disconnected | Restart server, refresh browser |
| Parse error | Check step format |
| Gemini not working | Run `check_gemini_status.py`, set API key |

## Performance Metrics

| Metric | Meaning |
|--------|---------|
| ⏱️ Total Time | Complete test duration |
| 🔄 Selectors Reused | Elements found with learned selectors |
| 🧠 Selectors Learned | New selectors learned this run |
| 📊 Reuse Efficiency | % found with learned selectors |
| 🤖 Gemini AI Usage | % requiring AI |
| 💡 AI Suggestions | AI-found / total elements |

## Example Test

```
Type "https://login.salesforce.com" into "URL"
Click "Go"
Wait for 2 seconds
Type "user@example.com" into "Username"
Type "password123" into "Password"
Click "Log in"
Wait for 3 seconds
Verify "Home" is visible
Click "App Launcher"
fill search with Accounts
Click "Accounts"
Verify "Recently Viewed" is visible
```

## API Endpoints

```
WebSocket: ws://localhost:8888/ws/test
GET:       /api/gemini-status
GET:       /api/learning-stats
POST:      /api/clear-learning
```

## Key Components

| Component | File | Purpose |
|-----------|------|---------|
| Base Executor | `real_test_executor.py` | Traditional selectors |
| Enhanced Executor | `enhanced_test_executor.py` | + Learning |
| Gemini Executor | `gemini_enhanced_executor.py` | + AI |
| Smart Locator | `smart_locator.py` | Selector generation |
| Gemini AI | `gemini_selector_ai.py` | AI integration |
| Server | `ui_real_test_server.py` | FastAPI + WebSocket |
| Dashboard | `ui/real_test_dashboard.html` | Web UI |

## Configuration

### config.json
```json
{
  "browser": {
    "headless": false,
    "slowMo": 100
  },
  "selectors": {
    "preferredStrategy": "css",
    "generateMultiple": true
  }
}
```

### gemini_config.json
```json
{
  "gemini_ai": {
    "enabled": true,
    "model": "gemini-pro",
    "max_retries": 3
  },
  "selector_strategies": {
    "use_traditional_first": true,
    "max_traditional_attempts": 10
  }
}
```

## Environment Variables

```bash
# Gemini API Key
set GEMINI_API_KEY=your_api_key_here

# Or use batch file
set_api_key.bat
```

## Dependencies

### Core (requirements.txt)
```
playwright==1.40.0
asyncio==3.4.3
google-generativeai>=0.3.0
```

### AI (requirements_ai.txt)
```
fastapi==0.104.1
uvicorn==0.24.0
websockets==12.0
```

## Decision Flow

```
User clicks Run
    ↓
Parse steps
    ↓
For each step:
    Try learned selector → Success? Execute
    ↓
    Try traditional → Success? Learn + Execute
    ↓
    Try Gemini AI → Success? Learn + Execute
    ↓
    Fail → Log error
```

## Best Practices

1. ✅ Let system learn on first run
2. ✅ Use Enhanced mode for repeated tests
3. ✅ Use Gemini AI for complex elements
4. ✅ Monitor metrics to optimize
5. ✅ Clear learning if page structure changes

## Support

- 📖 Full docs: `COMPLETE_DOCUMENTATION.md`
- 🔍 Troubleshooting: See documentation
- 🤖 Gemini setup: `check_gemini_status.py`
- 📊 View logs: `view_gemini_logs.py`
