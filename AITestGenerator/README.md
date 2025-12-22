# AI Test Generator

An intelligent application that uses AI to automatically convert User Stories into comprehensive Test Cases and Test Cases into detailed Test Steps. The system generates positive, negative, and edge case scenarios to ensure thorough test coverage.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Node](https://img.shields.io/badge/node-%3E%3D14.0.0-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## 🌟 Features

- **User Story → Test Cases**: Automatically generate comprehensive test cases from user stories
- **Test Cases → Test Steps**: Convert test cases into detailed, executable test steps
- **AI-Powered**: Leverages GPT-4, Claude, or local LLMs for intelligent generation
- **Scenario Coverage**: Generates positive, negative, and edge case scenarios
- **Beautiful UI**: Modern, responsive web interface built with Tailwind CSS
- **Export Functionality**: Export test cases and steps to CSV format
- **History Tracking**: Save and retrieve previous generations
- **Sample Library**: Built-in samples to get started quickly
- **Customizable**: Provide examples to guide AI generation style

## 📋 Table of Contents

- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Sample Data](#-sample-data)
- [Architecture](#-architecture)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

## 🔧 Prerequisites

- **Node.js** 14.0.0 or higher
- **npm** or **yarn**
- **OpenAI API Key** (or alternative AI provider)
- Modern web browser (Chrome, Firefox, Safari, Edge)

## 📦 Installation

### 1. Clone or Download the Project

```bash
cd AITestGenerator
```

### 2. Install Dependencies

```bash
npm install
```

This will install:
- Express.js (web server)
- OpenAI SDK (AI integration)
- Body-parser, CORS (middleware)
- UUID (unique ID generation)
- Other dependencies

### 3. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Server Configuration
PORT=3000
NODE_ENV=development

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Application Settings
MAX_TOKENS=2000
TEMPERATURE=0.7
```

### 4. Start the Server

```bash
npm start
```

For development with auto-reload:

```bash
npm run dev
```

### 5. Access the Application

Open your browser and navigate to:

```
http://localhost:3000
```

## ⚙️ Configuration

### AI Provider Options

#### Option 1: OpenAI (Recommended)

```env
OPENAI_API_KEY=sk-...your-key...
OPENAI_MODEL=gpt-4o-mini
```

Get your API key from: https://platform.openai.com/api-keys

#### Option 2: Azure OpenAI

```env
AZURE_OPENAI_API_KEY=your_azure_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
```

#### Option 3: Anthropic Claude

```env
ANTHROPIC_API_KEY=your_anthropic_key
ANTHROPIC_MODEL=claude-3-opus-20240229
```

#### Option 4: Local LLM (Ollama, LM Studio)

```env
LOCAL_LLM_ENDPOINT=http://localhost:11434/api/generate
LOCAL_LLM_MODEL=llama2
```

### Application Settings

- **MAX_TOKENS**: Maximum tokens for AI response (default: 2000)
- **TEMPERATURE**: AI creativity level 0-1 (default: 0.7)
- **PORT**: Server port (default: 3000)

## 🚀 Usage

### 1. User Story to Test Cases

#### Step 1: Enter User Story
- Navigate to the "User Story → Test Cases" tab
- Fill in:
  - **Title**: Brief title for the user story
  - **User Story**: Full user story description
  - **Acceptance Criteria**: (Optional) List of acceptance criteria
  - **Examples**: (Optional) Example test cases to guide AI

#### Step 2: Generate
- Click "Generate Test Cases"
- Wait for AI to process (typically 10-30 seconds)

#### Step 3: Review Results
The system generates:
- **Positive Test Cases**: Happy path scenarios (3-5 cases)
- **Negative Test Cases**: Error conditions and invalid inputs (3-5 cases)
- **Edge Cases**: Boundary conditions and unusual scenarios (2-3 cases)

Each test case includes:
- Unique ID (TC001, TC002, etc.)
- Title
- Type (positive/negative/edge)
- Priority (high/medium/low)
- Description
- Preconditions
- Expected Result

#### Step 4: Export (Optional)
- Click "Export CSV" to download test cases
- Use in test management tools (Jira, TestRail, etc.)

### 2. Test Case to Test Steps

#### Step 1: Enter Test Case
- Navigate to "Test Case → Test Steps" tab
- Fill in:
  - **Test Case ID**: Unique identifier
  - **Title**: Test case title
  - **Description**: Detailed description
  - **Type**: Positive/Negative/Edge
  - **Priority**: High/Medium/Low
  - **Preconditions**: List of preconditions

Or click "Generate Steps" from a generated test case

#### Step 2: Generate
- Click "Generate Test Steps"
- AI processes the test case

#### Step 3: Review Results
The system generates:
- **Setup Steps**: Preconditions and preparation
- **Test Steps**: Detailed step-by-step instructions
  - Step number
  - Action to perform
  - Test data to use
  - Expected result
- **Teardown Steps**: Cleanup actions

#### Step 4: Export (Optional)
- Click "Export CSV" to download test steps

### 3. View History

- Navigate to "History" tab
- View all previously generated test cases
- Click "View Details" to reload a user story
- Click "Export" to download test cases

### 4. Use Sample Data

- Click "View Samples" in the header
- Choose from pre-built user stories:
  - Login Feature
  - Shopping Cart
  - And more...
- Click "Use This Sample" to populate the form

## 📚 API Documentation

### Endpoints

#### Health Check
```
GET /api/health
```
Returns server status

#### Save User Story
```
POST /api/user-stories
Body: {
  "title": "string",
  "description": "string",
  "acceptanceCriteria": ["string"]
}
```

#### Get All User Stories
```
GET /api/user-stories
```

#### Get User Story by ID
```
GET /api/user-stories/:id
```

#### Generate Test Cases
```
POST /api/generate-test-cases
Body: {
  "userStoryId": "string (optional)",
  "userStory": "string",
  "examples": "string (optional)"
}
```

#### Get Test Cases for User Story
```
GET /api/user-stories/:id/test-cases
```

#### Generate Test Steps
```
POST /api/generate-test-steps
Body: {
  "testCaseId": "string (optional)",
  "testCase": {
    "id": "string",
    "title": "string",
    "description": "string",
    "type": "positive|negative|edge",
    "priority": "high|medium|low",
    "preconditions": ["string"]
  },
  "examples": "string (optional)"
}
```

#### Get Test Steps for Test Case
```
GET /api/test-cases/:id/test-steps
```

#### Export Test Cases
```
GET /api/export/test-cases/:userStoryId
```
Returns CSV file

#### Export Test Steps
```
GET /api/export/test-steps/:testCaseId
```
Returns CSV file

## 📖 Sample Data

The `samples/` directory contains:

### sample-user-stories.md
10 complete user stories covering:
- Login functionality
- Shopping cart
- Search features
- Payment processing
- User registration
- Order tracking
- Product reviews
- Wishlist
- Password reset
- Notification preferences

### sample-test-cases.md
Complete test cases for multiple features with:
- Positive scenarios
- Negative scenarios
- Edge cases
- Full details (ID, priority, preconditions, expected results)

### sample-test-steps.md
Detailed test steps including:
- Setup steps
- Numbered test steps with actions, test data, and expected results
- Teardown steps

## 🏗️ Architecture

```
AITestGenerator/
├── server.js                 # Express server & API routes
├── services/
│   ├── aiService.js         # AI integration (OpenAI, Claude, etc.)
│   └── storageService.js    # Data persistence (JSON files)
├── public/
│   ├── index.html           # Main UI
│   └── app.js               # Frontend JavaScript
├── data/                    # Generated data storage (auto-created)
│   ├── userStories.json
│   ├── testCases.json
│   └── testSteps.json
├── samples/                 # Sample data for reference
│   ├── sample-user-stories.md
│   ├── sample-test-cases.md
│   └── sample-test-steps.md
└── package.json
```

### Technology Stack

**Backend:**
- Node.js + Express.js
- OpenAI SDK
- File-based JSON storage

**Frontend:**
- Vanilla JavaScript
- Tailwind CSS
- Font Awesome icons

**AI Integration:**
- OpenAI GPT-4
- Anthropic Claude (optional)
- Local LLMs (optional)

## 🐛 Troubleshooting

### Issue: "Failed to generate test cases"

**Possible causes:**
1. Invalid or missing API key
2. Network connectivity issues
3. API rate limits exceeded

**Solutions:**
- Verify API key in `.env` file
- Check internet connection
- Wait a few minutes if rate limited
- Check console logs for detailed error

### Issue: Server won't start

**Possible causes:**
1. Port already in use
2. Missing dependencies
3. Node.js version too old

**Solutions:**
```bash
# Change port in .env
PORT=3001

# Reinstall dependencies
rm -rf node_modules
npm install

# Check Node.js version
node --version  # Should be >= 14.0.0
```

### Issue: AI generates incorrect format

**Solutions:**
- Provide example test cases/steps in the optional fields
- Adjust TEMPERATURE in `.env` (lower = more consistent)
- Try a different AI model

### Issue: Data not persisting

**Solutions:**
- Check file permissions on `data/` directory
- Ensure disk space available
- Check console for write errors

## 💡 Best Practices

### Writing User Stories

1. **Be Specific**: Include clear acceptance criteria
2. **Use Standard Format**: "As a [user], I want [action] so that [benefit]"
3. **Include Context**: Add relevant business rules and constraints

### Providing Examples

When providing example test cases or steps:
- Use the same format you want in the output
- Include 2-3 examples for best results
- Be consistent with terminology

### Reviewing Generated Content

Always review AI-generated content:
- Verify test coverage is complete
- Check for logical consistency
- Ensure test data is realistic
- Validate expected results

## 🔒 Security Considerations

- **API Keys**: Never commit `.env` file to version control
- **Data Storage**: Data is stored locally in JSON files
- **Network**: Use HTTPS in production
- **Access Control**: Add authentication for production use

## 📈 Future Enhancements

Potential features for future versions:
- [ ] Database integration (MongoDB, PostgreSQL)
- [ ] User authentication and multi-tenancy
- [ ] Integration with test management tools (Jira, TestRail)
- [ ] Automated test script generation (Selenium, Playwright)
- [ ] Test execution tracking
- [ ] Collaboration features
- [ ] Advanced filtering and search
- [ ] Custom templates
- [ ] Bulk import/export

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional AI provider integrations
- UI/UX enhancements
- Export format options (Excel, JSON, XML)
- Test case templates
- Documentation improvements

## 📄 License

MIT License - feel free to use and modify for your needs

## 🆘 Support

For issues or questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review sample data in `samples/` directory
3. Check console logs for detailed errors
4. Verify API key and configuration

## 🎯 Quick Start Checklist

- [ ] Node.js 14+ installed
- [ ] Dependencies installed (`npm install`)
- [ ] `.env` file configured with API key
- [ ] Server started (`npm start`)
- [ ] Browser opened to `http://localhost:3000`
- [ ] Sample user story tested
- [ ] Test cases generated successfully
- [ ] Test steps generated successfully
- [ ] Export functionality tested

---

**Built with ❤️ for QA Engineers and Test Automation Professionals**
