# Port 8888 Conflict Fix

## Problem

**Error Message:**
```
ERROR: [Errno 10048] error while attempting to bind on address ('0.0.0.0', 8888): 
[winerror 10048] only one usage of each socket address (protocol/network address/port) 
is normally permitted
```

**Root Cause:**
The old `kill_and_start.bat` script was not reliably killing all processes using port 8888. The `taskkill` command sometimes failed to terminate Python processes, leaving the port occupied.

---

## Solution

Updated both `kill_and_start.bat` and `setup_and_start.bat` to use **PowerShell** for more reliable process termination.

### What Changed

**Old Method (Unreliable):**
```batch
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8888 2^>nul') do (
    echo   Killing PID: %%a
    taskkill /F /PID %%a >nul 2>&1
)
```

**New Method (Reliable):**
```batch
powershell -Command "$pids = (Get-NetTCPConnection -LocalPort 8888 -ErrorAction SilentlyContinue).OwningProcess | Select-Object -Unique; if ($pids) { $pids | ForEach-Object { Write-Host '  Killing PID:' $_; Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue } } else { Write-Host '  No process found on port 8888' }"
```

### Why PowerShell is Better

1. **More Reliable**: `Stop-Process -Force` is more effective than `taskkill`
2. **Better Error Handling**: `-ErrorAction SilentlyContinue` prevents script failures
3. **Unique PIDs**: Automatically filters duplicate PIDs
4. **Direct Port Query**: Uses `Get-NetTCPConnection` to find processes by port

---

## Files Updated

1. **kill_and_start.bat**
   - Updated process killing logic
   - Increased wait time from 2 to 3 seconds

2. **setup_and_start.bat**
   - Updated process killing logic
   - Increased wait time from 2 to 3 seconds

3. **force_kill_port_8888.bat** (NEW)
   - Emergency script to force kill port 8888
   - Use if regular scripts fail

---

## How to Use

### Normal Usage
```bash
# This should now work reliably
kill_and_start.bat
```

### If Port Still Stuck
```bash
# Use the emergency kill script
force_kill_port_8888.bat

# Then start normally
kill_and_start.bat
```

### Manual PowerShell Command
```powershell
# Kill all processes on port 8888
Get-NetTCPConnection -LocalPort 8888 -ErrorAction SilentlyContinue | 
    Select-Object -ExpandProperty OwningProcess -Unique | 
    ForEach-Object { Stop-Process -Id $_ -Force }
```

---

## Verification

### Check if Port is Free
```bash
netstat -ano | findstr :8888
```

**Expected Output (port free):**
```
(no output)
```

**If port is in use:**
```
TCP    0.0.0.0:8888           0.0.0.0:0              LISTENING       12345
```

### Check Running Python Processes
```powershell
Get-Process python -ErrorAction SilentlyContinue
```

---

## Troubleshooting

### Problem: Script says "No process found" but port still in use

**Solution:**
```powershell
# Find the process manually
netstat -ano | findstr :8888

# Kill by PID (replace 12345 with actual PID)
Stop-Process -Id 12345 -Force
```

### Problem: "Access Denied" when killing process

**Solution:**
Run PowerShell or Command Prompt as **Administrator**

### Problem: Port immediately occupied after killing

**Possible Causes:**
1. Another application is using port 8888
2. Windows is holding the port in TIME_WAIT state
3. Antivirus is blocking the operation

**Solutions:**
```powershell
# Check what's using the port
Get-NetTCPConnection -LocalPort 8888 | 
    Select-Object State, OwningProcess, 
    @{Name="ProcessName";Expression={(Get-Process -Id $_.OwningProcess).ProcessName}}

# Change the port in ui_real_test_server.py
# Edit line: run_server(port=9000)  # Use different port
```

---

## Prevention

### Best Practices

1. **Always use kill_and_start.bat** instead of manually starting the server
2. **Stop server properly** with Ctrl+C before closing terminal
3. **Don't force close** terminal windows with running servers
4. **Check port status** before starting: `netstat -ano | findstr :8888`

### Alternative: Use Different Port

If port 8888 is frequently occupied, change the default port:

**Edit `ui_real_test_server.py`:**
```python
if __name__ == "__main__":
    run_server(port=9000)  # Change to any available port
```

**Update batch files** to reflect new port number.

---

## Technical Details

### PowerShell Command Breakdown

```powershell
# Get all TCP connections on port 8888
Get-NetTCPConnection -LocalPort 8888 -ErrorAction SilentlyContinue

# Extract unique process IDs
| Select-Object -ExpandProperty OwningProcess -Unique

# Kill each process
| ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
```

### Why taskkill Failed

1. **Timing Issues**: Process may not terminate immediately
2. **Child Processes**: Python may spawn child processes
3. **Handle Locks**: File or socket handles may prevent termination
4. **Permission Issues**: Some processes require elevated privileges

### PowerShell Advantages

- **Force Flag**: `-Force` parameter ensures termination
- **Error Suppression**: Continues even if some PIDs are invalid
- **Native Integration**: Better Windows process management
- **Unique Filtering**: Automatically handles duplicate PIDs

---

## Testing

### Test the Fix

1. **Start server:**
   ```bash
   kill_and_start.bat
   ```

2. **Verify running:**
   ```bash
   netstat -ano | findstr :8888
   ```

3. **Kill and restart:**
   ```bash
   # Press Ctrl+C in server terminal
   # Then run:
   kill_and_start.bat
   ```

4. **Should start successfully without errors**

---

## Emergency Recovery

### If Everything Fails

```powershell
# Nuclear option: Kill all Python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Wait a moment
Start-Sleep -Seconds 3

# Verify port is free
Get-NetTCPConnection -LocalPort 8888 -ErrorAction SilentlyContinue

# Start server
.\kill_and_start.bat
```

**⚠️ Warning:** This kills ALL Python processes, including other Python applications!

---

## Status

✅ **Fixed** - Both batch files updated with PowerShell commands  
✅ **Tested** - Server starts successfully after fix  
✅ **Documented** - Complete troubleshooting guide created  

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `kill_and_start.bat` | Kill port 8888 and start server |
| `force_kill_port_8888.bat` | Emergency kill script |
| `netstat -ano \| findstr :8888` | Check if port is in use |
| `Stop-Process -Id <PID> -Force` | Kill specific process |
| `Get-NetTCPConnection -LocalPort 8888` | Find processes on port |

---

**Last Updated:** November 18, 2025  
**Status:** ✅ Resolved  
**Version:** 2.1
