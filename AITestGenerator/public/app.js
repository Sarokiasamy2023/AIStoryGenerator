// API Base URL
const API_BASE = '/api';

// Current data
let currentTestCases = null;
let currentTestSteps = null;
let currentUserStoryId = null;

// Tab switching
function switchTab(tabName) {
    // Hide all content
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    
    // Remove active class from all tabs
    document.querySelectorAll('[id^="tab-"]').forEach(el => {
        el.classList.remove('tab-active', 'text-purple-600');
        el.classList.add('text-gray-600');
    });
    
    // Show selected content
    document.getElementById(`content-${tabName}`).classList.remove('hidden');
    
    // Add active class to selected tab
    const activeTab = document.getElementById(`tab-${tabName}`);
    activeTab.classList.add('tab-active', 'text-purple-600');
    activeTab.classList.remove('text-gray-600');
    
    // Load history if history tab
    if (tabName === 'history') {
        loadHistory();
    }
}

// Show/hide loading modal
function showLoading() {
    document.getElementById('loading-modal').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading-modal').classList.add('hidden');
}

// Generate Test Cases
async function generateTestCases() {
    const title = document.getElementById('story-title').value.trim();
    const description = document.getElementById('story-description').value.trim();
    const criteria = document.getElementById('story-criteria').value.trim();
    const examples = document.getElementById('story-examples').value.trim();
    
    if (!title || !description) {
        alert('Please enter both title and user story description');
        return;
    }
    
    // Build user story text
    let userStory = `Title: ${title}\n\n${description}`;
    if (criteria) {
        userStory += `\n\nAcceptance Criteria:\n${criteria}`;
    }
    
    showLoading();
    
    try {
        // First save the user story
        const saveResponse = await fetch(`${API_BASE}/user-stories`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title,
                description,
                acceptanceCriteria: criteria.split('\n').filter(c => c.trim())
            })
        });
        
        if (!saveResponse.ok) throw new Error('Failed to save user story');
        const savedStory = await saveResponse.json();
        currentUserStoryId = savedStory.id;
        
        // Generate test cases
        const response = await fetch(`${API_BASE}/generate-test-cases`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                userStoryId: currentUserStoryId,
                userStory,
                examples: examples || null
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to generate test cases');
        }
        
        const data = await response.json();
        currentTestCases = data.testCases || data;
        displayTestCases(currentTestCases);
        
        // Show export button
        document.getElementById('export-cases-btn').classList.remove('hidden');
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error generating test cases: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Display Test Cases
function displayTestCases(testCases) {
    const output = document.getElementById('test-cases-output');
    
    if (!testCases || testCases.length === 0) {
        output.innerHTML = '<p class="text-gray-500 text-center py-8">No test cases generated</p>';
        return;
    }
    
    // Group by type
    const positive = testCases.filter(tc => tc.type === 'positive');
    const negative = testCases.filter(tc => tc.type === 'negative');
    const edge = testCases.filter(tc => tc.type === 'edge');
    
    let html = '<div class="space-y-6">';
    
    // Summary
    html += `
        <div class="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <h3 class="font-bold text-purple-800 mb-2">Summary</h3>
            <div class="flex space-x-6 text-sm">
                <div><span class="font-semibold">${positive.length}</span> Positive</div>
                <div><span class="font-semibold">${negative.length}</span> Negative</div>
                <div><span class="font-semibold">${edge.length}</span> Edge Cases</div>
                <div><span class="font-semibold">${testCases.length}</span> Total</div>
            </div>
        </div>
    `;
    
    // Render each category
    if (positive.length > 0) {
        html += renderTestCaseCategory('Positive Test Cases', positive, 'positive');
    }
    if (negative.length > 0) {
        html += renderTestCaseCategory('Negative Test Cases', negative, 'negative');
    }
    if (edge.length > 0) {
        html += renderTestCaseCategory('Edge Case Test Cases', edge, 'edge');
    }
    
    html += '</div>';
    output.innerHTML = html;
}

