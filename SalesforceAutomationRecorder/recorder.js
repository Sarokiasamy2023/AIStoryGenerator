/**
 * Salesforce Automation Recorder - Browser Injection Script
 * Captures user interactions on Lightning and OmniScript components
 */

class SalesforceRecorder {
    constructor() {
        this.isRecording = false;
        // Use global storage to persist across page navigations
        if (!window.__recorderData) {
            window.__recorderData = [];
        }
        this.capturedInteractions = window.__recorderData;
        this.highlightedElement = null;
        this.config = {
            highlightColor: '#00ff00',
            highlightDuration: 500
        };
        
        // Bind event handlers once to maintain references
        this.boundHandleClick = this.handleClick.bind(this);
        this.boundHandleInput = this.handleInput.bind(this);
        this.boundHandleChange = this.handleChange.bind(this);
        this.boundHandleMouseOver = this.handleMouseOver.bind(this);
        this.boundHandleMouseOut = this.handleMouseOut.bind(this);
    }

    /**
     * Start recording user interactions
     */
    startRecording() {
        this.isRecording = true;
        // capturedInteractions points to window.__recorderData, so it persists
        this.attachEventListeners();
        this.injectStyles();
        console.log('[Recorder] Recording started - ' + this.capturedInteractions.length + ' interactions so far');
    }

    /**
     * Stop recording user interactions
     */
    stopRecording() {
        this.isRecording = false;
        this.removeEventListeners();
        console.log('[Recorder] Recording stopped');
        return this.capturedInteractions;
    }

