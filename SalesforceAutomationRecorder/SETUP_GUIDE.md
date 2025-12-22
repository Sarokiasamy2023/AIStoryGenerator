# Setup Guide for Salesforce Automation Recorder

This guide will help you set up and run the Salesforce Automation Recorder project.

## Prerequisites

- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **Git** (optional) - For cloning the repository

## Step-by-Step Setup

### 1. Install Python Dependencies

Open a terminal/command prompt in the project directory and run:

```bash
pip install -r requirements.txt
```

This will install:
- Playwright (browser automation)
- Google Generative AI (Gemini AI integration)
- Allure (test reporting)
- Other required packages

### 2. Install Playwright Browsers

After installing the Python packages, install the Chromium browser:

```bash
playwright install chromium
```

### 3. Set Up Gemini API Key (Optional)

The project uses Google's Gemini AI for intelligent test generation and healing. You have two options:

#### Option A: Use Environment Variable (Recommended for sharing)
```bash
# Windows (Command Prompt)
set GEMINI_API_KEY=your_api_key_here

# Windows (PowerShell)
$env:GEMINI_API_KEY="your_api_key_here"

# Linux/Mac
export GEMINI_API_KEY=your_api_key_here
```

#### Option B: Use the provided batch file
```bash
.\setup_gemini.bat
```

**Note:** If you don't have a Gemini API key, you can get one from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Running the Server

### Method 1: Simple Start (Recommended for Others)

Use the simple start script:

```bash
.\start_server.bat
```

This will:
- Check if Python is installed
- Verify the server file exists
- Start the server on http://localhost:8889

### Method 2: Direct Python Command

```bash
python ui_real_test_server.py
```

### Method 3: With Port Cleanup (if port is already in use)

```bash
.\kill_and_start.bat
```

This will:
- Kill any process using port 8888
- Set the Gemini API key
- Start the server

## Accessing the Application

Once the server is running, open your web browser and navigate to:

```
http://localhost:8888
```

or

```
http://localhost:8889
```

(depending on which start script you used)

## Running Tests

### Run a Single Test

```bash
python test_dcp.py
```

### Run All Tests

```bash
.\run_all_tests.bat
```

### Run Tests with Reporting

```bash
.\run_and_report.bat
```

## Troubleshooting

### Port Already in Use

If you see an error about port 8888 or 8889 being in use:

1. Use `kill_and_start.bat` to automatically kill the process
2. Or manually find and kill the process:
   ```bash
   # Windows
   netstat -ano | findstr :8888
   taskkill /F /PID <process_id>
   ```

### Python Not Found

Make sure Python is installed and added to your PATH:
```bash
python --version
```

### Playwright Browser Not Installed

If you get browser-related errors:
```bash
playwright install chromium
```

### Missing Dependencies

If you get import errors:
```bash
pip install -r requirements.txt --upgrade
```

## Project Structure

```
SalesforceAutomationRecorder/
├── ui_real_test_server.py      # Main server file
├── automation_recorder.py       # Core recorder logic
├── test_dcp.py                 # Sample test file
├── requirements.txt            # Python dependencies
├── start_server.bat            # Simple server start
├── kill_and_start.bat          # Server start with cleanup
└── templates/                  # HTML templates
    └── enhanced_dashboard.html # Web UI
```

## For Developers

### Creating New Tests

1. Create a new Python file (e.g., `test_mytest.py`)
2. Import the required modules:
   ```python
   import asyncio
   from playwright.async_api import async_playwright
   ```
3. Follow the pattern in `test_dcp.py`

### Recording New Interactions

1. Start the server
2. Navigate to the web UI
3. Click "Start Recording"
4. Perform actions in Salesforce
5. Click "Stop Recording"
6. Export the JSON file

## Support

For issues or questions:
1. Check the `DOCUMENTATION_COMPLETE.md` file
2. Review the `QUICK_REFERENCE_GUIDE.md`
3. Check existing test files for examples

## Quick Start Checklist

- [ ] Install Python 3.8+
- [ ] Run `pip install -r requirements.txt`
- [ ] Run `playwright install chromium`
- [ ] (Optional) Set GEMINI_API_KEY environment variable
- [ ] Run `.\start_server.bat` or `python ui_real_test_server.py`
- [ ] Open http://localhost:8888 in your browser
- [ ] Start testing!
