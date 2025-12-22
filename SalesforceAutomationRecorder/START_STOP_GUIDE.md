# Server Start & Stop Guide

## Overview

This guide explains how to start and stop the Salesforce Automation Recorder server using the provided batch files.

---

## Starting the Server

### Method 1: kill_and_start.bat (RECOMMENDED)

**Best for:** Daily use, quick restarts, when server is already running

```bash
kill_and_start.bat
```

**What it does:**
1. ✅ Finds any process using port 8888
2. ✅ Kills the process forcefully
3. ✅ Waits 2 seconds
4. ✅ Sets Gemini API key
5. ✅ Starts fresh server on port 8888

**Output:**
```
======================================================================
  Killing processes on port 8888 and starting fresh
======================================================================

Stopping any process on port 8888...
  Killing PID: 12345
  Done

Setting Gemini API Key...
  API Key: SET

======================================================================
  Starting Server on Port 8888
======================================================================

[OK] Google Gemini enabled!
INFO:     Started server process [67890]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8888 (Press CTRL+C to quit)
```

---

### Method 2: setup_and_start.bat

**Best for:** First time setup, after code updates, dependency changes

```bash
setup_and_start.bat
```

**What it does:**
1. ✅ Installs Python dependencies from requirements.txt
2. ✅ Installs Playwright Chromium browser
3. ✅ Kills any existing process on port 8888
4. ✅ Sets Gemini API key
5. ✅ Starts server on port 8888

**Output:**
```
======================================================================
  Salesforce Automation Recorder - Full Setup and Start
======================================================================

[1/3] Installing Python dependencies...
======================================================================
Collecting playwright==1.40.0
...
Successfully installed playwright-1.40.0 ...
  Python dependencies installed successfully

[2/3] Installing Playwright Chromium...
======================================================================
Downloading Chromium...
...
  Playwright Chromium installed successfully

[3/3] Killing any existing server sessions on port 8888...
======================================================================
  Killing PID: 12345
  Existing sessions terminated

Setting Gemini API Key...
  API Key: SET

======================================================================
  Starting New Server Session on Port 8888
======================================================================

Server will be available at: http://localhost:8888
Press Ctrl+C to stop the server

[OK] Google Gemini enabled!
INFO:     Started server process [67890]
INFO:     Uvicorn running on http://0.0.0.0:8888 (Press CTRL+C to quit)
```

---

### Method 3: start_real_test.bat

**Best for:** Quick testing when no server is running

```bash
start_real_test.bat
```

**What it does:**
1. ✅ Starts server on port 8888
2. ❌ Does NOT kill existing processes
3. ❌ Does NOT install dependencies

**Output:**
```
============================================================
  Real Test Execution with Learning and Playback
============================================================

Features:
 - Write tests in plain text
 - Watch real browser execution
 - Automatic selector learning
 - Selector reuse on 2nd run
 - Live execution view

Dashboard: http://localhost:8888

Press Ctrl+C to stop
============================================================

[OK] Google Gemini enabled!
INFO:     Started server process [67890]
INFO:     Uvicorn running on http://0.0.0.0:8888 (Press CTRL+C to quit)
```

---

## Stopping the Server

### Method 1: Keyboard Interrupt (RECOMMENDED)

**In the terminal window where server is running:**

```
Press: Ctrl+C
```

**Output:**
```
^C
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [67890]
```

---

### Method 2: Kill Process Manually

**Step 1: Find the process**
```bash
netstat -ano | findstr :8888
```

**Output:**
```
TCP    0.0.0.0:8888           0.0.0.0:0              LISTENING       12345
```

**Step 2: Kill the process**
```bash
taskkill /F /PID 12345
```

**Output:**
```
SUCCESS: The process with PID 12345 has been terminated.
```

---

### Method 3: Use kill_and_start.bat

Running `kill_and_start.bat` automatically kills any existing server before starting a new one.

```bash
kill_and_start.bat
```

---

## Decision Tree

```
Need to start server?
│
├─ First time setup? ──────────────────────► setup_and_start.bat
│
├─ After code update? ─────────────────────► setup_and_start.bat
│
├─ Dependencies changed? ──────────────────► setup_and_start.bat
│
├─ Server already running? ────────────────► kill_and_start.bat
│
├─ Daily work / Quick restart? ────────────► kill_and_start.bat
│
└─ Quick test (no conflicts)? ─────────────► start_real_test.bat
```

---

## Verification

### Check if Server is Running