    /**
     * Inject CSS styles for element highlighting
     */
    injectStyles() {
        if (document.getElementById('recorder-styles')) return;

        const style = document.createElement('style');
        style.id = 'recorder-styles';
        style.textContent = `
            .recorder-highlight {
                outline: 3px solid ${this.config.highlightColor} !important;
                outline-offset: 2px !important;
                box-shadow: 0 0 10px ${this.config.highlightColor} !important;
                transition: all 0.2s ease !important;
            }
            .recorder-highlight-click {
                animation: recorder-pulse 0.5s ease !important;
            }
            @keyframes recorder-pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.02); }
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Attach event listeners for capturing interactions
     */
    attachEventListeners() {
        // Remove any existing listeners first to avoid duplicates
        this.removeEventListeners();
        
        // Click events
        document.addEventListener('click', this.boundHandleClick, true);
        
        // Input events
        document.addEventListener('input', this.boundHandleInput, true);
        document.addEventListener('change', this.boundHandleChange, true);
        
        // Hover events for highlighting
        document.addEventListener('mouseover', this.boundHandleMouseOver, true);
        document.addEventListener('mouseout', this.boundHandleMouseOut, true);
        
        console.log('[Recorder] Event listeners attached');
    }

    /**
     * Remove event listeners
     */
    removeEventListeners() {
        document.removeEventListener('click', this.boundHandleClick, true);
        document.removeEventListener('input', this.boundHandleInput, true);
        document.removeEventListener('change', this.boundHandleChange, true);
        document.removeEventListener('mouseover', this.boundHandleMouseOver, true);
        document.removeEventListener('mouseout', this.boundHandleMouseOut, true);
    }

    /**
     * Handle click events
     */
    handleClick(event) {
        if (!this.isRecording) return;
        
        // Ignore clicks on the recorder UI overlay
        if (event.target.closest('#recorder-ui-overlay')) {
            return;
        }

        let element = event.target;
        
        // If clicking on a Salesforce container (flowruntime, omniscript), try to find the actual clickable element
        if (element.tagName && (element.tagName.toLowerCase().includes('flowruntime') || 
                                element.tagName.toLowerCase().includes('omniscript'))) {
            // Don't record clicks on containers - they're not the actual interactive elements
            console.log('[Recorder] Skipping container element:', element.tagName);
            return;
        }
        
        // If clicking inside a flowruntime/omniscript, find the actual button/input
        const container = element.closest('flowruntime-flow, runtime_omnistudio-omniscript');
        if (container) {
            // Look for actual interactive elements
            if (element.tagName === 'BUTTON' || element.tagName === 'INPUT' || 
                element.tagName === 'A' || element.getAttribute('role') === 'button') {
                // This is the actual element, use it
            } else {
                // Try to find a button/input within the clicked element
                const button = element.querySelector('button, input[type="checkbox"], a, [role="button"]');
                if (button) {
                    element = button;
                } else {
                    // No interactive element found, skip this click
                    console.log('[Recorder] No interactive element found in container');
                    return;
                }
            }
        }
        
        // Detect if this is a checkbox/toggle interaction
        let actionType = 'click';
        let targetElement = element;
        
        // Check if clicking on a label for a checkbox/toggle
        if (element.tagName === 'LABEL') {
            const forAttr = element.getAttribute('for');
            if (forAttr) {
                const input = document.getElementById(forAttr);
                if (input && (input.type === 'checkbox' || input.getAttribute('role') === 'switch')) {
                    targetElement = input;
                    actionType = 'check';
                }
            }
        }
        
        // Check if element is a checkbox or toggle switch
        if (element.type === 'checkbox' || element.getAttribute('role') === 'switch') {
            actionType = 'check';
            targetElement = element;
        }
        
        // Check if clicking on a toggle button container
        const toggleContainer = element.closest('[role="switch"], .slds-checkbox_toggle, .toggle-button, input[type="checkbox"]');
        if (toggleContainer) {
            const checkbox = toggleContainer.querySelector('input[type="checkbox"]') || toggleContainer;
            if (checkbox && checkbox.type === 'checkbox') {
                targetElement = checkbox;
                actionType = 'check';
            }
        }
        
        const metadata = this.extractElementMetadata(targetElement, actionType);
        
        // For checkboxes, capture the checked state
        if (actionType === 'check' && targetElement.type === 'checkbox') {
            metadata.value = targetElement.checked ? 'checked' : 'unchecked';
        }
        
        // Add visual feedback
        element.classList.add('recorder-highlight-click');
        setTimeout(() => {
            element.classList.remove('recorder-highlight-click');
        }, this.config.highlightDuration);

        this.capturedInteractions.push(metadata);
        console.log(`[Recorder] Captured ${actionType}:`, metadata);

        // Notify parent window if in iframe
        this.notifyCapture(metadata);
    }

    /**
     * Handle input events
     */
    handleInput(event) {
        if (!this.isRecording) return;

        const element = event.target;
        const metadata = this.extractElementMetadata(element, 'input');
        metadata.value = element.value; // Capture input value (optional)

        this.capturedInteractions.push(metadata);
        console.log('[Recorder] Captured input:', metadata);
        this.notifyCapture(metadata);
    }

    /**
     * Handle change events (for dropdowns, checkboxes, etc.)
     */
    handleChange(event) {
        if (!this.isRecording) return;

        const element = event.target;
        const metadata = this.extractElementMetadata(element, 'change');
        metadata.value = element.value;

        this.capturedInteractions.push(metadata);
        console.log('[Recorder] Captured change:', metadata);
        this.notifyCapture(metadata);
    }

    /**
     * Handle mouse over for highlighting
     */
    handleMouseOver(event) {
        if (!this.isRecording) return;

        const element = event.target;
        if (this.isInteractiveElement(element)) {
            element.classList.add('recorder-highlight');
            this.highlightedElement = element;
        }
    }

    /**
     * Handle mouse out to remove highlighting
     */
    handleMouseOut(event) {
        if (!this.isRecording) return;

        const element = event.target;
        element.classList.remove('recorder-highlight');
        if (this.highlightedElement === element) {
            this.highlightedElement = null;
        }
    }

    /**
     * Check if element is interactive
     */
    isInteractiveElement(element) {
        const interactiveTags = ['BUTTON', 'A', 'INPUT', 'SELECT', 'TEXTAREA'];
        const interactiveRoles = ['button', 'link', 'textbox', 'combobox'];
        
        return interactiveTags.includes(element.tagName) ||
               interactiveRoles.includes(element.getAttribute('role')) ||
               element.hasAttribute('onclick') ||
               element.classList.contains('slds-button') ||
               element.tagName.startsWith('LIGHTNING-') ||
               element.tagName.startsWith('C-OMNISCRIPT-');
    }

    /**
     * Extract comprehensive metadata from an element
     */
    extractElementMetadata(element, action) {
        const framework = this.detectFramework(element);
        const componentType = this.detectComponentType(element);
        const label = this.extractLabel(element);
        const selector = this.generateCSSSelector(element);
        const xpath = this.generateXPath(element);
        const attributes = this.extractAttributes(element);

        return {
            timestamp: new Date().toISOString(),
            label: label,
            action: action,
            selector: selector,
            xpath: xpath,
            framework: framework,
            componentType: componentType,
            tagName: element.tagName.toLowerCase(),
            innerText: element.innerText?.substring(0, 100) || '',
            attributes: attributes,
            isNested: this.isNestedComponent(element),
            parentFramework: this.detectParentFramework(element)
        };
    }

    /**
     * Detect if element belongs to Lightning or OmniScript framework
     */
    detectFramework(element) {
        // Check element and its parents for framework indicators
        let current = element;
        let depth = 0;
        const maxDepth = 10;

        while (current && depth < maxDepth) {
            // OmniScript detection
            if (this.isOmniScriptElement(current)) {
                return 'OmniScript';
            }

            // Lightning detection
            if (this.isLightningElement(current)) {
                return 'Lightning';
            }

            current = current.parentElement;
            depth++;
        }

        return 'Standard';
    }

    /**
     * Check if element is an OmniScript component
     */
    isOmniScriptElement(element) {
        const tagName = element.tagName.toLowerCase();
        const className = element.className || '';
        
        // Check tag name
        if (tagName.startsWith('c-omniscript-') || 
            tagName.startsWith('c-omni-') ||
            tagName.includes('vlocity')) {
            return true;
        }

        // Check attributes
        const attributes = Array.from(element.attributes || []);
        if (attributes.some(attr => 
            attr.name.startsWith('data-omnistudio-') || 
            attr.name.startsWith('data-omni-'))) {
            return true;
        }

        // Check classes
        if (className.includes('vlocity_') || 
            className.includes('omnistudio-') ||
            className.includes('nds-')) {
            return true;
        }

        return false;
    }

    /**
     * Check if element is a Lightning component
     */
    isLightningElement(element) {
        const tagName = element.tagName.toLowerCase();
        const className = element.className || '';

        // Check tag name
        if (tagName.startsWith('lightning-') || 
            tagName.startsWith('force-')) {
            return true;
        }

        // Check attributes
        const attributes = Array.from(element.attributes || []);
        if (attributes.some(attr => 
            attr.name.startsWith('data-aura-') || 
            attr.name.startsWith('data-lightning-'))) {
            return true;
        }

        // Check classes (Salesforce Lightning Design System)
        if (className.includes('slds-') || 
            className.includes('forceStyle')) {
            return true;
        }

        return false;
    }

    /**
     * Detect component type (button, input, dropdown, etc.)
     */
    detectComponentType(element) {
        const tagName = element.tagName.toLowerCase();
        const role = element.getAttribute('role');
        const type = element.getAttribute('type');

        // Direct tag mapping
        const tagMap = {
            'button': 'button',
            'a': 'link',
            'input': type || 'input',
            'select': 'dropdown',
            'textarea': 'textarea'
        };

        if (tagMap[tagName]) {
            return tagMap[tagName];
        }

        // Lightning components
        if (tagName.startsWith('lightning-')) {
            return tagName.replace('lightning-', '');
        }

        // OmniScript components
        if (tagName.startsWith('c-omniscript-')) {
            return tagName.replace('c-omniscript-', '');
        }

        // Role-based detection
        if (role) {
            return role;
        }

        return 'unknown';
    }

    /**
     * Extract visible label or text from element
     */
    extractLabel(element) {
        // Check for aria-label
        if (element.getAttribute('aria-label')) {
            return element.getAttribute('aria-label');
        }

        // Check for associated label
        const id = element.id;
        if (id) {
            const label = document.querySelector(`label[for="${id}"]`);
            if (label) {
                return label.innerText.trim();
            }
        }

        // Check for placeholder
        if (element.placeholder) {
            return element.placeholder;
        }

        // Check for title
        if (element.title) {
            return element.title;
        }

        // Check for button text (including nested content)
        if (element.tagName === 'BUTTON' || element.tagName === 'A') {
            const text = element.innerText?.trim() || element.textContent?.trim();
            if (text && text.length > 0) {
                return text.substring(0, 50);
            }
        }
        
        // Check for clickable elements with text
        if (element.onclick || element.getAttribute('role') === 'button') {
            const text = element.innerText?.trim() || element.textContent?.trim();
            if (text && text.length > 0) {
                return text.substring(0, 50);
            }
        }

        // Check for name attribute
        if (element.name) {
            return element.name;
        }

        // Check parent label
        const parentLabel = element.closest('label');
        if (parentLabel) {
            return parentLabel.innerText.trim();
        }

        // Check for data attributes
        const dataLabel = element.getAttribute('data-label') || 
                         element.getAttribute('data-field-label') ||
                         element.getAttribute('data-omnistudio-field');
        if (dataLabel) {
            return dataLabel;
        }

        return element.innerText?.trim().substring(0, 50) || 'Unlabeled';
    }

    /**
     * Generate CSS selector for element
     */
    generateCSSSelector(element) {
        // If element has unique ID
        if (element.id) {
            return `#${element.id}`;
        }

