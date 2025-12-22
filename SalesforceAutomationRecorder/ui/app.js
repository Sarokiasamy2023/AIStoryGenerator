/**
 * Salesforce Automation Recorder - UI Application Logic
 */

class RecorderUI {
    constructor() {
        this.isRecording = false;
        this.capturedInteractions = [];
        this.startTime = null;
        this.timerInterval = null;
        
        this.initializeElements();
        this.attachEventListeners();
        this.loadFromLocalStorage();
    }

    initializeElements() {
        // Buttons
        this.startBtn = document.getElementById('start-btn');
        this.stopBtn = document.getElementById('stop-btn');
        this.exportBtn = document.getElementById('export-btn');
        this.clearBtn = document.getElementById('clear-btn');
        this.copyJsonBtn = document.getElementById('copy-json-btn');

        // Inputs
        this.urlInput = document.getElementById('url-input');
        this.outputInput = document.getElementById('output-input');
        this.searchInput = document.getElementById('search-input');
        this.autoSaveCheckbox = document.getElementById('auto-save');
        this.screenshotsCheckbox = document.getElementById('capture-screenshots');

        // Display elements
        this.statusBadge = document.getElementById('status-badge');
        this.statusText = document.getElementById('status-text');
        this.interactionsList = document.getElementById('interactions-list');
        this.jsonOutput = document.getElementById('json-output');

        // Stats
        this.totalInteractionsEl = document.getElementById('total-interactions');
        this.lightningCountEl = document.getElementById('lightning-count');
        this.omniscriptCountEl = document.getElementById('omniscript-count');
        this.recordingTimeEl = document.getElementById('recording-time');
    }

    attachEventListeners() {
        this.startBtn.addEventListener('click', () => this.startRecording());
        this.stopBtn.addEventListener('click', () => this.stopRecording());
        this.exportBtn.addEventListener('click', () => this.exportJSON());
        this.clearBtn.addEventListener('click', () => this.clearInteractions());
        this.copyJsonBtn.addEventListener('click', () => this.copyJSON());
        this.searchInput.addEventListener('input', (e) => this.filterInteractions(e.target.value));

        // Listen for messages from recorder
        window.addEventListener('message', (event) => {
            if (event.data.type === 'RECORDER_CAPTURE') {
                this.addInteraction(event.data.data);
            }
        });
    }

    startRecording() {
        const url = this.urlInput.value.trim();
        
        if (!url) {
            alert('Please enter a Salesforce URL');
            return;
        }

        // In a real implementation, this would communicate with the Python backend
        // For now, we'll simulate the recording process
        this.isRecording = true;
        this.startTime = Date.now();
        
        this.updateUI();
        this.startTimer();
        
        console.log('Recording started for URL:', url);
        
        // Show notification
        this.showNotification('Recording started! Interact with the page to capture elements.', 'success');
    }

    stopRecording() {
        this.isRecording = false;
        this.stopTimer();
        
        this.updateUI();
        
        console.log('Recording stopped');
        console.log('Captured interactions:', this.capturedInteractions);
        
        // Auto-save if enabled
        if (this.autoSaveCheckbox.checked) {
            this.exportJSON();
        }
        
        this.showNotification(`Recording stopped. Captured ${this.capturedInteractions.length} interactions.`, 'info');
    }

    addInteraction(interaction) {
        this.capturedInteractions.push(interaction);
        this.updateStats();
        this.renderInteractions();
        this.updateJSONPreview();
        this.saveToLocalStorage();
    }

    clearInteractions() {
        if (this.capturedInteractions.length === 0) {
            return;
        }

        if (confirm('Are you sure you want to clear all captured interactions?')) {
            this.capturedInteractions = [];
            this.updateStats();
            this.renderInteractions();
            this.updateJSONPreview();
            this.saveToLocalStorage();
            this.showNotification('All interactions cleared', 'info');
        }
    }

    filterInteractions(query) {
        const filtered = this.capturedInteractions.filter(interaction => {
            const searchText = `${interaction.label} ${interaction.action} ${interaction.framework} ${interaction.selector}`.toLowerCase();
            return searchText.includes(query.toLowerCase());
        });
        
        this.renderInteractions(filtered);
    }

    renderInteractions(interactions = null) {
        const items = interactions || this.capturedInteractions;
        
        if (items.length === 0) {
            this.interactionsList.innerHTML = `
                <div class="empty-state">
                    <svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="32" cy="32" r="30" stroke="#e0e0e0" stroke-width="2"/>
                        <path d="M32 20v24M20 32h24" stroke="#e0e0e0" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                    <p>No interactions captured yet</p>
                    <small>Start recording to capture user interactions</small>
                </div>
            `;
            return;
        }

        this.interactionsList.innerHTML = items.map((interaction, index) => {
            const time = new Date(interaction.timestamp).toLocaleTimeString();
            const framework = interaction.framework.toLowerCase();
            
            return `
                <div class="interaction-item ${framework}" data-index="${index}">
                    <div class="interaction-header">
                        <span class="interaction-badge ${framework}">${interaction.framework}</span>
                        <span class="interaction-time">${time}</span>
                    </div>
                    <div class="interaction-content">
                        <div class="interaction-label">
                            <span class="interaction-action">${interaction.action}</span>
                            ${interaction.label}
                        </div>
                        <div class="interaction-selector">
                            <strong>Selector:</strong> ${this.escapeHtml(interaction.selector)}
                        </div>
                        ${interaction.xpath ? `
                            <div class="interaction-selector">
                                <strong>XPath:</strong> ${this.escapeHtml(interaction.xpath)}
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
        }).join('');
    }

