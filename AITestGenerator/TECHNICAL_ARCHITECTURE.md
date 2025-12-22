# AI Test Generator - Technical Architecture & Implementation Guide

## Overview

This document explains how the AI Test Generator was built, the technologies used, the AI models integrated, and the complete code architecture.

---

## 🏗️ System Architecture

### **High-Level Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (UI)                         │
│  - index.html (Test Case Generator)                         │
│  - gherkin.html (Gherkin to Steps Converter)                │
│  - app.js (Client-side logic)                               │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTP/REST API
┌─────────────────────────────────────────────────────────────┐
│                     Backend (Node.js)                        │
│  - server.js (Express API endpoints)                         │
│  - services/aiService.js (AI integration)                    │
│  - services/storageService.js (Data persistence)             │
└─────────────────────────────────────────────────────────────┘
                            ↓ API Calls
┌─────────────────────────────────────────────────────────────┐
│                    AI Provider (OpenAI)                      │
│  - GPT-4o-mini (Default model)                              │
│  - Chat Completions API                                      │
│  - JSON & Text response formats                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🤖 AI Models Used

### **Primary Model: OpenAI GPT-4o-mini**

**Configuration:**
```javascript
Model: gpt-4o-mini
Temperature: 0.7 (configurable)
Max Tokens: 8000 (increased for detailed outputs)
Response Format: JSON (for test cases/steps) or Text (for Gherkin conversion)
```

**Why GPT-4o-mini?**
- Cost-effective (~60% cheaper than GPT-4)
- Fast response times
- Good at structured output (JSON)
- Handles complex prompts well
- Supports both JSON and text responses

**Alternative Models Supported:**
- Any OpenAI model (gpt-4, gpt-4-turbo, gpt-3.5-turbo)
- Local LLM via Ollama (configurable)
- Fine-tuned models (custom trained)

---

## 📁 Project Structure

```
AITestGenerator/
├── server.js                          # Express server & API endpoints
├── .env                               # Environment configuration
├── package.json                       # Dependencies
│
├── public/                            # Frontend files
│   ├── index.html                     # Main UI (Test Case Generator)
│   ├── gherkin.html                   # Gherkin Converter UI
│   └── app.js                         # Client-side JavaScript
│
├── services/                          # Backend services
│   ├── aiService.js                   # AI integration & prompt engineering
│   └── storageService.js              # Data storage (JSON files)
│
├── templates/                         # Example templates
│   ├── salesforce-automation-template.txt
│   ├── cbd-shcp-template.txt
│   └── user-exact-format-template.txt
│
├── examples/                          # Sample data
│   ├── cbd-shcp-user-story.md
│   ├── cbd-shcp-test-steps.md
│   └── cbd-shcp-automation-steps-example.txt
│
├── output/                            # Generated outputs
│   ├── user-stories/
│   ├── test-cases/
│   └── test-steps/
│
└── docs/                              # Documentation
    ├── GHERKIN_CONVERTER_GUIDE.md
    ├── FINE_TUNING_GUIDE.md
    ├── HOW_TO_GET_DETAILED_STEPS.md
    └── TECHNICAL_ARCHITECTURE.md (this file)
```

---

## 🔧 Technology Stack

### **Backend**
- **Runtime:** Node.js v18+
- **Framework:** Express.js v4.18
- **AI SDK:** OpenAI Node.js SDK v4.0
- **Environment:** dotenv for configuration
- **Storage:** JSON file-based storage

### **Frontend**
- **HTML5** with semantic markup
- **TailwindCSS** for styling
- **Vanilla JavaScript** (ES6+)
- **Font Awesome** for icons

### **AI Integration**
- **OpenAI API** (primary)
- **Ollama** (optional, for local LLMs)
- **Custom fine-tuned models** (supported)

---

## 🔄 Data Flow

### **1. Test Case Generation Flow**

```
User Input (User Story)
    ↓
Frontend (app.js)
    ↓ POST /api/generate-test-cases
Backend (server.js)
    ↓
AI Service (aiService.js)
    ↓ buildTestCasesPrompt()
OpenAI API (GPT-4o-mini)
    ↓ JSON Response
AI Service (parseTestCasesResponse())
    ↓
Storage Service (saveTestCases())
    ↓
Frontend (displayTestCases())
    ↓
User sees generated test cases
```

### **2. Test Steps Generation Flow**

