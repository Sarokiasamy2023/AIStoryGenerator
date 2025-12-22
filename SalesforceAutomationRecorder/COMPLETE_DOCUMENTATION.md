# 📚 Salesforce Automation Recorder - Complete Documentation

**Version:** 2.0 with Gemini AI  
**Last Updated:** November 3, 2025  
**Status:** Production Ready

---

## 📋 Quick Links

- [Architecture Overview](#architecture-overview)
- [Core Components](#core-components)
- [Gemini AI Integration](#gemini-ai-integration)
- [Installation & Setup](#installation--setup)
- [Usage Guide](#usage-guide)
- [API Reference](#api-reference)

---

## 🎯 Project Overview

### What is it?

A **next-generation test automation framework** for Salesforce that combines:
- Traditional selector strategies (CSS, XPath, text-based)
- AI-powered element location (Google Gemini AI)
- Self-healing capabilities
- Learning system that improves over time
- Real-time UI dashboard with WebSocket monitoring

### Key Features

✅ **Multi-Strategy Element Location**
- CSS selectors, XPath, text-based, aria labels
- AI-powered suggestions via Gemini
- Automatic fallback strategies

✅ **Three Execution Modes**
- Standard: Traditional selectors + learning
- Enhanced: Reuse learned selectors
- Gemini AI: AI-powered intelligent location

✅ **Self-Healing**
- Automatic selector recovery
- Multiple fallback strategies
- Learning from recoveries

✅ **Modern UI Dashboard**
- Real-time execution monitoring
- Live logs via WebSocket
- Performance metrics
- AI usage statistics

---

## 🏗️ Architecture Overview

### System Layers

```
┌─────────────────────────────────────────┐
│  UI Layer (Dashboard - Port 8888)      │
├─────────────────────────────────────────┤
│  Server Layer (FastAPI + WebSocket)    │
├─────────────────────────────────────────┤
│  Execution Layer (3 Executors)         │
│  - TestExecutor (Base)                  │
│  - EnhancedTestExecutor                 │
│  - GeminiEnhancedExecutor               │
├─────────────────────────────────────────┤
│  Selector Strategy Layer                │
│  - Traditional (CSS/XPath/Text)         │
│  - Smart Locator                        │
│  - Gemini AI Selector Engine            │
├─────────────────────────────────────────┤
│  Intelligence Layer                     │
│  - Learning System                      │
│  - Self-Healing Engine                  │
│  - AI Selector Engine                   │
├─────────────────────────────────────────┤
│  Storage Layer                          │
│  - Learning DB (JSON)                   │
│  - Config Files                         │
│  - Test Data                            │
├─────────────────────────────────────────┤
│  Browser Layer (Playwright)            │
└─────────────────────────────────────────┘
```

### Data Flow

```
User clicks "Run Test"
    ↓
WebSocket → Server
    ↓
Select Executor (Standard/Enhanced/Gemini)
    ↓
Parse test steps
    ↓
For each step:
    Try Learned Selectors → Success? Execute
    ↓ (if failed)
    Try Traditional Selectors → Success? Learn + Execute
    ↓ (if failed)
    Try Gemini AI → Success? Learn + Execute
    ↓ (if failed)
    Log Error
    ↓
Return Results + Metrics → WebSocket → Dashboard
```

---

## 🔧 Core Components

### 1. Test Executors

#### **real_test_executor.py** (Base)
- Browser management
- Basic step parsing
- Traditional selectors
- Performance metrics

#### **enhanced_test_executor.py**
- Extends base executor
- Selector learning system
- Reuse learned selectors
- Enhanced parsing (multiple formats)

**Supported formats:**
```
Type "value" into "Field"
fill Field with value
Click "Button"
Wait for X seconds
Select "option" from Dropdown "Field"
Check "Checkbox"
Verify "Text" is visible
```

#### **gemini_enhanced_executor.py**
- AI-powered element location
- Inherits from EnhancedTestExecutor
- Gemini AI integration
- AI usage metrics

**Decision flow:**
1. Try learned selectors (fastest)
2. Try traditional selectors (reliable)
3. If all fail → Consult Gemini AI
4. Learn successful selector

### 2. Selector Engines

#### **smart_locator.py**
- Multiple strategy generation
- Context-aware selection
- Salesforce-specific patterns

**Strategies:**
- Exact text match
- Partial text match
- Aria labels
- Placeholder attributes
- CSS classes
- XPath expressions
- Data attributes

#### **gemini_selector_ai.py**
- Gemini API integration
- Context-aware prompts
- Response parsing
- Caching & rate limiting

### 3. UI Server

#### **ui_real_test_server.py**
FastAPI server with WebSocket support.

**Endpoints:**
```
WebSocket: /ws/test
GET: /
GET: /api/gemini-status
GET: /api/learning-stats
POST: /api/clear-learning
```

### 4. Dashboard

#### **ui/real_test_dashboard.html**
Modern web interface with:
- Test input textarea
- Three execution buttons
- Live log streaming
- Performance metrics
- AI usage statistics
- Connection status

---

## 🤖 Gemini AI Integration

### Overview

Gemini AI provides intelligent element location when traditional methods fail.

### Components

**gemini_selector_ai.py** - Main AI module
- Google Gemini API integration
- Context-aware prompts
- Response parsing
- Error handling

**gemini_enhanced_executor.py** - AI executor
- Uses Gemini when needed
- Tracks AI usage metrics
- Learns from AI suggestions

**gemini_config.json** - Configuration
```json
{
  "gemini_ai": {
    "enabled": true,
    "model": "gemini-pro",
    "max_retries": 3,
    "timeout_seconds": 30
  },
  "selector_strategies": {
    "use_traditional_first": true,
    "max_traditional_attempts": 10,
    "max_ai_suggestions": 15
  }
}
```

### Setup

1. **Get API Key:**
   - Visit https://makersuite.google.com/app/apikey
   - Create new API key

2. **Set API Key:**
   ```bash
   set_api_key.bat
   ```

3. **Install Dependencies:**
   ```bash
   pip install google-generativeai>=0.3.0
   ```

4. **Verify:**
   ```bash
   python check_gemini_status.py
   ```

### Usage

**From Dashboard:**
1. Start server: `.\kill_and_start.bat`
2. Open: http://localhost:8888
3. Click: 🤖 Run with Gemini AI

**From Code:**
```python
from gemini_enhanced_executor import GeminiEnhancedExecutor

executor = GeminiEnhancedExecutor()
await executor.start_browser("https://example.com")
await executor.execute_step('Click "Submit"')
```

### When Gemini is Used

Gemini AI is consulted when:
- ❌ Learned selector not found
- ❌ All traditional selectors fail
- ✅ Gemini AI is enabled
- ✅ API key is configured

### Benefits

✅ Handles complex elements (dynamic IDs, Shadow DOM)  
✅ Context-aware (understands page structure)  
✅ Learning (AI suggestions are saved)  
✅ Fallback safety (traditional methods tried first)  

---

## 📦 Installation & Setup

### Prerequisites

- Python 3.8+
- pip
- Git (optional)

### Step 1: Install Dependencies

```bash
# Core dependencies
pip install -r requirements.txt

# AI dependencies (optional)
pip install -r requirements_ai.txt
```

### Step 2: Install Playwright Browsers

```bash
playwright install chromium
```

### Step 3: Configure Gemini AI (Optional)

```bash
# Set API key
set_api_key.bat

# Or manually
set GEMINI_API_KEY=your_api_key_here
```

### Step 4: Verify Installation

```bash
# Check Gemini status
python check_gemini_status.py

# Start server
.\kill_and_start.bat
```

### Step 5: Open Dashboard

```
http://localhost:8888
```

---

## 📖 Usage Guide

### Quick Start

1. **Start Server:**
   ```bash
   .\kill_and_start.bat
   ```

2. **Open Dashboard:**
   ```
   http://localhost:8888
   ```

3. **Enter Test Steps:**
   ```
   Type "https://login.salesforce.com" into "URL"
   Click "Go"
   Wait for 2 seconds
   Type "user@example.com" into "Username"
   Type "password" into "Password"
   Click "Log in"
   ```

4. **Click Run:**
   - ▶️ Green: Standard execution
   - 🔄 Blue: Enhanced with learning
   - 🤖 Purple: With Gemini AI

### Execution Modes

#### Standard Mode (Green Button)
- Uses traditional selectors
- Learns successful selectors
- No AI

**Use when:** First time running test

#### Enhanced Mode (Blue Button)
- Reuses learned selectors
- Fast execution
- No AI

**Use when:** Re-running known tests

#### Gemini AI Mode (Purple Button)
- Traditional + AI
- Smart fallback
- Learning enabled

**Use when:** Complex elements, traditional failing

### Test Step Formats

**Fill/Type:**
```
Type "value" into "Field"
fill Field with value
```

**Click:**
```
Click "Button Text"
```

**Wait:**
```
Wait for 2 seconds
```

**Select:**
```
Select "Option" from Dropdown "Field"
```

**Checkbox:**
```
Check "Checkbox Label"
```

**Verify:**
```
Verify "Text" is visible
```

### Performance Metrics

After execution, view:
- ⏱️ Total Time
- 🔄 Selectors Reused
- 🧠 Selectors Learned
- 📊 Reuse Efficiency
- 🤖 Gemini AI Usage
- 💡 AI Suggestions Used

---

## 🔌 API Reference

### WebSocket API

**Endpoint:** `ws://localhost:8888/ws/test`

**Send Message:**
```json
{
  "test_steps": "Click \"Login\"\nWait for 2 seconds",
  "url": "https://example.com",
  "headless": false,
  "use_ai": false
}
```

**Receive Messages:**
```json
{
  "type": "log",
  "level": "info",
  "message": "Step executed",
  "timestamp": "2025-11-03T21:00:00"
}
```

### REST API

**Get Gemini Status:**
```
GET /api/gemini-status
```

Response:
```json
{
  "enabled": true,
  "api_key_set": true,
  "model": "gemini-pro"
}
```

**Get Learning Stats:**
```
GET /api/learning-stats
```

Response:
```json
{
  "total_selectors": 45,
  "total_uses": 475,
  "most_used": [...]
}
```

**Clear Learning Data:**
```
POST /api/clear-learning
```

---

## 📁 File Structure

```
SalesforceAutomationRecorder/
├── Core Executors
│   ├── real_test_executor.py          # Base executor
│   ├── enhanced_test_executor.py      # Enhanced with learning
│   └── gemini_enhanced_executor.py    # AI-powered
│
├── Selector Engines
│   ├── smart_locator.py               # Smart selector generation
│   ├── ai_selector_engine.py          # AI analysis
│   └── gemini_selector_ai.py          # Gemini integration
│
├── Intelligence
│   ├── learning_feedback_system.py    # Learning system
│   ├── self_healing_engine.py         # Self-healing
│   └── auto_healer.py                 # Auto-healing
│
├── Server & UI
│   ├── ui_real_test_server.py         # FastAPI server
│   └── ui/
│       ├── real_test_dashboard.html   # Main dashboard
│       ├── app.js                     # Dashboard JS
│       └── styles.css                 # Styles
│
├── Configuration
│   ├── config.json                    # Main config
│   ├── gemini_config.json             # Gemini config
│   ├── requirements.txt               # Core dependencies
│   └── requirements_ai.txt            # AI dependencies
│
├── Utilities
│   ├── check_gemini_status.py         # Check Gemini
│   ├── view_gemini_logs.py            # View logs
│   └── clear_learning.py              # Clear learning
│
├── Batch Scripts
│   ├── kill_and_start.bat             # Start server
│   ├── set_api_key.bat                # Set API key
│   └── setup_gemini.bat               # Setup Gemini
│
└── Data
    ├── test_learning.json             # Learned selectors
    └── tests/                         # Test files
```

---

## 🛠️ Development Guide

### Adding New Selector Strategy

1. Edit `smart_locator.py`
2. Add strategy to `generate_selectors()`
3. Test with sample elements

### Extending Executor

```python
from enhanced_test_executor import EnhancedTestExecutor

class CustomExecutor(EnhancedTestExecutor):
    async def execute_step(self, step):
        # Custom logic
        return await super().execute_step(step)
```

### Adding Dashboard Features

1. Edit `ui/real_test_dashboard.html`
2. Add UI elements
3. Update WebSocket message handling
4. Test real-time updates

---

## 🐛 Troubleshooting

### Server Won't Start

**Error:** Port already in use

**Solution:**
```bash
netstat -ano | findstr :8888
taskkill /F /PID <PID>
.\kill_and_start.bat
```

### Gemini AI Not Working

**Check:**
```bash
python check_gemini_status.py
```

**Fix:**
```bash
set_api_key.bat
```

### Dashboard Shows "Disconnected"

**Solution:**
1. Restart server
2. Refresh browser
3. Check server logs

### Step Parse Error

**Error:** "Could not parse step"

**Fix:** Check step format:
```
✅ Type "value" into "Field"
✅ fill Field with value
❌ type Field value (missing format)
```

---

## 📊 Performance Tips

1. **Use Enhanced Mode** for repeated tests
2. **Let system learn** on first run
3. **Use Gemini AI** only when needed
4. **Clear learning** if selectors change
5. **Monitor metrics** to optimize

---

## 🔐 Security

- API keys stored in environment variables
- No credentials in code
- Use `.gitignore` for sensitive files
- Secure WebSocket connections

---

## 📝 License

[Your License Here]

---

## 👥 Contributors

[Your Team Here]

---

## 📞 Support

For issues or questions:
- Check troubleshooting section
- Review logs in server console
- Check Gemini status
- Verify configuration files

---

**Last Updated:** November 3, 2025  
**Version:** 2.0 with Gemini AI Integration