```bash
netstat -ano | findstr :8888
```

**If running:**
```
TCP    0.0.0.0:8888           0.0.0.0:0              LISTENING       12345
```

**If not running:**
```
(no output)
```

### Test Server Connectivity

**Open browser:**
```
http://localhost:8888
```

**Or use curl:**
```bash
curl http://localhost:8888
```

---

## Common Issues & Solutions

### Issue 1: Port Already in Use

**Error:**
```
ERROR: [Errno 10048] error while attempting to bind on address ('0.0.0.0', 8888)
```

**Solution:**
```bash
kill_and_start.bat
```

---

### Issue 2: Dependencies Not Found

**Error:**
```
ModuleNotFoundError: No module named 'playwright'
```

**Solution:**
```bash
setup_and_start.bat
```

---

### Issue 3: Playwright Browser Not Found

**Error:**
```
playwright._impl._api_types.Error: Executable doesn't exist
```

**Solution:**
```bash
playwright install chromium
# OR
setup_and_start.bat
```

---

### Issue 4: Server Won't Stop

**Solution:**
```bash
# Find PID
netstat -ano | findstr :8888

# Force kill (replace 12345 with actual PID)
taskkill /F /PID 12345
```

---

## Best Practices

### ✅ DO

- Use `kill_and_start.bat` for daily work
- Run `setup_and_start.bat` after pulling code changes
- Check if server is running before starting new instance
- Stop server properly with Ctrl+C
- Monitor console output for errors

### ❌ DON'T

- Run multiple servers on same port
- Close terminal without stopping server
- Ignore error messages
- Skip dependency installation
- Force kill unless necessary

---

## Quick Commands Reference

| Task | Command |
|------|---------|
| **Start (Quick)** | `kill_and_start.bat` |
| **Start (Full Setup)** | `setup_and_start.bat` |
| **Start (Simple)** | `start_real_test.bat` |
| **Stop** | `Ctrl+C` |
| **Check Running** | `netstat -ano \| findstr :8888` |
| **Kill Process** | `taskkill /F /PID <PID>` |
| **Install Browser** | `playwright install chromium` |
| **Install Dependencies** | `pip install -r requirements.txt` |

---

## Server URLs

Once server is running, access:

| Page | URL |
|------|-----|
| Main Dashboard | http://localhost:8888 |
| Parallel Execution | http://localhost:8888/parallel-execution |
| API Status | http://localhost:8888/api/gemini-status |
| Learned Selectors | http://localhost:8888/api/learned-selectors |

---

## Logs & Output

### Server Startup Success

```
============================================================
     Real Test Execution with Learning & Playback
============================================================

Dashboard: http://localhost:8888
Parallel Execution: http://localhost:8888/parallel-execution

Features:
[+] Plain text test steps
[+] Real browser execution
[+] Automatic selector learning
[+] Selector reuse on 2nd run
[+] Live execution view
[+] Parallel test execution

Press Ctrl+C to stop

[OK] Google Gemini enabled!
INFO:     Started server process [67890]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8888 (Press CTRL+C to quit)
```

### Server Shutdown Success

```
^C
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [67890]
```

---

## Environment Setup

### Set Gemini API Key (Optional)

**Temporary (current session):**
```bash
set GEMINI_API_KEY=your_api_key_here
```

**Permanent:**
```bash
setx GEMINI_API_KEY "your_api_key_here"
```

**Or use batch file:**
```bash
setup_gemini.bat
```

---

## Troubleshooting Checklist

- [ ] Python 3.8+ installed?
- [ ] Dependencies installed? (`pip list | findstr playwright`)
- [ ] Playwright browser installed? (`playwright --version`)
- [ ] Port 8888 available? (`netstat -ano | findstr :8888`)
- [ ] No firewall blocking port 8888?
- [ ] Running from correct directory?
- [ ] Terminal has admin rights (if needed)?

---

## Next Steps

After starting the server:

1. **Open browser** → http://localhost:8888
2. **Try basic test** → Use example test steps
3. **Try parallel execution** → http://localhost:8888/parallel-execution
4. **Read guides:**
   - [PARALLEL_EXECUTION_GUIDE.md](PARALLEL_EXECUTION_GUIDE.md)
   - [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
   - [README.md](README.md)

---

**Need Help?**
- Check console output for errors
- Review log messages
- Verify all dependencies installed
- Ensure port 8888 is available
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) (if exists)

---

**Last Updated:** November 2025  
**Version:** 2.0 with Parallel Execution
