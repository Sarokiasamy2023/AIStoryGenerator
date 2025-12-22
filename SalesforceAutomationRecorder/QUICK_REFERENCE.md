# Quick Reference Card

## Starting the Server

### 🚀 Quick Start (Recommended)
```bash
kill_and_start.bat
```
**Use this for:** Daily work, quick restarts

### 🔧 First Time Setup
```bash
setup_and_start.bat
```
**Use this for:** Initial setup, after updates

### ⚡ Simple Start
```bash
start_real_test.bat
```
**Use this for:** When no server is running

## Stopping the Server

```bash
Ctrl+C  # In the terminal window
```

Or restart with:
```bash
kill_and_start.bat
```

## Access URLs

| Page | URL |
|------|-----|
| Main Dashboard | http://localhost:8888 |
| Parallel Execution | http://localhost:8888/parallel-execution |

## Common Commands

### Check if Server is Running
```bash
netstat -ano | findstr :8888
```

### Kill Process Manually
```bash
# Find PID first
netstat -ano | findstr :8888

# Kill it (replace <PID> with actual number)
taskkill /F /PID <PID>
```

### Clear Learned Selectors
```bash
python clear_learning.py
```

### Check Gemini AI Status
```bash
python check_gemini_status.py
```

## Parallel Execution Quick Steps

1. **Start Server**: `kill_and_start.bat`
2. **Open Browser**: http://localhost:8888/parallel-execution
3. **Set Count**: Enter number of parallel executions
4. **Generate Forms**: Click "Generate Forms"
5. **Fill Details**: 
   - URLs
   - Credentials (optional)
   - Test steps
6. **Execute**: Click "Execute All Tests in Parallel"
7. **Monitor**: Watch real-time log and progress

## Test Step Examples

```
# Fill fields
fill search with Playwright automation
fill username with test@example.com

# Click buttons
click Google Search button
click login button

# Wait
wait for 2 seconds
wait for 5 seconds

# Type (alternative syntax)
Type "test@example.com" into "Username"
Type "password123" into "Password"
Click "Log in"
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 8888 in use | `kill_and_start.bat` |
| Dependencies missing | `setup_and_start.bat` |
| Playwright not found | `playwright install chromium` |
| Encoding errors | Already fixed in code |
| Server won't stop | `taskkill /F /PID <PID>` |

## File Locations

| Item | Location |
|------|----------|
| Screenshots | `parallel_test_instance_<N>.png` |
| Learned selectors | `test_learning.json` |
| Logs | Console output |
| Configuration | `config.json` |

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+C` | Stop server |
| `Ctrl+Shift+R` | Refresh browser (hard) |
| `F12` | Open browser DevTools |

## Tips

✅ **DO:**
- Use `kill_and_start.bat` for daily restarts
- Start with 2-3 parallel executions
- Monitor system resources
- Review logs after execution
- Use descriptive test step names

❌ **DON'T:**
- Run too many parallel tests (>10)
- Forget to stop previous server
- Use special characters in passwords
- Skip dependency installation

## Support Files

- `PARALLEL_EXECUTION_GUIDE.md` - Detailed guide
- `README.md` - Full documentation
- `QUICK_START.md` - Getting started
- `COMPONENT_ARCHITECTURE.md` - Technical details

## Quick Diagnostics

```bash
# Check Python version
python --version

# Check Playwright
playwright --version

# Check pip packages
pip list | findstr playwright

# Test server connectivity
curl http://localhost:8888

# View running processes
tasklist | findstr python
```

## Environment Variables

```bash
# Set Gemini API Key (temporary)
set GEMINI_API_KEY=your_api_key_here

# Set permanently (Windows)
setx GEMINI_API_KEY "your_api_key_here"
```

## Common Scenarios

### Scenario 1: Fresh Start
```bash
setup_and_start.bat
```

### Scenario 2: Daily Use
```bash
kill_and_start.bat
```

### Scenario 3: Server Stuck
```bash
netstat -ano | findstr :8888
taskkill /F /PID <PID>
kill_and_start.bat
```

### Scenario 4: Update Code
```bash
git pull
setup_and_start.bat
```

## Performance Tips

- **Parallel Count**: Start with 2-3, max 10
- **Headless Mode**: Faster but no visual feedback
- **Wait Times**: Use appropriate waits (2-5 seconds)
- **System Resources**: Monitor CPU/Memory usage
- **Screenshots**: Saved automatically per instance

## Need Help?

1. Check execution log
2. Review console output
3. Verify dependencies installed
4. Ensure port 8888 available
5. Check `PARALLEL_EXECUTION_GUIDE.md`
6. Review error messages carefully

---

**Last Updated:** November 2025
**Version:** 2.0 (with Parallel Execution)
