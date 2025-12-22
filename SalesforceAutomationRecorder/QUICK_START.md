# Quick Start Guide

## One-Command Setup (Recommended)

Run everything at once - installs dependencies, kills old sessions, starts server:
```bash
.\setup_and_start.bat
```

Then open in browser:
```
http://localhost:8888
```

---

## Manual 3-Step Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Start the Server
```bash
.\start_server.bat
```

Or directly:
```bash
python ui_real_test_server.py
```

### 3. Open in Browser
```
http://localhost:8888
```

## That's It! 🎉

You're ready to start recording and running Salesforce automation tests.

---

## Optional: Set Gemini API Key

For AI-powered features, set your API key:

**Windows (Command Prompt):**
```bash
set GEMINI_API_KEY=your_api_key_here
```

**Windows (PowerShell):**
```bash
$env:GEMINI_API_KEY="your_api_key_here"
```

Get your API key from: https://makersuite.google.com/app/apikey

---

## New Features

### 📤 File Upload Support
Upload files to your Salesforce forms:
```
Upload "path/to/document.pdf" to "Resume Upload"
```

### 📝 Textarea Support
Fill multi-line text fields:
```
Fill textarea "Description" with "Your long text content here"
```

See `UPLOAD_AND_TEXTAREA_GUIDE.md` for detailed examples and usage.

---

## Need More Help?

See `SETUP_GUIDE.md` for detailed instructions.
