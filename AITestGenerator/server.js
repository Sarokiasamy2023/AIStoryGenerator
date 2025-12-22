require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const path = require('path');

const aiService = require('./services/aiService');
const storageService = require('./services/storageService');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json({ limit: '10mb' }));
app.use(bodyParser.urlencoded({ extended: true, limit: '10mb' }));
app.use(express.static(path.join(__dirname, 'public')));

// Health check
app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// User Story endpoints
app.post('/api/user-stories', async (req, res) => {
    try {
        const { title, description, acceptanceCriteria } = req.body;
        
        if (!title || !description) {
            return res.status(400).json({ error: 'Title and description are required' });
        }

        const userStory = await storageService.saveUserStory({
            title,
            description,
            acceptanceCriteria: acceptanceCriteria || []
        });

        res.json(userStory);
    } catch (error) {
        console.error('Error saving user story:', error);
        res.status(500).json({ error: error.message });
    }
});

app.get('/api/user-stories', async (req, res) => {
    try {
        const userStories = await storageService.getUserStories();
        res.json(userStories);
    } catch (error) {
        console.error('Error fetching user stories:', error);
        res.status(500).json({ error: error.message });
    }
});

app.get('/api/user-stories/:id', async (req, res) => {
    try {
        const userStory = await storageService.getUserStory(req.params.id);
        if (!userStory) {
            return res.status(404).json({ error: 'User story not found' });
        }
        res.json(userStory);
    } catch (error) {
        console.error('Error fetching user story:', error);
        res.status(500).json({ error: error.message });
    }
});

// Generate test cases from user story
app.post('/api/generate-test-cases', async (req, res) => {
    try {
        const { userStoryId, userStory, examples } = req.body;
        
        if (!userStory) {
            return res.status(400).json({ error: 'User story is required' });
        }

        console.log('Generating test cases for user story...');
        const testCases = await aiService.generateTestCases(userStory, examples);
        
        // Save if userStoryId provided
        if (userStoryId) {
            const saved = await storageService.saveTestCases(userStoryId, testCases);
            return res.json(saved);
        }

        res.json(testCases);
    } catch (error) {
        console.error('Error generating test cases:', error);
        res.status(500).json({ error: error.message });
    }
});

// Get test cases for a user story
app.get('/api/user-stories/:id/test-cases', async (req, res) => {
    try {
        const testCases = await storageService.getTestCasesByUserStory(req.params.id);
        res.json(testCases);
    } catch (error) {
        console.error('Error fetching test cases:', error);
        res.status(500).json({ error: error.message });
    }
});

// Generate test steps from test case
app.post('/api/generate-test-steps', async (req, res) => {
    try {
        const { testCaseId, testCase, examples } = req.body;
        
        if (!testCase) {
            return res.status(400).json({ error: 'Test case is required' });
        }

        console.log('Generating test steps for test case...');
        const testSteps = await aiService.generateTestSteps(testCase, examples);
        
        // Save if testCaseId provided
        if (testCaseId) {
            const saved = await storageService.saveTestSteps(testCaseId, testSteps);
            return res.json(saved);
        }

        res.json(testSteps);
    } catch (error) {
        console.error('Error generating test steps:', error);
        res.status(500).json({ error: error.message });
    }
});

// Get test steps for a test case
app.get('/api/test-cases/:id/test-steps', async (req, res) => {
    try {
        const testSteps = await storageService.getTestStepsByTestCase(req.params.id);
        res.json(testSteps);
    } catch (error) {
        console.error('Error fetching test steps:', error);
        res.status(500).json({ error: error.message });
    }
});

// Export endpoints
app.get('/api/export/test-cases/:userStoryId', async (req, res) => {
    try {
        const csv = await storageService.exportToCSV('testCases', req.params.userStoryId);
        res.setHeader('Content-Type', 'text/csv');
        res.setHeader('Content-Disposition', `attachment; filename=test-cases-${req.params.userStoryId}.csv`);
        res.send(csv);
    } catch (error) {
        console.error('Error exporting test cases:', error);
        res.status(500).json({ error: error.message });
    }
});

app.get('/api/export/test-steps/:testCaseId', async (req, res) => {
    try {
        const csv = await storageService.exportToCSV('testSteps', req.params.testCaseId);
        res.setHeader('Content-Type', 'text/csv');
        res.setHeader('Content-Disposition', `attachment; filename=test-steps-${req.params.testCaseId}.csv`);
        res.send(csv);
    } catch (error) {
        console.error('Error exporting test steps:', error);
        res.status(500).json({ error: error.message });
    }
});

// Gherkin to automation steps endpoint
app.post('/api/gherkin-to-steps', async (req, res) => {
    try {
        const { gherkinText } = req.body;
        
        if (!gherkinText) {
            return res.status(400).json({ error: 'Gherkin text is required' });
        }

        console.log('Converting Gherkin to automation steps...');
        const automationSteps = await aiService.convertGherkinToSteps(gherkinText);
        
        res.json({ automationSteps });
    } catch (error) {
        console.error('Error converting Gherkin:', error);
        res.status(500).json({ error: error.message });
    }
});

// Serve the main HTML page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Serve the Gherkin page
app.get('/gherkin', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'gherkin.html'));
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('Unhandled error:', err);
    res.status(500).json({ error: 'Internal server error' });
});

// Start server
app.listen(PORT, () => {
    console.log(`\n🚀 AI Test Generator Server running on http://localhost:${PORT}`);
    console.log(`📝 Open http://localhost:${PORT} in your browser\n`);
});

module.exports = app;
