const OpenAI = require('openai');
const axios = require('axios');

class AIService {
    constructor() {
        this.provider = process.env.AI_PROVIDER || 'openai';
        this.initializeProvider();
    }

    initializeProvider() {
        if (this.provider === 'openai' && process.env.OPENAI_API_KEY) {
            this.openai = new OpenAI({
                apiKey: process.env.OPENAI_API_KEY
            });
            this.model = process.env.OPENAI_MODEL || 'gpt-4o-mini';
        }
    }

    async generateTestCases(userStory, examples = null) {
        const prompt = this.buildTestCasePrompt(userStory, examples);
        
        try {
            const response = await this.callAI(prompt);
            return this.parseTestCasesResponse(response);
        } catch (error) {
            console.error('Error generating test cases:', error);
            throw new Error('Failed to generate test cases: ' + error.message);
        }
    }

    async generateTestSteps(testCase, examples = null) {
        const prompt = this.buildTestStepsPrompt(testCase, examples);
        
        try {
            const response = await this.callAI(prompt);
            return this.parseTestStepsResponse(response);
        } catch (error) {
            console.error('Error generating test steps:', error);
            throw new Error('Failed to generate test steps: ' + error.message);
        }
    }

    buildTestCasePrompt(userStory, examples) {
        let prompt = `You are an expert QA engineer. Convert the following user story into comprehensive test cases.

Generate test cases for:
1. **Positive Scenarios**: Happy path, expected behavior
2. **Negative Scenarios**: Invalid inputs, error conditions
3. **Edge Cases**: Boundary conditions, unusual but valid scenarios

User Story:
${userStory}

`;

        if (examples) {
            prompt += `\nHere are examples of the expected format:\n${examples}\n`;
        }

        prompt += `
Please provide test cases in the following JSON format:
{
    "testCases": [
        {
            "id": "TC001",
            "title": "Test case title",
            "type": "positive|negative|edge",
            "priority": "high|medium|low",
            "description": "Detailed description",
            "preconditions": ["List of preconditions"],
            "expectedResult": "Expected outcome"
        }
    ]
}

Generate at least:
- 3-5 positive test cases
- 3-5 negative test cases
- 2-3 edge case scenarios

Return ONLY the JSON object, no additional text.`;

        return prompt;
    }

    buildTestStepsPrompt(testCase, examples) {
        let prompt = `You are an expert QA automation engineer. Convert the following test case into detailed, automation-ready test steps.

Test Case:
${JSON.stringify(testCase, null, 2)}

`;

        if (examples) {
            prompt += `\nHere are examples of the expected format:\n${examples}\n`;
        }

        prompt += `
Generate VERY DETAILED automation test steps following these EXACT rules:

1. **Action Format (CRITICAL - Follow exactly):**
   - Text fields: Type "%FieldName%" into "FieldName"
   - Dropdowns: Select "%FieldName%" from Dropdown "FieldName"
   - Textareas: Fill textarea "%FieldName%" with "FieldName"
   - Buttons: Click "ButtonName"
   - Wait: Wait for 1 seconds (after EVERY action)

2. **CSV Data Placeholders:**
   - Format: %FieldName% (percent signs around field name, NO quotes inside)
   - Examples: 
     * Type "%Username%" into "Username"
     * Type "%Number of people on listserv%" into "Number of people on listserv"
     * Select "%Behavioral Health%" from Dropdown "Behavioral Health"

3. **Dropdown/Select Fields:**
   - MUST use: Select "%FieldName%" from Dropdown "FieldName"
   - Capital D in "Dropdown"
   - Example: Select "%Articles%" from Dropdown "Articles"

4. **Textarea Fields:**
   - Use: Fill textarea "%FieldName%" with "FieldName"
   - Example: Fill textarea "%Collaborative effort in your state%" with "Collaborative effort in your state"

5. **Wait Times (CRITICAL):**
   - Add "Wait for 1 seconds" after EVERY action
   - No exceptions

6. **NO Section Headers:**
   - Do NOT use # for sections
   - Just list steps sequentially
   - Only use # for comments if needed (e.g., #Select "%Toolkits%" from Dropdown "Toolkits")

7. **Include ALL fields:**
   - Generate steps for EVERY field mentioned
   - Each field gets its own Type/Select/Fill line
   - Each action followed by Wait for 1 seconds

EXACT FORMAT EXAMPLE:
Click "HSD PERFORMANCE REPORTS"
Wait for 1 seconds
Click "Recently Viewed"
Wait for 1 seconds
Click "In Progress Reports"
Wait for 1 seconds
Click "HSD-01078"
Wait for 1 seconds
Click "Edit"
Wait for 1 seconds
Click "Next"
Wait for 1 seconds
Type "%Number of people on listserv%" into "Number of people on listserv"
Wait for 1 seconds
Type "%Number of people receiving newsletter (via mail or electronic)%" into "Number of people receiving newsletter (via mail or electronic)"
Wait for 1 seconds
Select "%Is the audience/membership for the listserv the same as for the newsletter?%" from Dropdown "Is the audience/membership for the listserv the same as for the newsletter?"
Wait for 1 seconds
Select "%Articles%" from Dropdown "Articles"
Wait for 1 seconds
Type "%Describe one tool that you created to address a problem in your state.%" into "Describe one tool that you created to address a problem in your state."
Wait for 1 seconds
Click "Next"
Wait for 1 seconds
Select "%Behavioral Health%" from Dropdown "Behavioral Health"
Wait for 1 seconds
Fill textarea "%Collaborative effort in your state%" with "Collaborative effort in your state"
Wait for 1 seconds

Please provide the test steps in the following JSON format:
{
    "automationSteps": [
        "Click \\"HSD PERFORMANCE REPORTS\\"",
        "Wait for 1 seconds",
        "Click \\"Recently Viewed\\"",
        "Wait for 1 seconds",
        "Type \\"%Field Name%\\" into \\"Field Name\\"",
        "Wait for 1 seconds",
        "Select \\"%Dropdown Field%\\" from Dropdown \\"Dropdown Field\\"",
        "Wait for 1 seconds",
        "Fill textarea \\"%Textarea Field%\\" with \\"Textarea Field\\"",
        "Wait for 1 seconds",
        "Click \\"Next\\"",
        "Wait for 1 seconds"
    ]
}

CRITICAL REQUIREMENTS:
1. Generate 50-100+ steps for a complete workflow
2. Include EVERY SINGLE field mentioned in the test case
3. Use Type "%FieldName%" into "FieldName" for text fields
4. Use Select "%FieldName%" from Dropdown "FieldName" for dropdowns (capital D)
5. Use Fill textarea "%FieldName%" with "FieldName" for textareas
6. Include "Wait for 1 seconds" after EVERY action
7. NO section headers with #
8. CSV placeholders: %FieldName% (no quotes inside percent signs)

Return ONLY the JSON object with the automationSteps array, no additional text.`;

        return prompt;
    }

