# Complete Workflow Guide

## Visual Guide to Starting, Using, and Stopping the Server

---

## 🎬 Complete Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    START THE SERVER                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┼───────────────────┐
        ↓                   ↓                   ↓
   First Time?         Daily Use?         Quick Test?
        │                   │                   │
        ↓                   ↓                   ↓
setup_and_start.bat  kill_and_start.bat  start_real_test.bat
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              SERVER RUNNING ON PORT 8888                     │
│         http://localhost:8888 is now available               │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┼───────────────────┐
        ↓                   ↓                   ↓
  Main Dashboard    Parallel Execution    API Endpoints
        │                   │                   │
        ↓                   ↓                   ↓
  Single Tests      Multiple Tests       Status/Config
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   EXECUTE TESTS                              │
│         Monitor logs, view progress, get results             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   STOP THE SERVER                            │
│                   Press Ctrl+C                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Step-by-Step: Parallel Execution

### Step 1: Start Server

```bash
# Open Command Prompt
cd C:\Test Automation\Latest\SalesforceAutomationRecorder

# Run batch file
kill_and_start.bat
```

**Expected Output:**
```
======================================================================
  Killing processes on port 8888 and starting fresh
======================================================================
Stopping any process on port 8888...
  Done
Setting Gemini API Key...
  API Key: SET
======================================================================
  Starting Server on Port 8888
======================================================================
[OK] Google Gemini enabled!
INFO:     Uvicorn running on http://0.0.0.0:8888 (Press CTRL+C to quit)
```

---

### Step 2: Open Browser

```
Navigate to: http://localhost:8888
```

**You'll see:**
- Main Dashboard
- "🚀 Parallel Execution" button in header

---

### Step 3: Navigate to Parallel Execution

```
Click: "🚀 Parallel Execution" button
```

**You'll see:**
- Configuration section
- Number of Parallel Executions input
- Generate Forms button

---

### Step 4: Configure Parallel Count

```
1. Enter number: 2 (or any number 1-10)
2. Click: "🔄 Generate Forms"
```

**Result:**
- Forms appear for each instance
- URL inputs
- Credential inputs
- Test step sections

---

### Step 5: Fill Instance 1

```
URL 1: https://www.google.com
Username 1: (leave empty for Google)
Password 1: (leave empty for Google)

Test Steps for Instance 1:
fill search with Playwright automation
click Google Search button
wait for 2 seconds
```

---

### Step 6: Fill Instance 2

```
URL 2: https://www.google.com
Username 2: (leave empty for Google)
Password 2: (leave empty for Google)

Test Steps for Instance 2:
fill search with Selenium testing
click Google Search button
wait for 2 seconds
```

---

### Step 7: Execute Tests

```
Click: "▶️ Execute All Tests in Parallel"
```

**What happens:**
1. WebSocket connection established
2. Both instances start simultaneously
3. Real-time log updates appear
4. Progress bar updates
5. Each step is logged with instance number

---

### Step 8: Monitor Execution

**Watch for:**
- 🎬 Instance X: Starting test on URL
- 📍 Instance X - Step Y: [step text]
- ✅ Instance X - Step Y succeeded
- 🎉 Instance X: Test completed successfully
- 🏁 All parallel tests completed!

**Progress Bar shows:**
- 0% → 50% → 100%
- "2/2 tests completed"

---

### Step 9: Review Results

**Check:**
- Execution log for any errors
- Screenshots saved as:
  - `parallel_test_instance_1.png`
  - `parallel_test_instance_2.png`
- Console output for detailed logs

---

### Step 10: Stop Server (When Done)

```
In the terminal window:
Press: Ctrl+C
```

**Expected Output:**
```
^C
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [PID]
```

---

## 🎯 Decision Flow Chart