```
User Input (Test Case Details)
    ↓
Frontend (app.js)
    ↓ POST /api/generate-test-steps
Backend (server.js)
    ↓
AI Service (aiService.js)
    ↓ buildTestStepsPrompt()
OpenAI API (GPT-4o-mini)
    ↓ JSON Response
AI Service (parseTestStepsResponse())
    ↓
Storage Service (saveTestSteps())
    ↓
Frontend (displayTestSteps())
    ↓
User sees automation steps
```

### **3. Gherkin Conversion Flow**

```
User Input (Gherkin .feature file)
    ↓
Frontend (gherkin.html)
    ↓ POST /api/gherkin-to-steps
Backend (server.js)
    ↓
AI Service (convertGherkinToSteps())
    ↓ Plain text prompt
OpenAI API (GPT-4o-mini)
    ↓ Text Response
AI Service (parse line by line)
    ↓
Frontend (displaySteps())
    ↓
User sees automation steps
```

---

## 🧠 AI Service Architecture

### **Core Components**

**File:** `services/aiService.js`

```javascript
class AIService {
    constructor() {
        // Initialize OpenAI client
        this.openai = new OpenAI({
            apiKey: process.env.OPENAI_API_KEY
        });
        this.model = process.env.OPENAI_MODEL || 'gpt-4o-mini';
        this.provider = 'openai';
    }

    // Main methods:
    async generateTestCases(userStory, examples)
    async generateTestSteps(testCase, examples)
    async convertGherkinToSteps(gherkinText)
    
    // Helper methods:
    buildTestCasesPrompt(userStory, examples)
    buildTestStepsPrompt(testCase, examples)
    parseTestCasesResponse(response)
    parseTestStepsResponse(response)
    
    // AI calling methods:
    async callAI(prompt, useJsonFormat = true)
    async callOpenAI(prompt, useJsonFormat = true)
    async callLocalLLM(prompt)
}
```

### **Prompt Engineering Strategy**

The system uses **detailed, structured prompts** with:

1. **System Message:** Defines AI role as QA expert
2. **Context:** Provides user story or test case details
3. **Format Rules:** Explicit formatting instructions
4. **Examples:** Shows expected output format
5. **Critical Requirements:** Emphasizes key rules
6. **Output Format:** Specifies JSON or text structure

**Example Prompt Structure:**
```
Generate test cases for the following user story:

[User Story Details]

Generate test cases following these rules:
1. [Rule 1]
2. [Rule 2]
...

EXAMPLES:
[Example 1]
[Example 2]

Return ONLY valid JSON in this format:
{
    "testCases": [...]
}
```

---

## 🎯 Key Features Implementation

### **1. Gherkin to Automation Steps**

**How it works:**
- Accepts any `.feature` file or Gherkin text
- Uses AI to parse and convert Gherkin syntax
- Applies strict formatting rules via prompt engineering
- Outputs in user's exact format

**Key Code:**
```javascript
async convertGherkinToSteps(gherkinText) {
    const prompt = `Convert the following Gherkin scenario...
    
    [Detailed rules for conversion]
    
    EXAMPLES:
    Gherkin: And the user enters "X" into "Y"
    Output: Type "%Y%" into "Y"
    `;
    
    const response = await this.callAI(prompt, false); // Text format
    return response.trim().split('\n').filter(line => line.trim());
}
```

### **2. Custom Format Support**

**Implementation:**
- User can provide example test steps
- Examples are injected into the AI prompt
- AI learns the format from examples
- Consistent output matching user's style

**Key Code:**
```javascript
if (examples) {
    prompt += `\nHere are examples of the expected format:\n${examples}\n`;
}
```

### **3. CSV Placeholder Generation**

**Format:** `%FieldName%` (no quotes inside)

**Implementation:**
- Prompt explicitly instructs AI on CSV format
- Multiple examples showing correct format
- Validation in parsing layer

**Output:**
```
Type "%Username%" into "Username"
Select "%Articles%" from Dropdown "Articles"
Fill textarea "%Comments%" with "Comments"
```

### **4. Wait Statement Injection**

**Rule:** Add `Wait for 1 seconds` after EVERY action

**Implementation:**
- Prompt emphasizes wait statements
- AI trained to add waits automatically
- No post-processing needed

---

## 🔐 Configuration

### **Environment Variables (.env)**

