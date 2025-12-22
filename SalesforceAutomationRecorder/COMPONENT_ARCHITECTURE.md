# 🏗️ Component Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Browser    │  │   CLI Tool   │  │  REST Client │          │
│  │  Dashboard   │  │              │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                    ↕ HTTP / WebSocket
┌─────────────────────────────────────────────────────────────────┐
│                      SERVER LAYER                                │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  FastAPI Server (ui_real_test_server.py)                  │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │  │
│  │  │  WebSocket  │  │  REST API   │  │  Static     │       │  │
│  │  │  Handler    │  │  Endpoints  │  │  Files      │       │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘       │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────────────────────────────┐
│                   ORCHESTRATION LAYER                            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Test Execution Orchestrator                              │  │
│  │  - Executor selection                                     │  │
│  │  - Test lifecycle management                              │  │
│  │  - Result aggregation                                     │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────────────────────────────┐
│                    EXECUTOR LAYER                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐      │
│  │ TestExecutor │  │  Enhanced    │  │  Gemini          │      │
│  │   (Base)     │  │  Executor    │  │  Enhanced        │      │
│  │              │  │              │  │  Executor        │      │
│  │ - Browser    │  │ + Learning   │  │ + AI             │      │
│  │ - Parse      │  │ + Smart      │  │ + Context        │      │
│  │ - Execute    │  │ + Metrics    │  │ + Fallback       │      │
│  └──────────────┘  └──────────────┘  └──────────────────┘      │
│         ↓                  ↓                    ↓                │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Step Parser & Executor Engine                            │  │
│  │  - Natural language parsing                               │  │
│  │  - Action execution (click, fill, verify, etc.)           │  │
│  │  - Wait handling                                          │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────────────────────────────┐
│                   SELECTOR STRATEGY LAYER                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐      │
│  │ Traditional  │  │ Smart        │  │ Gemini AI        │      │
│  │ Selectors    │  │ Locator      │  │ Selector Engine  │      │
│  │              │  │              │  │                  │      │
│  │ - CSS        │  │ - Context    │  │ - API Call       │      │
│  │ - XPath      │  │ - Learning   │  │ - Prompt Eng.    │      │
│  │ - Text       │  │ - Fallback   │  │ - Response Parse │      │
│  │ - Aria       │  │ - Optimize   │  │ - Caching        │      │
│  │ - Placeholder│  │ - Salesforce │  │ - Rate Limit     │      │
│  └──────────────┘  └──────────────┘  └──────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────────────────────────────┐
│                   INTELLIGENCE LAYER                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐      │
│  │ Learning     │  │ Self-Healing │  │ AI Selector      │      │
│  │ System       │  │ Engine       │  │ Engine           │      │
│  │              │  │              │  │                  │      │
│  │ - History    │  │ - Detect     │  │ - Gemini API     │      │
│  │ - Metrics    │  │ - Analyze    │  │ - Context        │      │
│  │ - Optimize   │  │ - Recover    │  │ - Suggest        │      │
│  │ - Feedback   │  │ - Learn      │  │ - Cache          │      │
│  └──────────────┘  └──────────────┘  └──────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────────────────────────────┐
│                      STORAGE LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐      │
│  │ Learning DB  │  │ Config Files │  │ Test Data        │      │
│  │ (JSON)       │  │ (JSON)       │  │ (JSON/TXT)       │      │
│  │              │  │              │  │                  │      │
│  │ - Selectors  │  │ - Browser    │  │ - Steps          │      │
│  │ - Metrics    │  │ - Gemini     │  │ - Examples       │      │
│  │ - History    │  │ - Strategies │  │ - Recordings     │      │
│  └──────────────┘  └──────────────┘  └──────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────────────────────────────┐
│                   BROWSER AUTOMATION LAYER                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Playwright Browser Engine                                │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │  │
│  │  │  Chromium   │  │  Firefox    │  │  WebKit     │       │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘       │  │
│  │  - Page interactions                                      │  │
│  │  - Element location                                       │  │
│  │  - Screenshot capture                                     │  │
│  │  - Network monitoring                                     │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Server Layer

#### **ui_real_test_server.py**
```python
FastAPI Application
├── WebSocket Endpoint (/ws/test)
│   ├── Receive test request
│   ├── Stream logs in real-time
│   └── Send results
├── REST API Endpoints
│   ├── GET / (Dashboard)
│   ├── GET /api/gemini-status
│   ├── GET /api/learning-stats
│   └── POST /api/clear-learning
└── Static File Serving
    └── ui/ directory
```