    updateStats() {
        const total = this.capturedInteractions.length;
        const lightning = this.capturedInteractions.filter(i => i.framework === 'Lightning').length;
        const omniscript = this.capturedInteractions.filter(i => i.framework === 'OmniScript').length;

        this.totalInteractionsEl.textContent = total;
        this.lightningCountEl.textContent = lightning;
        this.omniscriptCountEl.textContent = omniscript;
    }

    updateJSONPreview() {
        const json = JSON.stringify(this.capturedInteractions, null, 2);
        this.jsonOutput.innerHTML = `<code>${this.escapeHtml(json)}</code>`;
    }

    updateUI() {
        if (this.isRecording) {
            this.startBtn.disabled = true;
            this.stopBtn.disabled = false;
            this.exportBtn.disabled = true;
            this.statusBadge.classList.add('recording');
            this.statusText.textContent = 'Recording...';
        } else {
            this.startBtn.disabled = false;
            this.stopBtn.disabled = true;
            this.exportBtn.disabled = this.capturedInteractions.length === 0;
            this.statusBadge.classList.remove('recording');
            this.statusText.textContent = 'Ready';
        }
    }

    startTimer() {
        this.timerInterval = setInterval(() => {
            const elapsed = Date.now() - this.startTime;
            const minutes = Math.floor(elapsed / 60000);
            const seconds = Math.floor((elapsed % 60000) / 1000);
            this.recordingTimeEl.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        }, 1000);
    }

    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }

    exportJSON() {
        if (this.capturedInteractions.length === 0) {
            alert('No interactions to export');
            return;
        }

        const filename = this.outputInput.value || 'recording_output.json';
        const json = JSON.stringify(this.capturedInteractions, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        
        URL.revokeObjectURL(url);
        
        this.showNotification(`Exported ${this.capturedInteractions.length} interactions to ${filename}`, 'success');
    }

    copyJSON() {
        const json = JSON.stringify(this.capturedInteractions, null, 2);
        
        navigator.clipboard.writeText(json).then(() => {
            this.showNotification('JSON copied to clipboard!', 'success');
        }).catch(err => {
            console.error('Failed to copy:', err);
            this.showNotification('Failed to copy JSON', 'error');
        });
    }

    saveToLocalStorage() {
        try {
            localStorage.setItem('capturedInteractions', JSON.stringify(this.capturedInteractions));
            localStorage.setItem('recorderConfig', JSON.stringify({
                url: this.urlInput.value,
                output: this.outputInput.value,
                autoSave: this.autoSaveCheckbox.checked,
                screenshots: this.screenshotsCheckbox.checked
            }));
        } catch (e) {
            console.error('Failed to save to localStorage:', e);
        }
    }

    loadFromLocalStorage() {
        try {
            const saved = localStorage.getItem('capturedInteractions');
            if (saved) {
                this.capturedInteractions = JSON.parse(saved);
                this.updateStats();
                this.renderInteractions();
                this.updateJSONPreview();
                this.updateUI();
            }

            const config = localStorage.getItem('recorderConfig');
            if (config) {
                const cfg = JSON.parse(config);
                this.urlInput.value = cfg.url || '';
                this.outputInput.value = cfg.output || 'recording_output.json';
                this.autoSaveCheckbox.checked = cfg.autoSave !== false;
                this.screenshotsCheckbox.checked = cfg.screenshots !== false;
            }
        } catch (e) {
            console.error('Failed to load from localStorage:', e);
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#2ed573' : type === 'error' ? '#ff4757' : '#667eea'};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;

        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Add animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Initialize the UI when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.recorderUI = new RecorderUI();
    console.log('Recorder UI initialized');
});

// For testing: Simulate captured interactions
function simulateCapture() {
    const frameworks = ['Lightning', 'OmniScript', 'Standard'];
    const actions = ['click', 'input', 'change'];
    const labels = ['Next Button', 'Customer Name', 'Submit', 'Email Field', 'Save'];
    
    const interaction = {
        timestamp: new Date().toISOString(),
        label: labels[Math.floor(Math.random() * labels.length)],
        action: actions[Math.floor(Math.random() * actions.length)],
        selector: `button.slds-button-${Math.random().toString(36).substr(2, 5)}`,
        xpath: `//button[@class='slds-button']`,
        framework: frameworks[Math.floor(Math.random() * frameworks.length)],
        componentType: 'button',
        tagName: 'button',
        innerText: 'Click me',
        attributes: {
            class: 'slds-button',
            type: 'button'
        },
        isNested: false,
        parentFramework: null
    };
    
    window.postMessage({
        type: 'RECORDER_CAPTURE',
        data: interaction
    }, '*');
}

// Expose for testing
window.simulateCapture = simulateCapture;