```
┌─────────────────────────────────────────────────────────────┐
│              Need to Start Server?                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    Is this first time?
                            │
                ┌───────────┴───────────┐
               YES                      NO
                │                        │
                ↓                        ↓
        setup_and_start.bat    Is server already running?
                                        │
                            ┌───────────┴───────────┐
                           YES                      NO
                            │                        │
                            ↓                        ↓
                    kill_and_start.bat      start_real_test.bat
                            │                        │
                            └───────────┬────────────┘
                                        ↓
┌─────────────────────────────────────────────────────────────┐
│                  SERVER IS RUNNING                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    Choose your task:
                            │
        ┌───────────────────┼───────────────────┐
        ↓                   ↓                   ↓
  Single Test       Parallel Tests      Configuration
        │                   │                   │
        ↓                   ↓                   ↓
localhost:8888    /parallel-execution    /api/...
```

---

## 🔄 Common Workflows

### Workflow 1: Daily Testing

```bash
# Morning: Start server
kill_and_start.bat

# Work: Run tests throughout the day
# (Browser: http://localhost:8888/parallel-execution)

# Evening: Stop server
Ctrl+C
```

---

### Workflow 2: First Time Setup

```bash
# Step 1: Full setup
setup_and_start.bat

# Step 2: Test basic functionality
# Open: http://localhost:8888

# Step 3: Try parallel execution
# Open: http://localhost:8888/parallel-execution

# Step 4: Stop when done
Ctrl+C
```

---

### Workflow 3: After Code Update

```bash
# Step 1: Pull latest code
git pull

# Step 2: Reinstall dependencies
setup_and_start.bat

# Step 3: Test new features
# Open: http://localhost:8888/parallel-execution

# Step 4: Stop server
Ctrl+C
```

---

### Workflow 4: Quick Test

```bash
# Step 1: Quick start (if no server running)
start_real_test.bat

# Step 2: Run quick test
# Open: http://localhost:8888

# Step 3: Stop
Ctrl+C
```

---

### Workflow 5: Troubleshooting

```bash
# Step 1: Check if server is running
netstat -ano | findstr :8888

# Step 2: Kill if needed
taskkill /F /PID <PID>

# Step 3: Fresh start
kill_and_start.bat

# Step 4: Verify
# Open: http://localhost:8888
```

---

## 🎨 Visual Process Map

```
START
  │
  ├─→ [Open Terminal]
  │
  ├─→ [Navigate to Project Directory]
  │     cd C:\Test Automation\Latest\SalesforceAutomationRecorder
  │
  ├─→ [Choose Batch File]
  │     ├─ First time? → setup_and_start.bat
  │     ├─ Daily use? → kill_and_start.bat
  │     └─ Quick test? → start_real_test.bat
  │
  ├─→ [Wait for Server Start]
  │     Look for: "Uvicorn running on http://0.0.0.0:8888"
  │
  ├─→ [Open Browser]
  │     http://localhost:8888
  │
  ├─→ [Choose Mode]
  │     ├─ Single Test → Main Dashboard
  │     └─ Parallel Test → Click "Parallel Execution"
  │
  ├─→ [Configure Tests]
  │     ├─ Set parallel count
  │     ├─ Generate forms
  │     ├─ Fill URLs
  │     ├─ Fill credentials
  │     └─ Enter test steps
  │
  ├─→ [Execute Tests]
  │     Click "Execute All Tests in Parallel"
  │
  ├─→ [Monitor Execution]
  │     ├─ Watch real-time log
  │     ├─ Monitor progress bar
  │     └─ Check for errors
  │
  ├─→ [Review Results]
  │     ├─ Check execution log
  │     ├─ View screenshots
  │     └─ Verify success
  │
  └─→ [Stop Server]
        Press Ctrl+C in terminal
        
END
```

---

## 📊 Parallel Execution Flow