**Key Functions:**
- `websocket_test()` - Handle WebSocket connections
- `get_gemini_status()` - Check Gemini configuration
- `get_learning_stats()` - Return learning metrics
- `clear_learning_data()` - Reset learned selectors

---

### 2. Executor Layer

#### **Inheritance Hierarchy**

```
TestExecutor (real_test_executor.py)
    ↓
EnhancedTestExecutor (enhanced_test_executor.py)
    ↓
GeminiEnhancedExecutor (gemini_enhanced_executor.py)
```

#### **TestExecutor (Base)**
```python
class TestExecutor:
    # Core functionality
    - start_browser(url, headless)
    - stop_browser()
    - execute_step(step)
    - parse_plain_text_step(step)
    - generate_selectors(target, action)
    
    # Properties
    - page: Playwright page
    - browser: Playwright browser
    - execution_log: List of log entries
    - performance_metrics: Dict of metrics
```

#### **EnhancedTestExecutor**
```python
class EnhancedTestExecutor(TestExecutor):
    # Additional functionality
    - load_learning()
    - save_learning()
    - find_element_with_learning(target, action)
    - parse_plain_text_step(step)  # Enhanced
    
    # Properties
    - learned_selectors: Dict
    - learning_db: Path to JSON file
```

#### **GeminiEnhancedExecutor**
```python
class GeminiEnhancedExecutor(EnhancedTestExecutor):
    # AI functionality
    - find_element_with_ai(target, action)
    - execute_step(step)  # Override with AI
    - log(level, message, data)
    
    # Properties
    - gemini_ai: Gemini AI instance
    - performance_metrics: Extended with AI metrics
```

---

### 3. Selector Strategy Layer

#### **Traditional Selectors (smart_locator.py)**

```python
def generate_selectors(target, action):
    strategies = [
        # 1. Exact text match
        f"text='{target}'",
        
        # 2. Partial text match
        f"text=/{target}/i",
        
        # 3. Aria label
        f"[aria-label='{target}']",
        
        # 4. Placeholder
        f"[placeholder='{target}']",
        
        # 5. Button with text
        f"button:has-text('{target}')",
        
        # 6. Input following label
        f"text='{target}' >> xpath=following::input[1]",
        
        # 7. CSS class
        f".{target.lower().replace(' ', '-')}",
        
        # 8. XPath
        f"//*[contains(text(), '{target}')]"
    ]
    return strategies
```

#### **Smart Locator**

```python
class SmartLocator:
    def locate(self, target, context):
        # 1. Check learned selectors
        if target in learned_db:
            return learned_db[target]
        
        # 2. Analyze context
        context_hints = analyze_context(context)
        
        # 3. Generate strategies
        strategies = generate_with_context(target, context_hints)
        
        # 4. Try each strategy
        for strategy in strategies:
            if element_found(strategy):
                learn(target, strategy)
                return strategy
        
        return None
```

#### **Gemini AI Selector Engine**

```python
class GeminiSelectorAI:
    def find_element(self, page, target, action):
        # 1. Get page HTML
        html = await page.content()
        html_snippet = extract_relevant_html(html, target)
        
        # 2. Build prompt
        prompt = f"""
        You are an expert in web automation.
        
        Page HTML:
        {html_snippet}
        
        Task: Find selector for "{target}" to {action}
        
        Return ONLY the selector.
        """
        
        # 3. Call Gemini API
        response = gemini_model.generate_content(prompt)
        
        # 4. Parse response
        selector = parse_selector(response.text)
        
        # 5. Validate
        if await page.query_selector(selector):
            return selector
        
        return None
```

---

### 4. Intelligence Layer

#### **Learning System**

```python
class LearningSystem:
    def learn(self, target, selector, action):
        # Save successful selector
        learning_db[target] = {
            "selector": selector,
            "action": action,
            "success_count": 1,
            "first_learned": now(),
            "last_used": now()
        }
        save_to_file()
    
    def get_learned(self, target):
        # Retrieve learned selector
        if target in learning_db:
            learning_db[target]["last_used"] = now()
            learning_db[target]["success_count"] += 1
            return learning_db[target]["selector"]
        return None
```

#### **Self-Healing Engine**

