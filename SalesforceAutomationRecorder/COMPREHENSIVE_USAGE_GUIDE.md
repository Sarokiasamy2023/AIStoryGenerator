# Salesforce Automation Recorder - Comprehensive Usage Guide

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation & Setup](#installation--setup)
4. [Core Workflows](#core-workflows)
5. [Test Step Format](#test-step-format)
6. [Dynamic Data Generation](#dynamic-data-generation)
7. [Learned Selectors System](#learned-selectors-system)
8. [Parallel Execution](#parallel-execution)
9. [AI Integration](#ai-integration)
10. [API Reference](#api-reference)
11. [Troubleshooting](#troubleshooting)

---

## Overview

The **Salesforce Automation Recorder** is a comprehensive test automation framework designed specifically for Salesforce Lightning and OmniScript applications. It provides:

- **Recording**: Capture user interactions on Salesforce forms
- **Playback**: Execute recorded tests with intelligent element detection
- **Learning**: Auto-learn and reuse successful selectors
- **Data Generation**: Dynamic test data based on form schema
- **Parallel Execution**: Run multiple tests simultaneously
- **AI Enhancement**: Optional Gemini AI for smart element detection

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SALESFORCE AUTOMATION RECORDER                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────┐    ┌──────────────────────┐    ┌────────────────┐ │
│  │   UI Layer           │    │   Execution Layer     │    │  Data Layer    │ │
│  │                      │    │                       │    │                │ │
│  │  ui_real_test_       │◄──►│  EnhancedTestExecutor │◄──►│ test_learning  │ │
│  │  server.py           │    │  GeminiEnhancedExec   │    │ .json          │ │
│  │                      │    │                       │    │                │ │
│  │  /parallel-execution │    │  real_test_executor   │    │ data.csv       │ │
│  │  /                   │    │  .py                  │    │ fields.json    │ │
│  └──────────────────────┘    └──────────────────────┘    └────────────────┘ │
│           │                           │                          │          │
│           │                           │                          │          │
│  ┌────────▼──────────────────────────▼──────────────────────────▼────────┐ │
│  │                         PLAYWRIGHT BROWSER ENGINE                      │ │
│  │                                                                        │ │
│  │   - Chromium / Chrome / Edge / Firefox                                 │ │
│  │   - Headless or Visible mode                                           │ │
│  │   - Screenshot capture                                                 │ │
│  │   - Video recording                                                    │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                       │
│  ┌───────────────────────────────────▼───────────────────────────────────┐  │
│  │                         SALESFORCE APPLICATION                         │  │
│  │                                                                        │  │
│  │   - Lightning Components (lightning-*, slds-*)                         │  │
│  │   - OmniScript Forms (c-omniscript-*, data-omni-*)                    │  │
│  │   - Dynamic DOM elements                                               │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Key Components

| Component | File | Purpose |
|-----------|------|---------|
| **UI Server** | `ui_real_test_server.py` | FastAPI web server with dashboard |
| **Test Executor** | `enhanced_test_executor.py` | Executes test steps with learned selectors |
| **Gemini Executor** | `gemini_enhanced_executor.py` | AI-powered test execution |
| **Schema Extractor** | `SchemaExtractor.py` | Extracts form field metadata |
| **Data Generator** | `DataGenerator.py` | Generates synthetic test data |
| **Test Processor** | `test_step_processor.py` | Orchestrates data generation and execution |
| **Recorder** | `automation_recorder.py` | Records user interactions |

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- Windows 10/11 (recommended)
- Microsoft Edge browser (recommended for Salesforce)

### Quick Setup

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install Playwright browsers
playwright install chromium
playwright install msedge

# 3. Start the server
python ui_real_test_server.py
```

### One-Click Setup (Windows)
```bash
# Full setup with dependencies
setup_and_start.bat

# Quick restart (kills existing server)
kill_and_start.bat
```

### With Gemini AI
```bash
# Set API key
set GEMINI_API_KEY=your_api_key_here

# Start with AI
start_server_with_gemini.bat
```

---

## Core Workflows

### Workflow 1: Manual Test Execution (Web UI)

```
┌─────────────────────────────────────────────────────────────────┐
│  1. Start Server                                                 │
│     python ui_real_test_server.py                               │
│                                                                  │
│  2. Open Dashboard                                               │
│     http://localhost:8888                                        │
│                                                                  │
│  3. Enter Test Details                                           │
│     - URL: https://your-salesforce-instance.com                 │
│     - Test Steps (plain text format)                            │
│                                                                  │
│  4. Click "Run Test"                                             │
│     - Watch real-time execution                                 │
│     - View learned selectors                                    │
│     - See step-by-step results                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Workflow 2: Dynamic Data-Driven Testing

```
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Extract Schema (if no data.csv exists)                 │
│  ───────────────────────────────────────────────────────────────│
│  python main.py                                                  │
│                                                                  │
│  Output:                                                         │
│    - outputs/fields.json (form schema)                          │
│    - outputs/fields1.png... (screenshots)                       │
├─────────────────────────────────────────────────────────────────┤
│  STEP 2: Generate Test Data                                      │
│  ───────────────────────────────────────────────────────────────│
│  python test_step_processor.py --run --rows 10                  │
│                                                                  │
│  Output:                                                         │
│    - data.csv (10 rows of synthetic data)                       │
├─────────────────────────────────────────────────────────────────┤
│  STEP 3: Execute Tests                                           │
│  ───────────────────────────────────────────────────────────────│
│  python test_step_processor.py --execute --rows 5               │
│                                                                  │
│  Output:                                                         │
│    - Final Test steps.txt (executed steps for all datasets)     │
│    - test_learning.json (updated with new selectors)            │
└─────────────────────────────────────────────────────────────────┘
```

### Workflow 3: Full Automation Pipeline

```bash
# Single command: Extract schema + Generate data + Execute tests
python test_step_processor.py --run --rows 5 --execute
```

---

## Test Step Format

### Supported Actions

| Action | Syntax | Example |
|--------|--------|---------|
| **Type** | `Type "value" into "Field Name"` | `Type "john@example.com" into "Username"` |
| **Click** | `Click "Button/Link Text"` | `Click "Submit"` |
| **Wait** | `Wait for N seconds` | `Wait for 2 seconds` |
| **Select Dropdown** | `Select "option" from Dropdown "Field"` | `Select "Yes" from Dropdown "Status"` |
| **Fill Textarea** | `Fill textarea "Field" with "text"` | `Fill textarea "Notes" with "Hello"` |
| **Check** | `Check "Checkbox Label"` | `Check "I agree to terms"` |
| **Verify** | `Verify "Text" is visible` | `Verify "Success" is visible` |
| **Upload** | `Upload "file_path" to "Field"` | `Upload "doc.pdf" to "Document"` |

### Placeholders for Dynamic Data

Use `%Field Name%` placeholders in test steps:

```text
Type "%Username%" into "Username"
Type "%Email%" into "Email Address"
Select "%Country%" from Dropdown "Country"
```

These are replaced with data from `data.csv` at runtime.

### Sample Test Steps File

```text
# Login
Type "user@example.com" into "Username"
Type "password123" into "Password"
Click "Log in"
Wait for 2 seconds

# Navigate to form
Click "CBD PERFORMANCE REPORTS"
Wait for 1 seconds
Click "In Progress Reports"
Click "CBD-01361"

# Fill form with dynamic data
Type "%Number of Counties Served%" into "Number of Counties Served"
Type "%Hispanic or Latino%" into "Hispanic or Latino"
Select "%Status%" from Dropdown "Status"
Click "Next"
```

---

## Dynamic Data Generation

### How It Works

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  SchemaExtractor│     │  DataGenerator  │     │ Test Processor  │
│                 │     │                 │     │                 │
│  Navigates form │────►│  Reads schema   │────►│  Replaces       │
│  Extracts fields│     │  Generates data │     │  placeholders   │
│  Saves JSON     │     │  Saves CSV      │     │  Executes tests │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
   fields.json              data.csv           Final Test steps.txt
```

### Schema Format (fields.json)

```json
{
  "NumberOfCountiesServed__c": {
    "label": "Number of Counties Served",
    "type": "text",
    "required": true,
    "pattern": "^[0-9]+$",
    "minlength": 1,
    "maxlength": 5
  },
  "Status__c": {
    "label": "Status",
    "type": "select",
    "options": ["Active", "Inactive", "Pending"]
  }
}
```

### Generated Data Format (data.csv)

```csv
NumberOfCountiesServed__c,HispanicOrLatino__c,Status__c
125,45,Active
87,23,Pending
```

### Commands

```bash
# Extract schema only
python main.py

# Generate data (uses existing schema)
python test_step_processor.py --run --rows 10

# Generate and execute
python test_step_processor.py --run --execute --rows 5
```

---

## Learned Selectors System

### How Learning Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    SELECTOR LEARNING FLOW                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Test step received: Click "Log in"                          │
│                                                                  │
│  2. Check test_learning.json                                    │
│     ├── Found? → Use learned selector (fast!)                   │
│     └── Not found? → Generate selector strategies               │
│                                                                  │
│  3. Try selector strategies in order:                           │
│     ├── button:has-text('Log in')                               │
│     ├── input[value='Log in']                                   │
│     ├── a:has-text('Log in')                                    │
│     └── xpath=//button[contains(.,'Log in')]                    │
│                                                                  │
│  4. First successful selector → LEARN IT                        │
│     └── Save to test_learning.json                              │
│                                                                  │
│  5. Next time → Direct lookup (no trial and error)              │
└─────────────────────────────────────────────────────────────────┘
```

### Learned Selector Format

```json
{
  "log_in": {
    "selector": "button:has-text('Log in')",
    "target": "Log in",
    "action": "click",
    "success_count": 15,
    "first_learned": "2025-11-25T09:27:21",
    "last_used": "2025-12-04T09:02:49"
  }
}
```

### Benefits

- **Speed**: No trial-and-error on subsequent runs
- **Reliability**: Proven selectors from real execution
- **Shared**: Same selectors used by UI server and command line
- **Self-healing**: Failed selectors are removed and relearned

### Managing Learned Selectors

```bash
# View learned selectors
python -c "import json; print(json.dumps(json.load(open('test_learning.json')), indent=2))"

# Clear all learned selectors
python clear_learning.py

# Selectors are automatically updated during test execution
```

---

## Parallel Execution

### Web UI Method

1. Navigate to `http://localhost:8888/parallel-execution`
2. Set number of parallel instances (1-10)
3. Click "Generate Forms"
4. Fill in details for each instance:
   - URL
   - Username/Password
   - Test steps
5. Click "Execute All Tests in Parallel"

### API Method

```python
import requests

payload = {
    "instances": [
        {
            "url": "https://sf-instance1.com",
            "username": "user1",
            "password": "pass1",
            "steps": ["Click 'Login'", "Wait for 2 seconds"]
        },
        {
            "url": "https://sf-instance2.com",
            "username": "user2",
            "password": "pass2",
            "steps": ["Click 'Login'", "Wait for 2 seconds"]
        }
    ]
}

response = requests.post("http://localhost:8888/api/run-parallel", json=payload)
```

---

## AI Integration

### Gemini AI Features

- **Smart Selector Generation**: AI analyzes page structure
- **Visual Element Detection**: Screenshot-based element finding
- **Self-Healing**: AI suggests alternative selectors when elements fail

### Setup

```bash
# Set API key
set GEMINI_API_KEY=your_api_key_here

# Or use batch file
setup_gemini.bat
```

### Usage

```bash
# Command line with AI
python test_step_processor.py --execute --rows 2 --ai

# UI server with AI
start_server_with_gemini.bat
```

### Check AI Status

```bash
python check_gemini_status.py
```

---

## API Reference

### Server Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard |
| `/parallel-execution` | GET | Parallel execution UI |
| `/api/run-test` | POST | Execute single test |
| `/api/run-parallel` | POST | Execute parallel tests |
| `/api/stop-test` | POST | Stop running test |
| `/api/gemini-status` | GET | Check AI status |
| `/api/learned-selectors` | GET | View learned selectors |
| `/api/allure-summary` | GET | Test results summary |
| `/allure-report` | GET | Allure HTML report |

### WebSocket Events

Connect to `/ws` for real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8888/ws');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // Types: test_start, step_start, step_success, step_failed, 
    //        selector_learned, using_learned, test_complete
    console.log(data.type, data.message);
};
```

---

## Command Line Reference

### test_step_processor.py

```bash
# Show help
python test_step_processor.py --help

# Extract schema and generate data
python test_step_processor.py --run --rows 10

# Execute tests with learned selectors
python test_step_processor.py --execute --rows 5

# Execute with AI
python test_step_processor.py --execute --rows 5 --ai

# Process single dataset
python test_step_processor.py --dataset 1

# Process all datasets to file (no execution)
python test_step_processor.py --all

# Full pipeline
python test_step_processor.py --run --execute --rows 10
```

### main.py

```bash
# Extract schema from Salesforce form
python main.py

# With options
python main.py --skip-navigation  # Skip if already on form
python main.py --rows 50          # Generate 50 data rows
```

### ui_real_test_server.py

```bash
# Start server on default port (8888)
python ui_real_test_server.py

# Start on custom port
python ui_real_test_server.py 9000
```

---

## Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| Port 8888 in use | Run `kill_and_start.bat` |
| Browser not starting | Run `playwright install msedge` |
| Selector not found | Check `test_learning.json` and clear if stale |
| Login failing | Verify credentials in test steps |
| Elements not visible | Add `Wait for N seconds` before interaction |

### Debug Screenshots

When a selector fails, debug screenshots are saved:
- `debug_not_found_<element>.png`

### Logs

```bash
# View execution logs
type allure-results\*.json

# View Gemini AI logs
python view_gemini_logs.py
```

### Reset Everything

```bash
# Clear learned selectors
python clear_learning.py

# Clear test results
rmdir /s /q allure-results

# Restart server
kill_and_start.bat
```

---

## Quick Reference Card

### Start Testing
```bash
python ui_real_test_server.py     # Start UI server
# Open http://localhost:8888
```

### Generate Data & Execute
```bash
python test_step_processor.py --run --execute --rows 5
```

### View Results
```bash
# Open http://localhost:8888/allure-report
```

### Key Files
| File | Purpose |
|------|---------|
| `Sample Test Steps.txt` | Test step template |
| `data.csv` | Generated test data |
| `fields.json` | Form schema |
| `test_learning.json` | Learned selectors |
| `Final Test steps.txt` | Executed test output |

---

## Version Information

- **Version**: 2.0
- **Last Updated**: December 2025
- **Python**: 3.8+
- **Playwright**: Latest
- **AI**: Gemini API (optional)

---

*For more details, see the individual documentation files in this repository.*
