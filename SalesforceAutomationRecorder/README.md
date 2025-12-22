# Salesforce Automation Recorder

A powerful web automation tool for recording user interactions on Salesforce Lightning and OmniScript applications.

## Features

- 🎯 **Smart Element Detection**: Automatically identifies Lightning and OmniScript components
- 📝 **Detailed Capture**: Records selectors, labels, actions, and framework types
- 🎨 **Visual Feedback**: Hover highlighting for clicked elements during recording
- 💾 **JSON Export**: Clean, structured output for automation replay
- 🖥️ **Modern UI**: Intuitive control panel for capture management
- 🔄 **Dynamic Components**: Supports nested and dynamic OmniScript elements
- 🚀 **Parallel Execution**: Run multiple tests simultaneously across different URLs
- 🧠 **Selector Learning**: Automatically learns and reuses successful selectors
- 🤖 **AI Enhancement**: Optional Gemini AI integration for smart element detection

## Architecture

The tool consists of three main components:

1. **JavaScript Content Script** (`recorder.js`): Injected into the browser to capture click events and analyze DOM elements
2. **Python Playwright Framework** (`automation_recorder.py`): Orchestrates browser automation and manages recording sessions
3. **Web UI** (`ui/index.html`): Control panel for starting/stopping capture and viewing results

## Installation

### Prerequisites

- Python 3.8+
- Node.js (optional, for standalone testing)

### Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

## Quick Start

### Starting the Server

**Option 1: Quick Restart (Recommended)**
```bash
kill_and_start.bat
```
Kills any existing server on port 8888 and starts fresh.

**Option 2: Full Setup (First Time)**
```bash
setup_and_start.bat
```
Installs dependencies, Playwright browser, and starts the server.

**Option 3: Simple Start**
```bash
start_real_test.bat
```
Starts the server without killing existing processes.

### Accessing the Application

Once the server is running:
- **Main Dashboard**: http://localhost:8888
- **Parallel Execution**: http://localhost:8888/parallel-execution

### Stopping the Server

Press `Ctrl+C` in the terminal window or run `kill_and_start.bat` to restart.

## Usage

### Basic Recording

```python
from automation_recorder import SalesforceRecorder

# Initialize recorder
recorder = SalesforceRecorder()

# Start recording session
recorder.start_recording("https://your-salesforce-instance.lightning.force.com")

# Recording will continue until you click "Stop Capture" in the UI
# or call recorder.stop_recording()

# Export captured data
recorder.export_json("captured_interactions.json")
```

### Parallel Test Execution

1. Navigate to http://localhost:8888/parallel-execution
2. Set the number of parallel executions (1-10)
3. Click "Generate Forms"
4. Fill in URL, credentials, and test steps for each instance
5. Click "Execute All Tests in Parallel"

See [PARALLEL_EXECUTION_GUIDE.md](PARALLEL_EXECUTION_GUIDE.md) for detailed instructions.

### Command Line

```bash
# Start recording with UI
python automation_recorder.py --url "https://your-salesforce-instance.lightning.force.com"

# Start recording with custom output file
python automation_recorder.py --url "https://your-salesforce-instance.lightning.force.com" --output "my_recording.json"
```

## Output Format

```json
[
  {
    "timestamp": "2025-10-21T13:15:30.123Z",
    "label": "Next",
    "action": "click",
    "selector": "button.slds-button.next",
    "xpath": "//button[@class='slds-button next']",
    "framework": "Lightning",
    "componentType": "button",
    "innerText": "Next",
    "attributes": {
      "class": "slds-button next",
      "type": "button"
    }
  },
  {
    "timestamp": "2025-10-21T13:15:35.456Z",
    "label": "Customer Name",
    "action": "input",
    "selector": "input[data-omnistudio-field='CustomerName']",
    "xpath": "//input[@data-omnistudio-field='CustomerName']",
    "framework": "OmniScript",
    "componentType": "input",
    "innerText": "",
    "attributes": {
      "data-omnistudio-field": "CustomerName",
      "type": "text"
    }
  }
]
```

## Framework Detection Logic

### Lightning Components
- Checks for `lightning-*` tags
- Looks for `slds-*` CSS classes (Salesforce Lightning Design System)
- Identifies `data-aura-*` or `data-lightning-*` attributes

### OmniScript Components
- Detects `c-omniscript-*` tags
- Looks for `data-omnistudio-*` attributes
- Identifies `vlocity_*` or `omnistudio-*` class patterns

## Future Automation

The captured JSON can be used to:
1. Generate automated test scripts
2. Create AI-powered automation workflows
3. Build regression test suites
4. Document user journeys

## Project Structure

```
SalesforceAutomationRecorder/
├── automation_recorder.py      # Main Python orchestrator
├── recorder.js                 # Browser injection script
├── ui/
│   ├── index.html             # Control panel UI
│   ├── styles.css             # UI styling
│   └── app.js                 # UI logic
├── requirements.txt           # Python dependencies
├── config.json               # Configuration settings
└── README.md                 # This file
```

## Advanced Features

### Hover Highlighting
Elements are highlighted with a colored border when hovered during recording mode.

### Dynamic Component Support
Automatically handles dynamically loaded OmniScript steps and Lightning components.

### Smart Selector Generation
Generates multiple selector strategies (CSS, XPath) for robust element identification.

## Available Batch Files

### Server Management

| File | Purpose | When to Use |
|------|---------|-------------|
| `kill_and_start.bat` | Kill existing server and start fresh | Quick restart, server already running |
| `setup_and_start.bat` | Full setup with dependencies | First time, after updates |
| `start_real_test.bat` | Simple start | Quick testing, no conflicts |
| `start_server.bat` | Start automation recorder server | Recording mode |
| `start_server_with_gemini.bat` | Start with Gemini AI enabled | AI-enhanced testing |

### Configuration

| File | Purpose |
|------|---------|
| `setup_gemini.bat` | Configure Gemini API key |
| `setup_credentials.bat` | Set up login credentials |
| `set_api_key.bat` | Set API key environment variable |

### Utilities

| File | Purpose |
|------|---------|
| `clear_learning.py` | Clear learned selectors |
| `check_gemini_status.py` | Verify Gemini AI configuration |
| `view_gemini_logs.py` | View AI interaction logs |

## Troubleshooting

### Server Won't Start
```bash
# Kill existing process and restart
kill_and_start.bat
```

### Dependencies Missing
```bash
# Run full setup
setup_and_start.bat
```

### Port Already in Use
```bash
# Check what's using port 8888
netstat -ano | findstr :8888

# Kill the process (replace PID)
taskkill /F /PID <PID>
```

## Documentation

- [PARALLEL_EXECUTION_GUIDE.md](PARALLEL_EXECUTION_GUIDE.md) - Comprehensive guide for parallel testing
- [QUICK_START.md](QUICK_START.md) - Quick start guide
- [COMPONENT_ARCHITECTURE.md](COMPONENT_ARCHITECTURE.md) - Architecture details

## Contributing

This tool is designed to be extended. Future enhancements could include:
- Support for additional Salesforce frameworks
- AI-powered action prediction
- Automated test script generation
- Integration with CI/CD pipelines

## License

MIT License