```bash
# Server Configuration
PORT=3000

# OpenAI Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
TEMPERATURE=0.7
MAX_TOKENS=8000

# Optional: Local LLM
LOCAL_LLM_ENDPOINT=http://localhost:11434/api/generate
LOCAL_LLM_MODEL=llama2

# Optional: Other AI Providers
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
```

### **Model Configuration**

**Default Settings:**
```javascript
{
    model: "gpt-4o-mini",
    temperature: 0.7,        // Creativity level (0-1)
    max_tokens: 8000,        // Max response length
    response_format: {
        type: "json_object"  // For structured output
    }
}
```

**For Gherkin Conversion:**
```javascript
{
    model: "gpt-4o-mini",
    temperature: 0.7,
    max_tokens: 8000,
    // No response_format (plain text)
}
```

---

## 🚀 API Endpoints

### **Test Case Generation**
```
POST /api/generate-test-cases
Body: {
    userStory: { title, description, acceptanceCriteria },
    examples: "optional format examples"
}
Response: { testCases: [...] }
```

### **Test Steps Generation**
```
POST /api/generate-test-steps
Body: {
    testCase: { id, title, description, type, priority },
    examples: "optional format examples"
}
Response: { automationSteps: [...] }
```

### **Gherkin Conversion**
```
POST /api/gherkin-to-steps
Body: {
    gherkinText: "Feature: ..."
}
Response: { automationSteps: [...] }
```

### **Storage Endpoints**
```
POST /api/user-stories
GET /api/user-stories
GET /api/user-stories/:id
GET /api/user-stories/:id/test-cases
GET /api/test-cases/:id/test-steps
GET /api/export/test-cases/:userStoryId
GET /api/export/test-steps/:testCaseId
```

---

## 📊 Data Models

### **User Story**
```javascript
{
    id: "us_timestamp",
    title: "string",
    description: "string",
    acceptanceCriteria: ["string"],
    createdAt: "ISO date",
    updatedAt: "ISO date"
}
```

### **Test Case**
```javascript
{
    id: "tc_timestamp",
    userStoryId: "string",
    title: "string",
    description: "string",
    type: "positive|negative|edge",
    priority: "high|medium|low",
    preconditions: "string",
    testData: "string",
    expectedResult: "string",
    createdAt: "ISO date"
}
```

### **Test Steps**
```javascript
{
    testCaseId: "string",
    automationSteps: [
        "Type \"%Field%\" into \"Field\"",
        "Wait for 1 seconds",
        "Click \"Button\""
    ],
    createdAt: "ISO date"
}
```

---

## 🎨 Frontend Architecture

### **Main UI (index.html)**
- Tab-based navigation
- User Story → Test Cases → Test Steps flow
- Real-time generation with loading states
- Export functionality (CSV, JSON)

### **Gherkin UI (gherkin.html)**
- File upload with drag & drop
- Text input area
- Side-by-side input/output view
- Copy/Download functionality

### **Client-Side Logic (app.js)**
```javascript
// Key functions:
async function generateTestCases()
async function generateTestSteps()
function displayTestCases(testCases)
function displayTestSteps(steps)
function exportToCSV()
function exportToJSON()
```

---

## 🔍 Prompt Engineering Details

### **Test Steps Prompt Structure**

```javascript
const prompt = `
Generate VERY DETAILED automation test steps following these EXACT rules:

1. **Action Format (CRITICAL - Follow exactly):**
   - Text fields: Type "%FieldName%" into "FieldName"
   - Dropdowns: Select "%FieldName%" from Dropdown "FieldName"
   - Textareas: Fill textarea "%FieldName%" with "FieldName"
   - Buttons: Click "ButtonName"
   - Wait: Wait for 1 seconds (after EVERY action)

2. **CSV Placeholders (CRITICAL):**
   - Format: %FieldName% (NO quotes inside percent signs)
   - Correct: Type "%Newsletter%" into "Newsletter"
   - WRONG: Type "%"Newsletter"%" into "Newsletter"

3. **Convert Gherkin steps (CRITICAL - Use FIELD NAME not value):**
   - "And the user selects X for Y" → Select "%Y%" from Dropdown "Y"
   - Y is the FIELD NAME, not X

4. **Special field handling:**
   - If field name contains "textarea" → Use Fill textarea format
   - If field name is "Other-Specify" → Use Type format (not Select)