function renderTestCaseCategory(title, testCases, type) {
    let html = `
        <div class="mt-6">
            <h3 class="text-xl font-bold text-gray-800 mb-3 flex items-center">
                <span class="badge-${type} text-white px-3 py-1 rounded-full text-sm mr-2">${testCases.length}</span>
                ${title}
            </h3>
            <div class="space-y-3">
    `;
    
    testCases.forEach(tc => {
        html += `
            <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
                <div class="flex justify-between items-start mb-2">
                    <div class="flex items-center space-x-2">
                        <span class="font-mono text-sm bg-gray-100 px-2 py-1 rounded">${tc.id}</span>
                        <h4 class="font-semibold text-gray-800">${tc.title}</h4>
                    </div>
                    <span class="priority-${tc.priority} font-semibold text-sm">
                        <i class="fas fa-flag mr-1"></i>${tc.priority.toUpperCase()}
                    </span>
                </div>
                <p class="text-gray-600 text-sm mb-2">${tc.description}</p>
                ${tc.preconditions && tc.preconditions.length > 0 ? `
                    <div class="mb-2">
                        <span class="text-xs font-semibold text-gray-500">PRECONDITIONS:</span>
                        <ul class="list-disc list-inside text-sm text-gray-600 ml-2">
                            ${tc.preconditions.map(p => `<li>${p}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                <div class="bg-green-50 border-l-4 border-green-500 p-2 mt-2">
                    <span class="text-xs font-semibold text-green-700">EXPECTED RESULT:</span>
                    <p class="text-sm text-green-800">${tc.expectedResult}</p>
                </div>
                <div class="mt-3 flex justify-end">
                    <button onclick='generateStepsFromCase(${JSON.stringify(tc).replace(/'/g, "&#39;")})' 
                            class="text-purple-600 hover:text-purple-800 text-sm font-semibold">
                        <i class="fas fa-arrow-right mr-1"></i>Generate Steps
                    </button>
                </div>
            </div>
        `;
    });
    
    html += '</div></div>';
    return html;
}

// Generate steps from a test case
function generateStepsFromCase(testCase) {
    // Switch to case-to-steps tab
    switchTab('case-to-steps');
    
    // Populate form
    document.getElementById('case-id').value = testCase.id;
    document.getElementById('case-title').value = testCase.title;
    document.getElementById('case-description').value = testCase.description;
    document.getElementById('case-type').value = testCase.type;
    document.getElementById('case-priority').value = testCase.priority;
    document.getElementById('case-preconditions').value = testCase.preconditions.join('\n');
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Generate Test Steps
async function generateTestSteps() {
    const id = document.getElementById('case-id').value.trim();
    const title = document.getElementById('case-title').value.trim();
    const description = document.getElementById('case-description').value.trim();
    const type = document.getElementById('case-type').value;
    const priority = document.getElementById('case-priority').value;
    const preconditions = document.getElementById('case-preconditions').value.trim();
    const examples = document.getElementById('steps-examples').value.trim();
    
    if (!title || !description) {
        alert('Please enter at least title and description');
        return;
    }
    
    const testCase = {
        id: id || 'TC001',
        title,
        description,
        type,
        priority,
        preconditions: preconditions.split('\n').filter(p => p.trim())
    };
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE}/generate-test-steps`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                testCase,
                examples: examples || null
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to generate test steps');
        }
        
        const data = await response.json();
        currentTestSteps = data;
        displayTestSteps(currentTestSteps);
        
        // Show export button
        document.getElementById('export-steps-btn').classList.remove('hidden');
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error generating test steps: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Display Test Steps
function displayTestSteps(data) {
    const output = document.getElementById('test-steps-output');
    
    // Check for automation steps format first
    if (data && data.automationSteps && data.automationSteps.length > 0) {
        let html = '<div class="space-y-4">';
        html += `
            <div class="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6">
                <h3 class="font-bold text-purple-800 mb-4 flex items-center text-lg">
                    <i class="fas fa-robot mr-2"></i>Automation Test Steps
                </h3>
                <div class="bg-white rounded p-4 font-mono text-sm space-y-1">
                    ${data.automationSteps.map((step, idx) => {
                        // Color code different types of steps
                        let color = 'text-gray-800';
                        let extraClass = '';
                        
                        if (step.startsWith('# ')) {
                            // Section headers
                            color = 'text-purple-700 font-bold text-base mt-3 mb-1';
                            extraClass = 'border-b border-purple-200 pb-1';
                        } else if (step.startsWith('Navigate')) {
                            color = 'text-indigo-600 font-semibold';
                        } else if (step.startsWith('Click')) {
                            color = 'text-blue-600 font-semibold';
                        } else if (step.startsWith('Type')) {
                            color = 'text-green-600 font-semibold';
                        } else if (step.startsWith('Verify')) {
                            color = 'text-orange-600 font-semibold';
                        } else if (step.startsWith('Wait')) {
                            color = 'text-gray-500';
                        } else if (step.startsWith('Select')) {
                            color = 'text-purple-600 font-semibold';
                        } else if (step.startsWith('Check')) {
                            color = 'text-teal-600 font-semibold';
                        } else if (step.startsWith('Clear')) {
                            color = 'text-red-600 font-semibold';
                        } else if (step.startsWith('--') || step.startsWith('#') && !step.startsWith('# ')) {
                            color = 'text-gray-400 italic';
                        }
                        
                        return `<div class="${color} ${extraClass}">${step}</div>`;
                    }).join('')}
                </div>
                <div class="mt-4 flex gap-2">
                    <button onclick="copyAutomationSteps()" class="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 transition">
                        <i class="fas fa-copy mr-2"></i>Copy Steps
                    </button>
                    <button onclick="downloadAutomationSteps()" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition">
                        <i class="fas fa-download mr-2"></i>Download as TXT
                    </button>
                </div>
            </div>
        `;
        html += '</div>';
        output.innerHTML = html;
        return;
    }
    
    // Fallback to old format
    if (!data || !data.testSteps || data.testSteps.length === 0) {
        output.innerHTML = '<p class="text-gray-500 text-center py-8">No test steps generated</p>';
        return;
    }
    
    let html = '<div class="space-y-6">';
    
    // Setup Steps
    if (data.setupSteps && data.setupSteps.length > 0) {
        html += `
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 class="font-bold text-blue-800 mb-2 flex items-center">
                    <i class="fas fa-cog mr-2"></i>Setup Steps
                </h3>
                <ol class="list-decimal list-inside space-y-1 text-sm text-blue-900">
                    ${data.setupSteps.map(step => `<li>${step}</li>`).join('')}
                </ol>
            </div>
        `;
    }
    
    // Test Steps
    html += `
        <div>
            <h3 class="text-xl font-bold text-gray-800 mb-3">Test Steps</h3>
            <div class="space-y-3">
    `;
    
    data.testSteps.forEach(step => {
        html += `
            <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
                <div class="flex items-start space-x-4">
                    <div class="flex-shrink-0">
                        <div class="w-10 h-10 bg-purple-600 text-white rounded-full flex items-center justify-center font-bold">
                            ${step.stepNumber}
                        </div>
                    </div>
                    <div class="flex-1">
                        <div class="mb-2">
                            <span class="text-xs font-semibold text-gray-500">ACTION:</span>
                            <p class="text-gray-800 font-medium">${step.action}</p>
                        </div>
                        ${step.testData ? `
                            <div class="mb-2 bg-yellow-50 border-l-4 border-yellow-400 p-2">
                                <span class="text-xs font-semibold text-yellow-700">TEST DATA:</span>
                                <p class="text-sm text-yellow-900">${step.testData}</p>
                            </div>
                        ` : ''}
                        <div class="bg-green-50 border-l-4 border-green-500 p-2">
                            <span class="text-xs font-semibold text-green-700">EXPECTED RESULT:</span>
                            <p class="text-sm text-green-800">${step.expectedResult}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div></div>';
    
    // Teardown Steps
    if (data.teardownSteps && data.teardownSteps.length > 0) {
        html += `
            <div class="bg-orange-50 border border-orange-200 rounded-lg p-4">
                <h3 class="font-bold text-orange-800 mb-2 flex items-center">
                    <i class="fas fa-broom mr-2"></i>Teardown Steps
                </h3>
                <ol class="list-decimal list-inside space-y-1 text-sm text-orange-900">
                    ${data.teardownSteps.map(step => `<li>${step}</li>`).join('')}
                </ol>
            </div>
        `;
    }
    
    html += '</div>';
    output.innerHTML = html;
}

// Load History
async function loadHistory() {
    const historyContent = document.getElementById('history-content');
    
    try {
        const response = await fetch(`${API_BASE}/user-stories`);
        if (!response.ok) throw new Error('Failed to load history');
        
        const userStories = await response.json();
        
        if (userStories.length === 0) {
            historyContent.innerHTML = '<p class="text-gray-500 text-center py-8">No history yet. Start by generating some test cases!</p>';
            return;
        }
        
        let html = '<div class="space-y-4">';
        
        for (const story of userStories) {
            html += `
                <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
                    <div class="flex justify-between items-start mb-2">
                        <h3 class="font-bold text-gray-800">${story.title}</h3>
                        <span class="text-xs text-gray-500">${new Date(story.createdAt).toLocaleString()}</span>
                    </div>
                    <p class="text-gray-600 text-sm mb-3">${story.description.substring(0, 150)}...</p>
                    <div class="flex space-x-2">
                        <button onclick="loadUserStory('${story.id}')" class="text-purple-600 hover:text-purple-800 text-sm font-semibold">
                            <i class="fas fa-eye mr-1"></i>View Details
                        </button>
                        <button onclick="exportTestCasesForStory('${story.id}')" class="text-green-600 hover:text-green-800 text-sm font-semibold">
                            <i class="fas fa-download mr-1"></i>Export
                        </button>
                    </div>
                </div>
            `;
        }
        
        html += '</div>';
        historyContent.innerHTML = html;
        
    } catch (error) {
        console.error('Error loading history:', error);
        historyContent.innerHTML = '<p class="text-red-500 text-center py-8">Error loading history</p>';
    }
}

// Load a specific user story
async function loadUserStory(id) {
    try {
        const [storyResponse, casesResponse] = await Promise.all([
            fetch(`${API_BASE}/user-stories/${id}`),
            fetch(`${API_BASE}/user-stories/${id}/test-cases`)
        ]);
        
        if (!storyResponse.ok) throw new Error('Failed to load user story');
        
        const story = await storyResponse.json();
        const testCaseSets = await casesResponse.json();
        
        // Switch to story-to-cases tab
        switchTab('story-to-cases');
        
        // Populate form
        document.getElementById('story-title').value = story.title;
        document.getElementById('story-description').value = story.description;
        document.getElementById('story-criteria').value = story.acceptanceCriteria.join('\n');
        
        // Display test cases if available
        if (testCaseSets.length > 0) {
            const latestSet = testCaseSets[testCaseSets.length - 1];
            currentTestCases = latestSet.testCases;
            displayTestCases(currentTestCases);
            document.getElementById('export-cases-btn').classList.remove('hidden');
        }
        
        window.scrollTo({ top: 0, behavior: 'smooth' });
        
    } catch (error) {
        console.error('Error loading user story:', error);
        alert('Error loading user story');
    }
}

// Export functions
function exportTestCases() {
    if (!currentTestCases) return;
    
    const csv = convertTestCasesToCSV(currentTestCases);
    downloadCSV(csv, 'test-cases.csv');
}

function exportTestSteps() {
    if (!currentTestSteps) return;
    
    const csv = convertTestStepsToCSV(currentTestSteps);
    downloadCSV(csv, 'test-steps.csv');
}

function convertTestCasesToCSV(testCases) {
    let csv = 'ID,Title,Type,Priority,Description,Preconditions,Expected Result\n';
    
    testCases.forEach(tc => {
        csv += `"${tc.id}","${tc.title}","${tc.type}","${tc.priority}","${tc.description}","${tc.preconditions.join('; ')}","${tc.expectedResult}"\n`;
    });
    
    return csv;
}

function convertTestStepsToCSV(data) {
    let csv = 'Step Number,Action,Test Data,Expected Result\n';
    
    data.testSteps.forEach(step => {
        csv += `"${step.stepNumber}","${step.action}","${step.testData}","${step.expectedResult}"\n`;
    });
    
    return csv;
}

function downloadCSV(csv, filename) {
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

// Samples
function showSamples() {
    const modal = document.getElementById('samples-modal');
    const content = document.getElementById('samples-content');
    
    content.innerHTML = `
        <div class="space-y-6">
            <div class="border-l-4 border-purple-600 pl-4">
                <h3 class="font-bold text-lg mb-2">Sample User Story: Login Feature</h3>
                <p class="text-gray-700 mb-2"><strong>As a</strong> registered user<br>
                <strong>I want to</strong> log in to my account<br>
                <strong>So that</strong> I can access my personalized dashboard</p>
                <p class="text-sm text-gray-600"><strong>Acceptance Criteria:</strong></p>
                <ul class="list-disc list-inside text-sm text-gray-600 ml-4">
                    <li>User can log in with valid email and password</li>
                    <li>System displays error for invalid credentials</li>
                    <li>Account locks after 5 failed attempts</li>
                    <li>User can reset password via email</li>
                </ul>
                <button onclick="useSample('login')" class="mt-3 bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700">
                    Use This Sample
                </button>
            </div>
            
            <div class="border-l-4 border-blue-600 pl-4">
                <h3 class="font-bold text-lg mb-2">Sample User Story: Shopping Cart</h3>
                <p class="text-gray-700 mb-2"><strong>As a</strong> customer<br>
                <strong>I want to</strong> add items to my shopping cart<br>
                <strong>So that</strong> I can purchase multiple items at once</p>
                <p class="text-sm text-gray-600"><strong>Acceptance Criteria:</strong></p>
                <ul class="list-disc list-inside text-sm text-gray-600 ml-4">
                    <li>User can add items to cart from product page</li>
                    <li>Cart displays total price and item count</li>
                    <li>User can update quantities or remove items</li>
                    <li>Cart persists across sessions</li>
                </ul>
                <button onclick="useSample('cart')" class="mt-3 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                    Use This Sample
                </button>
            </div>
        </div>
    `;
    
    modal.classList.remove('hidden');
}

function closeSamples() {
    document.getElementById('samples-modal').classList.add('hidden');
}

function useSample(type) {
    closeSamples();
    switchTab('story-to-cases');
    
    if (type === 'login') {
        document.getElementById('story-title').value = 'User Login Feature';
        document.getElementById('story-description').value = 'As a registered user, I want to log in to my account so that I can access my personalized dashboard and saved preferences.';
        document.getElementById('story-criteria').value = '- User can log in with valid email and password\n- System displays error for invalid credentials\n- Account locks after 5 failed attempts\n- User can reset password via email\n- Session expires after 30 minutes of inactivity';
    } else if (type === 'cart') {
        document.getElementById('story-title').value = 'Shopping Cart Feature';
        document.getElementById('story-description').value = 'As a customer, I want to add items to my shopping cart so that I can purchase multiple items at once and review my order before checkout.';
        document.getElementById('story-criteria').value = '- User can add items to cart from product page\n- Cart displays total price and item count\n- User can update quantities or remove items\n- Cart persists across sessions\n- Maximum 10 items per product allowed';
    }
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Copy automation steps to clipboard
function copyAutomationSteps() {
    if (!currentTestSteps || !currentTestSteps.automationSteps) {
        alert('No automation steps to copy');
        return;
    }
    
    const stepsText = currentTestSteps.automationSteps.join('\n');
    navigator.clipboard.writeText(stepsText).then(() => {
        alert('Automation steps copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy:', err);
        alert('Failed to copy to clipboard');
    });
}

// Download automation steps as text file
function downloadAutomationSteps() {
    if (!currentTestSteps || !currentTestSteps.automationSteps) {
        alert('No automation steps to download');
        return;
    }
    
    const stepsText = currentTestSteps.automationSteps.join('\n');
    const blob = new Blob([stepsText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'automation-test-steps.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('AI Test Generator initialized');
});