    async callAI(prompt, useJsonFormat = true) {
        if (this.provider === 'openai' && this.openai) {
            return await this.callOpenAI(prompt, useJsonFormat);
        } else if (process.env.LOCAL_LLM_ENDPOINT) {
            return await this.callLocalLLM(prompt);
        } else {
            throw new Error('No AI provider configured');
        }
    }

    async callOpenAI(prompt, useJsonFormat = true) {
        const options = {
            model: this.model,
            messages: [
                {
                    role: 'system',
                    content: useJsonFormat 
                        ? 'You are an expert QA engineer specializing in test case design and test automation. Always respond with valid JSON.'
                        : 'You are an expert QA engineer specializing in test automation. Generate detailed automation test steps.'
                },
                {
                    role: 'user',
                    content: prompt
                }
            ],
            temperature: parseFloat(process.env.TEMPERATURE) || 0.7,
            max_tokens: parseInt(process.env.MAX_TOKENS) || 8000
        };

        // Only add response_format for JSON responses
        if (useJsonFormat) {
            options.response_format = { type: "json_object" };
        }

        const response = await this.openai.chat.completions.create(options);
        return response.choices[0].message.content;
    }

    async callLocalLLM(prompt) {
        const response = await axios.post(process.env.LOCAL_LLM_ENDPOINT, {
            model: process.env.LOCAL_LLM_MODEL || 'llama2',
            prompt: prompt,
            stream: false
        });

        return response.data.response;
    }

    parseTestCasesResponse(response) {
        try {
            const parsed = JSON.parse(response);
            
            // Validate structure
            if (!parsed.testCases || !Array.isArray(parsed.testCases)) {
                throw new Error('Invalid response structure');
            }

            // Add IDs if missing
            parsed.testCases = parsed.testCases.map((tc, index) => ({
                id: tc.id || `TC${String(index + 1).padStart(3, '0')}`,
                title: tc.title || 'Untitled Test Case',
                type: tc.type || 'positive',
                priority: tc.priority || 'medium',
                description: tc.description || '',
                preconditions: tc.preconditions || [],
                expectedResult: tc.expectedResult || ''
            }));

            return parsed;
        } catch (error) {
            console.error('Error parsing test cases response:', error);
            console.error('Response:', response);
            throw new Error('Failed to parse AI response');
        }
    }