```
USER ACTION                    SYSTEM RESPONSE
───────────                    ───────────────

Enter parallel count (2)
    │
    ├──→ Generate Forms ──────→ Create 2 URL inputs
    │                           Create 2 credential inputs
    │                           Create 2 test step sections
    │
Fill Instance 1 details
Fill Instance 2 details
    │
    ├──→ Click Execute ───────→ Send to backend API
    │                           Create 2 executors
    │                           Start 2 browser sessions
    │
    │                           Instance 1: Start browser
    │                           Instance 2: Start browser
    │                           ↓
    │                           Instance 1: Execute Step 1
    │                           Instance 2: Execute Step 1
    │                           ↓
    │                           Instance 1: Execute Step 2
    │                           Instance 2: Execute Step 2
    │                           ↓
    │                           Instance 1: Complete ✅
    │                           Instance 2: Complete ✅
    │                           ↓
    │                           Take screenshots
    │                           Close browsers
    │                           Send completion message
    │
    └──→ View Results ────────→ Display logs
                                Show progress: 100%
                                Show success message
```

---

## 🛠️ Troubleshooting Flow

```
PROBLEM: Server won't start
    │
    ├─→ Check: Is port 8888 in use?
    │     netstat -ano | findstr :8888
    │     │
    │     ├─→ YES: Kill process
    │     │   taskkill /F /PID <PID>
    │     │   Then: kill_and_start.bat
    │     │
    │     └─→ NO: Check dependencies
    │         pip list | findstr playwright
    │         │
    │         └─→ Missing: setup_and_start.bat

PROBLEM: Dependencies missing
    │
    └─→ Run: setup_and_start.bat
        Wait for completion
        Verify: pip list

PROBLEM: Playwright not found
    │
    └─→ Run: playwright install chromium
        Or: setup_and_start.bat

PROBLEM: Tests failing
    │
    ├─→ Check execution log
    ├─→ Verify URLs are correct
    ├─→ Check test step syntax
    └─→ Review console output
```

---

## 📝 Checklist

### Before Starting
- [ ] Python 3.8+ installed
- [ ] In correct directory
- [ ] Terminal open
- [ ] No other server on port 8888

### Starting Server
- [ ] Choose appropriate batch file
- [ ] Run batch file
- [ ] Wait for "Uvicorn running" message
- [ ] Verify in browser (http://localhost:8888)

### Running Parallel Tests
- [ ] Navigate to parallel execution page
- [ ] Set parallel count
- [ ] Generate forms
- [ ] Fill all URLs
- [ ] Fill credentials (if needed)
- [ ] Enter test steps
- [ ] Click execute
- [ ] Monitor progress

### After Execution
- [ ] Review execution log
- [ ] Check screenshots
- [ ] Verify all tests completed
- [ ] Note any errors
- [ ] Stop server (Ctrl+C)

---

## 🎓 Tips & Best Practices

### Starting Server
✅ Use `kill_and_start.bat` for daily work
✅ Use `setup_and_start.bat` after updates
✅ Check console for error messages
✅ Verify server is accessible

### Running Tests
✅ Start with 2-3 parallel executions
✅ Use descriptive test step names
✅ Monitor system resources
✅ Review logs after execution

### Stopping Server
✅ Always use Ctrl+C when possible
✅ Wait for graceful shutdown
✅ Verify server stopped (netstat)
✅ Kill process only if necessary

---

## 🚀 Quick Commands

```bash
# Start server (daily use)
kill_and_start.bat

# Open parallel execution
start http://localhost:8888/parallel-execution

# Check if running
netstat -ano | findstr :8888

# Stop server
# Press Ctrl+C in terminal

# Kill if stuck
taskkill /F /PID <PID>
```

---

## 📚 Related Documentation

- **PARALLEL_EXECUTION_GUIDE.md** - Complete parallel execution guide
- **START_STOP_GUIDE.md** - Detailed start/stop instructions
- **QUICK_REFERENCE.md** - Quick command reference
- **README.md** - Full project documentation
- **UPDATES_SUMMARY.md** - Recent changes summary

---

**Ready to Start?**

```bash
kill_and_start.bat
```

Then open: http://localhost:8888/parallel-execution

Happy Testing! 🎉