        // Build selector path
        const path = [];
        let current = element;

        while (current && current.tagName !== 'BODY') {
            let selector = current.tagName.toLowerCase();

            // Add classes
            if (current.className && typeof current.className === 'string') {
                const classes = current.className.trim().split(/\s+/)
                    .filter(c => c && !c.startsWith('recorder-'))
                    .slice(0, 3);
                if (classes.length > 0) {
                    selector += '.' + classes.join('.');
                }
            }

            // Add data attributes for uniqueness
            const dataAttrs = ['data-omnistudio-field', 'data-field-name', 'name'];
            for (const attr of dataAttrs) {
                const value = current.getAttribute(attr);
                if (value) {
                    selector += `[${attr}="${value}"]`;
                    break;
                }
            }

            path.unshift(selector);
            current = current.parentElement;

            // Limit depth
            if (path.length >= 5) break;
        }

        return path.join(' > ');
    }

    /**
     * Generate XPath for element - improved for reliability
     */
    generateXPath(element) {
        // Strategy 1: Use ID if available and doesn't contain dynamic parts
        if (element.id && !element.id.includes(':') && element.id.length < 20) {
            return `//*[@id="${element.id}"]`;
        }

        // Strategy 2: Try to use unique attributes
        const uniqueAttrs = ['name', 'data-field-name', 'data-omnistudio-field', 'aria-label'];
        for (const attr of uniqueAttrs) {
            const value = element.getAttribute(attr);
            if (value && value.length > 0 && value.length < 100) {
                return `//*[@${attr}="${value}"]`;
            }
        }

        // Strategy 3: For input fields, use label association
        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
            const label = this.extractLabel(element);
            if (label && label !== 'Unlabeled') {
                // Try to find by placeholder
                const placeholder = element.getAttribute('placeholder');
                if (placeholder) {
                    return `//input[@placeholder="${placeholder}"]`;
                }
                // Try to find by associated label
                return `//label[contains(text(), "${label}")]/following::input[1] | //label[contains(text(), "${label}")]/..//input`;
            }
        }

        // Strategy 4: For checkboxes/toggles, use label or aria-label
        if (element.type === 'checkbox' || element.getAttribute('role') === 'switch') {
            const ariaLabel = element.getAttribute('aria-label');
            if (ariaLabel) {
                return `//input[@type='checkbox' and @aria-label='${ariaLabel}']`;
            }
            // Try to find by associated label
            const id = element.id;
            if (id) {
                return `//label[@for='${id}']/..//input[@type='checkbox'] | //input[@type='checkbox' and @id='${id}']`;
            }
            // Try to find by nearby text
            const label = this.extractLabel(element);
            if (label && label !== 'Unlabeled') {
                return `//label[contains(text(), '${label}')]/..//input[@type='checkbox'] | //input[@type='checkbox' and contains(@aria-label, '${label}')]`;
            }
        }

        // Strategy 5: For buttons/links, use text content (simplified)
        if (element.tagName === 'BUTTON' || element.tagName === 'A' || element.getAttribute('role') === 'button') {
            const text = element.innerText?.trim();
            if (text && text.length > 0 && text.length < 100) {
                // Use simple text-based selector
                return `//*[contains(text(), "${text}")]`;
            }
        }
        
        // Strategy 6: For navigation tiles/cards with text
        const innerText = element.innerText?.trim();
        if (innerText && innerText.length > 0 && innerText.length < 100) {
            // Check if it's a clickable element with meaningful text
            if (element.tagName === 'DIV' || element.tagName === 'SPAN') {
                const isClickable = element.onclick || 
                                   element.closest('a') || 
                                   element.closest('[role="button"]') ||
                                   element.closest('[onclick]');
                if (isClickable) {
                    return `//*[contains(text(), "${innerText}")]`;
                }
            }
        }

        // Strategy 5: Build relative path with more context
        const path = [];
        let current = element;
        let depth = 0;
        const maxDepth = 8;

        while (current && current.tagName !== 'BODY' && depth < maxDepth) {
            let segment = current.tagName.toLowerCase();
            
            // Add identifying attributes
            const classAttr = current.className;
            if (classAttr && typeof classAttr === 'string') {
                const classes = classAttr.trim().split(/\s+/)
                    .filter(c => c && !c.startsWith('recorder-') && !c.match(/^\d/) && c.length < 30);
                if (classes.length > 0) {
                    // Use first meaningful class
                    segment += `[contains(@class, "${classes[0]}")]`;
                }
            }
            
            // Add position only if no other identifier
            if (!segment.includes('[')) {
                let index = 1;
                let sibling = current.previousElementSibling;
                while (sibling) {
                    if (sibling.tagName === current.tagName) {
                        index++;
                    }
                    sibling = sibling.previousElementSibling;
                }
                segment += `[${index}]`;
            }

            path.unshift(segment);
            current = current.parentElement;
            depth++;
        }

        return '//' + path.join('/');
    }

    /**
     * Extract relevant attributes from element
     */
    extractAttributes(element) {
        const attributes = {};
        const relevantAttrs = [
            'id', 'name', 'class', 'type', 'role', 'placeholder',
            'data-omnistudio-field', 'data-field-name', 'data-aura-rendered-by',
            'aria-label', 'title', 'value'
        ];

        for (const attr of relevantAttrs) {
            const value = element.getAttribute(attr);
            if (value) {
                attributes[attr] = value;
            }
        }

        return attributes;
    }

    /**
     * Check if element is nested within a dynamic component
     */
    isNestedComponent(element) {
        let current = element.parentElement;
        let depth = 0;
        const maxDepth = 5;

        while (current && depth < maxDepth) {
            const tagName = current.tagName.toLowerCase();
            if (tagName.startsWith('c-omniscript-') || 
                tagName.startsWith('lightning-')) {
                return true;
            }
            current = current.parentElement;
            depth++;
        }

        return false;
    }

    /**
     * Detect parent framework for nested components
     */
    detectParentFramework(element) {
        let current = element.parentElement;
        let depth = 0;
        const maxDepth = 10;

        while (current && depth < maxDepth) {
            if (this.isOmniScriptElement(current)) {
                return 'OmniScript';
            }
            if (this.isLightningElement(current)) {
                return 'Lightning';
            }
            current = current.parentElement;
            depth++;
        }

        return null;
    }

    /**
     * Notify parent window of captured interaction
     */
    notifyCapture(metadata) {
        // Send message to parent window (for UI updates)
        window.postMessage({
            type: 'RECORDER_CAPTURE',
            data: metadata
        }, '*');

        // Store in window object for Python access
        if (!window.__recorderData) {
            window.__recorderData = [];
        }
        window.__recorderData.push(metadata);
    }

    /**
     * Get all captured interactions
     */
    getCapturedInteractions() {
        return this.capturedInteractions;
    }

    /**
     * Clear captured interactions
     */
    clearCaptures() {
        this.capturedInteractions = [];
        if (window.__recorderData) {
            window.__recorderData = [];
        }
    }
}

// Initialize recorder instance
if (typeof window !== 'undefined') {
    window.salesforceRecorder = new SalesforceRecorder();
    console.log('[Recorder] Salesforce Recorder initialized');
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SalesforceRecorder;
}