```python
class SelfHealingEngine:
    def heal(self, target, failed_selector):
        # 1. Detect failure
        log_failure(target, failed_selector)
        
        # 2. Analyze context
        page_structure = analyze_page()
        similar_elements = find_similar(target)
        
        # 3. Generate alternatives
        alternatives = [
            relax_selector(failed_selector),
            use_alternative_attributes(),
            structural_fallback(),
            ai_suggestion()
        ]
        
        # 4. Test alternatives
        for alt in alternatives:
            if test_selector(alt):
                learn(target, alt)
                return alt
        
        return None
```

---

### 5. Data Flow

#### **Test Execution Flow**

```
1. User Input
   ↓
   Dashboard → WebSocket → Server

2. Server Processing
   ↓
   Parse request → Select executor → Initialize

3. Executor Selection
   ↓
   if use_ai:
       executor = GeminiEnhancedExecutor()
   else:
       executor = EnhancedTestExecutor()

4. Test Execution
   ↓
   for step in test_steps:
       parsed = parse_step(step)
       result = execute_step(parsed)
       log_result(result)
       send_to_dashboard(result)

5. Element Location
   ↓
   Try learned selector
   ↓ (if failed)
   Try traditional selectors
   ↓ (if failed)
   Try Gemini AI
   ↓ (if failed)
   Self-healing attempt
   ↓ (if failed)
   Log error

6. Results
   ↓
   Aggregate metrics → Send to dashboard → Display
```

#### **Selector Resolution Flow**

```
find_element(target, action)
    ↓
┌─────────────────────┐
│ Check Learned DB    │
└─────────────────────┘
    ↓ Found?
    Yes → Return selector
    ↓ No
┌─────────────────────┐
│ Try Traditional     │
│ - CSS               │
│ - XPath             │
│ - Text              │
│ - Aria              │
└─────────────────────┘
    ↓ Found?
    Yes → Learn + Return
    ↓ No
┌─────────────────────┐
│ Consult Gemini AI   │
│ - Build prompt      │
│ - Call API          │
│ - Parse response    │
└─────────────────────┘
    ↓ Found?
    Yes → Learn + Return
    ↓ No
┌─────────────────────┐
│ Self-Healing        │
│ - Relax selector    │
│ - Alternative attrs │
│ - Structural        │
└─────────────────────┘
    ↓ Found?
    Yes → Learn + Return
    ↓ No
    Error → Log + Fail
```

---

## Component Communication

### WebSocket Messages

**Client → Server:**
```json
{
  "test_steps": "Click \"Login\"\nWait for 2 seconds",
  "url": "https://example.com",
  "headless": false,
  "use_ai": true
}
```

**Server → Client:**
```json
{
  "type": "log",
  "level": "info",
  "message": "Executing step 1",
  "timestamp": "2025-11-03T21:00:00"
}

{
  "type": "result",
  "success": true,
  "metrics": {
    "total_time": 5.2,
    "selectors_reused": 3,
    "ai_usage": 0
  }
}
```

### Internal Events

```python
# Event: Element found
event = {
    "type": "element_found",
    "target": "Login",
    "selector": "button:has-text('Login')",
    "method": "traditional",  # or "ai"
    "time_ms": 150
}

# Event: Selector learned
event = {
    "type": "selector_learned",
    "target": "Login",
    "selector": "button:has-text('Login')",
    "action": "click"
}

# Event: AI consulted
event = {
    "type": "ai_consulted",
    "target": "Complex Element",
    "traditional_failed": True,
    "ai_success": True,
    "selector": "[data-id='complex-123']"
}
```

---

## Configuration Flow

```
Application Start
    ↓
Load config.json
    ├── Browser settings
    ├── Selector preferences
    └── Framework patterns
    ↓
Load gemini_config.json
    ├── AI settings
    ├── Strategy config
    └── Performance tuning
    ↓
Check environment variables
    └── GEMINI_API_KEY
    ↓
Initialize components
    ├── Server
    ├── Executors
    ├── Selector engines
    └── Learning system
    ↓
Ready to accept requests
```

---

## Summary

This architecture provides:

✅ **Modularity** - Each component has clear responsibility  
✅ **Extensibility** - Easy to add new executors or strategies  
✅ **Reliability** - Multiple fallback mechanisms  
✅ **Intelligence** - Learning and AI integration  
✅ **Performance** - Optimized selector reuse  
✅ **Monitoring** - Real-time metrics and logging  

The system is designed to be:
- **Maintainable** - Clear separation of concerns
- **Scalable** - Can handle complex test scenarios
- **Intelligent** - Learns and adapts over time
- **User-friendly** - Modern dashboard interface
