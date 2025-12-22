# Single Port Integration - Everything on Port 8888

## Overview

The system has been updated to run **everything on port 8888**. The AITestGenerator Node.js service is no longer required as the OpenAI API integration has been embedded directly into the Python server.

## What Changed

### 1. **New Python Module: `ai_gherkin_converter.py`**
- Direct OpenAI API integration using `httpx`
- Converts Gherkin scenarios to test steps
- Same AI-powered conversion as before, but without Node.js dependency

### 2. **Updated API Endpoint**
- `/api/convert-gherkin-steps` now calls OpenAI API directly from Python
- Automatic fallback to local `GherkinStepGenerator` if OpenAI API is unavailable
- No dependency on external Node.js service

### 3. **Simplified Startup Script**
- `kill_and_start.bat` now only starts the Python service on port 8888
- Sets both Gemini and OpenAI API keys
- Single process, single port

## How to Use

### 1. Start the Server

```bash
kill_and_start.bat
```

This will:
- Kill any process on port 8888
- Set API keys (Gemini + OpenAI)
- Start the Python server on port 8888

### 2. Access the Dashboard

Open your browser to:
```
http://localhost:8888
```

### 3. Use Gherkin Conversion

1. Paste Gherkin scenario in the input section
2. Click "Generate Test Steps from Gherkin"
3. Watch the progress bar and logs
4. AI converts Gherkin to test steps
5. Steps appear in the test steps textarea

## Configuration

### OpenAI API Key

The OpenAI API key is set in `kill_and_start.bat`:

```batch
set OPENAI_API_KEY=your_api_key_here
set OPENAI_MODEL=gpt-4o-mini
set MAX_TOKENS=2000
set TEMPERATURE=0.7
```

### Alternative: Environment Variables

You can also set these in your system environment variables or create a `.env` file:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
MAX_TOKENS=2000
TEMPERATURE=0.7
```

## Features Available on Port 8888

All features are now accessible through a single port:

- ✅ **Test Execution Engine** - Run automated tests
- ✅ **AI-Powered Gherkin Conversion** - Convert Gherkin to test steps (OpenAI)
- ✅ **Gemini AI Selector Generation** - Smart element detection
- ✅ **Parallel Test Execution** - Run multiple tests simultaneously
- ✅ **Allure Reporting** - Test execution reports
- ✅ **Real-time Logs** - Live execution monitoring
- ✅ **Progress Tracking** - Visual progress bars for AI operations

## Architecture

```
┌─────────────────────────────────────────────────┐
│  SalesforceAutomationRecorder (Port 8888)       │
│  ┌───────────────────────────────────────────┐  │
│  │  FastAPI Server                           │  │
│  │  - Test Execution                         │  │
│  │  - Gherkin Conversion (OpenAI API)        │  │
│  │  - Gemini AI Integration                  │  │
│  │  - Parallel Execution                     │  │
│  │  - Allure Reporting                       │  │
│  └───────────────────────────────────────────┘  │
│                                                  │
│  ┌───────────────────────────────────────────┐  │
│  │  ai_gherkin_converter.py                  │  │
│  │  - Direct OpenAI API calls                │  │
│  │  - Gherkin to test steps conversion       │  │
│  │  - Fallback to local generator            │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                    │
                    │ HTTPS
                    ▼
        ┌─────────────────────┐
        │  OpenAI API         │
        │  (api.openai.com)   │
        └─────────────────────┘
```

## Benefits

1. **Simpler Deployment** - Only one service to manage
2. **Single Port** - Everything on port 8888
3. **No Node.js Required** - Pure Python solution
4. **Faster Startup** - No need to wait for multiple services
5. **Easier Debugging** - Single process to monitor
6. **Same Features** - All AI capabilities preserved

## Troubleshooting

### Issue: "OpenAI API key not configured"

**Solution:** Set the `OPENAI_API_KEY` environment variable in `kill_and_start.bat` or your system environment.

### Issue: Gherkin conversion uses fallback generator

**Cause:** OpenAI API key is not set or invalid

**Solution:** 
1. Check API key in `kill_and_start.bat`
2. Verify API key is valid at https://platform.openai.com/api-keys
3. Ensure you have API credits available

### Issue: Port 8888 already in use

**Solution:** Run `kill_and_start.bat` which will automatically kill any process on port 8888 before starting.

## Migration from Dual-Port Setup

If you were using the previous setup with Node.js on port 3000:

1. **No action needed** - The new setup is backward compatible
2. **Node.js service is optional** - It's no longer required
3. **Same UI** - No changes to the dashboard
4. **Same API** - Endpoints remain the same

## Performance

- **Gherkin Conversion Time:** 5-15 seconds (same as before)
- **Startup Time:** ~3 seconds (faster than dual-service setup)
- **Memory Usage:** Lower (single Python process vs Python + Node.js)

## API Endpoint

### POST /api/convert-gherkin-steps

**Request:**
```json
{
  "gherkin_text": "Given the user is on the login page\nWhen the user enters \"admin\" into \"Username\"",
  "use_parameters": true
}
```

**Response (OpenAI):**
```json
{
  "steps": [
    "Type \"%Username%\" into \"Username\"",
    "Wait for 1 seconds"
  ],
  "total_steps": 2,
  "source": "OpenAI-Python"
}
```

**Response (Fallback):**
```json
{
  "steps": [...],
  "total_steps": 2,
  "source": "GherkinStepGenerator"
}
```

## Files Modified

1. **Created:**
   - `ai_gherkin_converter.py` - OpenAI API integration

2. **Modified:**
   - `ui_real_test_server.py` - Updated API endpoint
   - `kill_and_start.bat` - Simplified to single service

3. **No longer needed:**
   - AITestGenerator Node.js service (optional, can be removed)
   - `start_with_ai_generator.bat` (use `kill_and_start.bat` instead)

## Summary

Everything now runs on **port 8888** with a single Python process. The AI-powered Gherkin conversion works the same way, but without requiring a separate Node.js service. This makes the system simpler to deploy, manage, and debug while maintaining all the same features.

---

**Last Updated:** December 2024  
**Version:** 2.0.0 (Single Port)
