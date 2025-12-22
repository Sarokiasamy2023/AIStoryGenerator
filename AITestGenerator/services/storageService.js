const fs = require('fs').promises;
const path = require('path');
const { v4: uuidv4 } = require('uuid');

class StorageService {
    constructor() {
        this.dataDir = path.join(__dirname, '../data');
        this.userStoriesFile = path.join(this.dataDir, 'userStories.json');
        this.testCasesFile = path.join(this.dataDir, 'testCases.json');
        this.testStepsFile = path.join(this.dataDir, 'testSteps.json');
        this.initializeStorage();
    }

    async initializeStorage() {
        try {
            await fs.mkdir(this.dataDir, { recursive: true });
            
            // Initialize files if they don't exist
            await this.ensureFileExists(this.userStoriesFile, { userStories: [] });
            await this.ensureFileExists(this.testCasesFile, { testCases: [] });
            await this.ensureFileExists(this.testStepsFile, { testSteps: [] });
        } catch (error) {
            console.error('Error initializing storage:', error);
        }
    }

    async ensureFileExists(filePath, defaultContent) {
        try {
            await fs.access(filePath);
        } catch {
            await fs.writeFile(filePath, JSON.stringify(defaultContent, null, 2));
        }
    }

    async saveUserStory(userStory) {
        const data = await this.readFile(this.userStoriesFile);
        const id = uuidv4();
        const story = {
            id,
            ...userStory,
            createdAt: new Date().toISOString()
        };
        data.userStories.push(story);
        await this.writeFile(this.userStoriesFile, data);
        return story;
    }

    async getUserStories() {
        const data = await this.readFile(this.userStoriesFile);
        return data.userStories;
    }

    async getUserStory(id) {
        const data = await this.readFile(this.userStoriesFile);
        return data.userStories.find(story => story.id === id);
    }

    async saveTestCases(userStoryId, testCases) {
        const data = await this.readFile(this.testCasesFile);
        const id = uuidv4();
        const testCaseSet = {
            id,
            userStoryId,
            testCases: testCases.testCases,
            createdAt: new Date().toISOString()
        };
        data.testCases.push(testCaseSet);
        await this.writeFile(this.testCasesFile, data);
        return testCaseSet;
    }

    async getTestCasesByUserStory(userStoryId) {
        const data = await this.readFile(this.testCasesFile);
        return data.testCases.filter(tc => tc.userStoryId === userStoryId);
    }

    async getTestCase(id) {
        const data = await this.readFile(this.testCasesFile);
        return data.testCases.find(tc => tc.id === id);
    }

    async saveTestSteps(testCaseId, testSteps) {
        const data = await this.readFile(this.testStepsFile);
        const id = uuidv4();
        const testStepSet = {
            id,
            testCaseId,
            ...testSteps,
            createdAt: new Date().toISOString()
        };
        data.testSteps.push(testStepSet);
        await this.writeFile(this.testStepsFile, data);
        return testStepSet;
    }

    async getTestStepsByTestCase(testCaseId) {
        const data = await this.readFile(this.testStepsFile);
        return data.testSteps.filter(ts => ts.testCaseId === testCaseId);
    }

    async readFile(filePath) {
        const content = await fs.readFile(filePath, 'utf8');
        return JSON.parse(content);
    }

    async writeFile(filePath, data) {
        await fs.writeFile(filePath, JSON.stringify(data, null, 2));
    }

    async exportToCSV(type, id) {
        // Export functionality for test cases or test steps
        if (type === 'testCases') {
            return await this.exportTestCasesToCSV(id);
        } else if (type === 'testSteps') {
            return await this.exportTestStepsToCSV(id);
        }
    }

    async exportTestCasesToCSV(userStoryId) {
        const testCases = await this.getTestCasesByUserStory(userStoryId);
        if (!testCases.length) return '';

        let csv = 'ID,Title,Type,Priority,Description,Preconditions,Expected Result\n';
        
        testCases.forEach(tcSet => {
            tcSet.testCases.forEach(tc => {
                csv += `"${tc.id}","${tc.title}","${tc.type}","${tc.priority}","${tc.description}","${tc.preconditions.join('; ')}","${tc.expectedResult}"\n`;
            });
        });

        return csv;
    }

    async exportTestStepsToCSV(testCaseId) {
        const testSteps = await this.getTestStepsByTestCase(testCaseId);
        if (!testSteps.length) return '';

        let csv = 'Step Number,Action,Test Data,Expected Result\n';
        
        testSteps.forEach(tsSet => {
            tsSet.testSteps.forEach(step => {
                csv += `"${step.stepNumber}","${step.action}","${step.testData}","${step.expectedResult}"\n`;
            });
        });

        return csv;
    }
}

module.exports = new StorageService();