    async convertGherkinToSteps(gherkinText) {
        try {
            console.log('Converting Gherkin to automation steps...');
            
            const prompt = `Convert the following Gherkin scenario to detailed automation test steps.

Gherkin Input:
${gherkinText}

Generate automation steps following these EXACT rules:

1. **Action Format (CRITICAL - Follow exactly):**
   - Text fields: Type "%FieldName%" into "FieldName"
   - Dropdowns: Select "%FieldName%" from Dropdown "FieldName"
   - Textareas: Fill textarea "%FieldName%" with "FieldName"
   - Buttons: Click "ButtonName"
   - Wait: Wait for 1 seconds (after EVERY action)

2. **CSV Placeholders (CRITICAL):**
   - Format: %FieldName% (NO quotes inside percent signs)
   - Correct: Type "%Newsletter%" into "Newsletter"
   - Correct: Select "%Articles%" from Dropdown "Articles"
   - WRONG: Type "%"Newsletter"%" into "Newsletter"
   - PRESERVE all special characters in field names (?, !, -, /, etc.)
   - Example: Type "%How many newsletter issues per year (if known)?%" into "How many newsletter issues per year (if known)?"

3. **Convert Gherkin steps (CRITICAL - Use FIELD NAME not value):**
   - "When the user enters X into Y" → Type "%Y%" into "Y"
   - "And the user enters X into Y" → Type "%Y%" into "Y"
   - "And the user enters X into textarea Y" → Fill textarea "%Y%" with "Y"
   - "And the user selects X for Y" → Select "%Y%" from Dropdown "Y" (Y is the FIELD NAME, not X)
   - "And the user clicks X" → Click "X"
   - "When the user navigates to X" → Click "X"
   - "And the user opens X" → Click "X"
   - "And I click X" → Click "X"
   - "When I click on X button" → Click "X"
   - CRITICAL: Keep ALL characters in field names including ?, !, -, /, (, ), etc.

4. **Special field handling:**
   - If field name contains "textarea" or Gherkin says "into textarea" → Use Fill textarea format
   - If field name is "Other-Specify" → Use Type format (not Select)
   - All other dropdowns → Use Select format

5. **CRITICAL for Select statements:**
   - ALWAYS use the FIELD NAME in both the CSV placeholder and the field name
   - Gherkin: "And the user selects 'Yes' for 'Behavioral Health'"
   - Output: Select "%Behavioral Health%" from Dropdown "Behavioral Health"
   - NOT: Select "%Yes%" from Dropdown "Behavioral Health"
   - The value "Yes" is ignored - use the field name "Behavioral Health"

6. **Add Wait for 1 seconds after EVERY action**

7. **Output format:** Plain list of steps, no JSON, no section headers

EXAMPLES:
Gherkin: When the user enters "test" into "Username"
Output: Type "%Username%" into "Username"
        Wait for 1 seconds

Gherkin: And the user selects "Yes" for "Articles"
Output: Select "%Articles%" from Dropdown "Articles"
        Wait for 1 seconds

Gherkin: And the user enters "100" into "Number of people on listserv"
Output: Type "%Number of people on listserv%" into "Number of people on listserv"
        Wait for 1 seconds

Gherkin: And the user enters "12" into "How many newsletter issues per year (if known)?"
Output: Type "%How many newsletter issues per year (if known)?%" into "How many newsletter issues per year (if known)?"
        Wait for 1 seconds

Gherkin: And the user enters "Custom topic description" into "Other-Specify"
Output: Type "%Other-Specify%" into "Other-Specify"
        Wait for 1 seconds

Gherkin: And the user enters "Worked with local hospitals" into textarea "Collaborative effort in your state"
Output: Fill textarea "%Collaborative effort in your state%" with "Collaborative effort in your state"
        Wait for 1 seconds

Gherkin: And the user clicks "Next"
Output: Click "Next"
        Wait for 1 seconds

Generate the automation steps now. Return ONLY the steps, one per line, no additional text.`;

            const response = await this.callAI(prompt, false); // Use plain text format
            
            // Parse response - it should be plain text steps
            const steps = response.trim().split('\n').filter(line => line.trim());
            
            return steps;
        } catch (error) {
            console.error('Error in convertGherkinToSteps:', error);
            throw new Error(`Failed to convert Gherkin: ${error.message}`);
        }
    }

    parseTestStepsResponse(response) {
        try {
            const parsed = JSON.parse(response);
            
            // Check for new automation steps format
            if (parsed.automationSteps && Array.isArray(parsed.automationSteps)) {
                return {
                    automationSteps: parsed.automationSteps,
                    testSteps: [], // Keep for backward compatibility
                    setupSteps: [],
                    teardownSteps: []
                };
            }
            
            // Fallback to old format
            if (!parsed.testSteps || !Array.isArray(parsed.testSteps)) {
                throw new Error('Invalid response structure');
            }

            // Ensure step numbers
            parsed.testSteps = parsed.testSteps.map((step, index) => ({
                stepNumber: step.stepNumber || index + 1,
                action: step.action || '',
                testData: step.testData || '',
                expectedResult: step.expectedResult || ''
            }));

            parsed.setupSteps = parsed.setupSteps || [];
            parsed.teardownSteps = parsed.teardownSteps || [];
            parsed.automationSteps = []; // Add empty for compatibility

            return parsed;
        } catch (error) {
            console.error('Error parsing test steps response:', error);
            console.error('Response:', response);
            throw new Error('Failed to parse AI response');
        }
    }
}

module.exports = new AIService();