5. **CRITICAL for Select statements:**
   - ALWAYS use the FIELD NAME in both CSV placeholder and field name
   - Gherkin: "And the user selects 'Yes' for 'Behavioral Health'"
   - Output: Select "%Behavioral Health%" from Dropdown "Behavioral Health"
   - NOT: Select "%Yes%" from Dropdown "Behavioral Health"

6. **Add Wait for 1 seconds after EVERY action**

7. **Output format:** Plain list of steps, no JSON, no section headers

EXAMPLES:
[Multiple detailed examples]

Generate the automation steps now. Return ONLY the steps, one per line.
`;
```

### **Why This Works**

1. **Explicit Rules:** AI knows exactly what to do
2. **Multiple Examples:** Shows correct format in context
3. **Negative Examples:** Shows what NOT to do
4. **Emphasis:** Uses CRITICAL, ALWAYS, MUST for key rules
5. **Structured Format:** Easy for AI to parse and follow

---

## 🧪 Testing Strategy

### **Manual Testing**
1. Test with various user stories
2. Test with different Gherkin formats
3. Verify output format matches exactly
4. Test edge cases (special characters, long field names)

### **Validation**
- JSON schema validation for test cases
- Format validation for automation steps
- Field name extraction accuracy
- CSV placeholder correctness

---

## 📈 Performance Considerations

### **Response Times**
- Test Case Generation: 3-8 seconds
- Test Steps Generation: 5-15 seconds (depending on complexity)
- Gherkin Conversion: 3-10 seconds

### **Token Usage**
- Average prompt: 1,000-2,000 tokens
- Average response: 1,000-5,000 tokens
- Cost per request: ~$0.001-$0.005 (GPT-4o-mini)

### **Optimization**
- Increased max_tokens to 8000 for detailed outputs
- Efficient prompt design to minimize tokens
- Caching of common examples
- Batch processing support

---

## 🔄 Future Enhancements

### **Planned Features**
1. Support for more AI models (Claude, Gemini)
2. Database storage (PostgreSQL, MongoDB)
3. User authentication and multi-tenancy
4. Test execution integration
5. CI/CD pipeline integration
6. Advanced analytics and reporting

### **Model Improvements**
1. Fine-tuning on custom data
2. Few-shot learning with user examples
3. Retrieval-augmented generation (RAG)
4. Model ensemble for better accuracy

---

## 🛠️ Development Setup

### **Prerequisites**
```bash
Node.js v18+
npm or yarn
OpenAI API key
```

### **Installation**
```bash
# Clone repository
git clone <repo-url>
cd AITestGenerator

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your API key

# Start server
npm start
# or
node server.js
```

### **Dependencies**
```json
{
    "express": "^4.18.2",
    "openai": "^4.0.0",
    "dotenv": "^16.0.3",
    "cors": "^2.8.5",
    "body-parser": "^1.20.2",
    "axios": "^1.4.0"
}
```

---

## 📚 Key Learnings

### **What Worked Well**
1. **Detailed prompts** with examples produce consistent output
2. **JSON response format** ensures structured data
3. **Explicit rules** in prompts prevent AI hallucination
4. **GPT-4o-mini** is cost-effective and fast enough
5. **Template-based approach** allows customization

### **Challenges Solved**
1. **CSV placeholder format** - Fixed with explicit examples
2. **Field name vs value** - Clarified in prompt with negative examples
3. **Textarea detection** - Added special handling rules
4. **Wait statement consistency** - Emphasized in prompt
5. **Dropdown format** - Standardized with capital D

---

## 🎯 Summary

**The AI Test Generator is built using:**
- **Backend:** Node.js + Express
- **AI Model:** OpenAI GPT-4o-mini
- **Frontend:** HTML + TailwindCSS + Vanilla JS
- **Storage:** JSON file-based
- **Key Technique:** Prompt engineering with detailed rules and examples

**The system converts:**
- User Stories → Test Cases
- Test Cases → Automation Steps
- Gherkin Scenarios → Automation Steps

**All in your exact format with:**
- CSV placeholders: `%FieldName%`
- Type format: `Type "%Field%" into "Field"`
- Select format: `Select "%Field%" from Dropdown "Field"`
- Textarea format: `Fill textarea "%Field%" with "Field"`
- Wait statements after every action

**The architecture is modular, extensible, and production-ready!**
