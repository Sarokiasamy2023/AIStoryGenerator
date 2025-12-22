"""
AI-powered Gherkin to Test Steps Converter
Uses OpenAI API to convert Gherkin scenarios to automation test steps
"""

import os
from typing import List, Dict, Optional
import httpx
import json


class AIGherkinConverter:
    """Convert Gherkin scenarios to test steps using OpenAI API"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY', '')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        self.max_tokens = int(os.getenv('MAX_TOKENS', '2000'))
        self.temperature = float(os.getenv('TEMPERATURE', '0.7'))
        self.api_url = "https://api.openai.com/v1/chat/completions"
    
    def is_available(self) -> bool:
        """Check if OpenAI API is configured"""
        return bool(self.api_key and self.api_key.startswith('sk-'))
    
    async def convert_gherkin_to_steps(self, gherkin_text: str, use_parameters: bool = True) -> Dict:
        """
        Convert Gherkin scenario to automation test steps
        
        Args:
            gherkin_text: Gherkin scenario text
            use_parameters: Whether to use parameter placeholders like %FieldName%
            
        Returns:
            Dict with 'steps' (list) and 'total_steps' (int)
        """
        if not self.is_available():
            raise ValueError("OpenAI API key not configured")
        
        prompt = self._build_prompt(gherkin_text, use_parameters)
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert QA automation engineer specializing in test automation. Generate detailed automation test steps."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens
                }
            )
            
            if response.status_code != 200:
                error_data = response.json() if response.text else {}
                raise Exception(f"OpenAI API error: {response.status_code} - {error_data}")
            
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            # Parse the response - it should be plain text steps
            steps = content.strip().split('\n')
            steps = [step.strip() for step in steps if step.strip()]
            
            return {
                'steps': steps,
                'total_steps': len(steps),
                'source': 'OpenAI-Python'
            }
    
    def _build_prompt(self, gherkin_text: str, use_parameters: bool) -> str:
        """Build the prompt for OpenAI API"""
        
        prompt = f"""Convert the following Gherkin scenario to detailed automation test steps.

Gherkin Input:
{gherkin_text}

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

Generate the automation steps now. Return ONLY the steps, one per line, no additional text."""

        return prompt


# Global instance
_ai_converter = None


def get_ai_gherkin_converter() -> AIGherkinConverter:
    """Get or create the global AI Gherkin converter instance"""
    global _ai_converter
    if _ai_converter is None:
        _ai_converter = AIGherkinConverter()
    return _ai_converter
