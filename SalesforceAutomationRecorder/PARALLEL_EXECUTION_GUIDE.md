# Parallel Execution Guide

## Overview

The Parallel Execution feature allows you to run multiple test cases simultaneously across different URLs with separate login credentials and test steps.

## Starting the Server

### Option 1: Quick Start (Kill existing and start fresh)

```bash
kill_and_start.bat
```

**What it does:**
- Kills any existing process on port 8888
- Sets the Gemini API key
- Starts the UI server on port 8888

**Use this when:**
- You want to restart the server quickly
- A previous server instance is still running
- You need a fresh start

### Option 2: Full Setup and Start

```bash
setup_and_start.bat
```

**What it does:**
- Installs all Python dependencies from requirements.txt
- Installs Playwright Chromium browser
- Kills any existing process on port 8888
- Sets the Gemini API key
- Starts the UI server on port 8888

**Use this when:**
- First time setup
- After updating dependencies
- After pulling new code changes
- Playwright browser needs reinstallation

### Option 3: Simple Start

```bash
start_real_test.bat
```

**What it does:**
- Simply starts the server (assumes dependencies are installed)
- Does NOT kill existing processes

**Use this when:**
- Dependencies are already installed
- No existing server is running
- Quick testing

## Stopping the Server

### Method 1: Keyboard Interrupt
Press `Ctrl+C` in the terminal window where the server is running.

### Method 2: Kill Process Manually

```bash
# Find the process on port 8888
netstat -ano | findstr :8888

# Kill the process (replace PID with actual process ID)
taskkill /F /PID <PID>
```

### Method 3: Use kill_and_start.bat
Running `kill_and_start.bat` will automatically kill any existing server before starting a new one.

## Accessing the Application

Once the server is running, access:

- **Main Dashboard**: http://localhost:8888
- **Parallel Execution**: http://localhost:8888/parallel-execution

## Using Parallel Execution

### Step 1: Navigate to Parallel Execution
Click the "🚀 Parallel Execution" button on the main dashboard.

### Step 2: Configure Number of Parallel Executions
1. Enter the number of parallel executions (1-10)
2. Click "🔄 Generate Forms"

### Step 3: Fill in Details for Each Instance

For each instance, provide:

**URL Configuration:**
- URL: The target website URL (e.g., https://example.com)

**Login Credentials (Optional):**
- Username: Login username for this instance
- Password: Login password for this instance

**Test Steps:**
- Enter test steps in plain text format (one per line)
- Each instance can have different test steps

### Step 4: Execute Tests
Click "▶️ Execute All Tests in Parallel" to start execution.

### Step 5: Monitor Progress
- Watch the real-time execution log
- Monitor the progress bar
- View success/failure status for each instance

## Test Step Format

### Supported Formats

**Format 1: Natural Language**
```
fill search with Playwright automation
click Google Search button
wait for 2 seconds
```

**Format 2: Explicit Actions**
```
Type "test@example.com" into "Username"
Type "password123" into "Password"
Click "Log in"
Wait for 3 seconds
```

### Common Actions

- **Fill/Type**: `fill <field> with <value>` or `Type "<value>" into "<field>"`
- **Click**: `click <button>` or `Click "<button>"`
- **Wait**: `wait for <N> seconds` or `Wait for <N> seconds`
- **Select**: `select <option> from <dropdown>`

## Example Use Cases

### Example 1: Testing Multiple Environments

**Instance 1:**
- URL: https://dev.example.com
- Username: dev_user@example.com
- Password: dev_password
- Steps: Standard test flow

**Instance 2:**
- URL: https://staging.example.com
- Username: staging_user@example.com
- Password: staging_password
- Steps: Standard test flow

### Example 2: Load Testing

**Instance 1-5:**
- Same URL: https://example.com
- Different credentials for each
- Same test steps
- Tests concurrent user load

### Example 3: Cross-Browser Testing

**Instance 1:**
- URL: https://example.com
- Test Steps: UI validation tests

**Instance 2:**
- URL: https://example.com
- Test Steps: Form submission tests

**Instance 3:**
- URL: https://example.com
- Test Steps: Navigation tests

## Troubleshooting

### Server Won't Start

**Problem:** Port 8888 is already in use

**Solution:**
```bash
# Use kill_and_start.bat to kill existing process
kill_and_start.bat
```

### Dependencies Missing

**Problem:** Module not found errors

**Solution:**
```bash
# Run full setup
setup_and_start.bat
```

### Playwright Browser Not Found

**Problem:** Browser executable not found

**Solution:**
```bash
# Install Playwright browsers
playwright install chromium
```

### Encoding Errors

**Problem:** UnicodeEncodeError on Windows

**Solution:** The code has been updated to avoid special Unicode characters. If you still see errors, ensure your terminal supports UTF-8:
```bash
chcp 65001
```

## Features

### Real-time Updates
- Live execution log showing each step
- WebSocket-based real-time communication
- Progress tracking for all instances

### Independent Execution
- Each instance runs in its own browser session
- Failures in one instance don't affect others
- Separate screenshots for each instance

### Learning & Reuse
- Selectors learned during execution
- Reused in subsequent runs
- Improved performance over time

### AI Enhancement (Optional)
- Gemini AI integration for smart selectors
- Automatic fallback to traditional selectors
- Enhanced element detection

## Advanced Configuration

### Changing the Port

Edit `ui_real_test_server.py`:
```python
if __name__ == "__main__":
    run_server(port=9000)  # Change port here
```

### Headless Mode

In the parallel execution page, modify the API call:
```javascript
body: JSON.stringify({
    tests: executionData,
    headless: true  // Change to true for headless
})
```

### Custom Timeouts

Edit test steps:
```
wait for 5 seconds  # Increase wait time
```

## Best Practices

1. **Start with 2-3 parallel executions** to test stability
2. **Use descriptive test steps** for better logging
3. **Monitor system resources** when running many parallel tests
4. **Save screenshots** are automatically saved as `parallel_test_instance_<N>.png`
5. **Review logs** after execution for debugging

## API Endpoints

### Execute Parallel Tests
```
POST /api/execute-parallel-tests
Body: {
    "tests": [...],
    "headless": false
}
```

### Stop Parallel Tests
```
POST /api/stop-parallel-tests
```

### WebSocket Connection
```
ws://localhost:8888/ws/parallel-test
```

## Support

For issues or questions:
1. Check the execution log for error messages
2. Review the console output in the terminal
3. Verify all dependencies are installed
4. Ensure port 8888 is available

## Quick Reference

| Command | Purpose |
|---------|---------|
| `kill_and_start.bat` | Kill existing server and start fresh |
| `setup_and_start.bat` | Full setup and start |
| `start_real_test.bat` | Simple start (no kill) |
| `Ctrl+C` | Stop server |
| `netstat -ano \| findstr :8888` | Check if server is running |
| `taskkill /F /PID <PID>` | Kill specific process |

## Server URLs

- Main Dashboard: http://localhost:8888
- Parallel Execution: http://localhost:8888/parallel-execution
- API Status: http://localhost:8888/api/gemini-status
