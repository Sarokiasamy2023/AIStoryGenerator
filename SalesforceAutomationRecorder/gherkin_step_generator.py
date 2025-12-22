"""Gherkin Step Generator

Converts Gherkin-style test scenarios (Given/When/Then/And) into 
executable test steps with proper syntax for the test executor.

Input: Gherkin text with Given/When/Then/And statements
Output: Executable test steps like Type "value" into "field", Click "button", etc.
"""

from __future__ import annotations
import re
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class GherkinStep:
    """A parsed Gherkin step with its type and content."""
    keyword: str  # Given, When, Then, And
    text: str
    table_data: List[Dict[str, str]] = None  # For data tables


class GherkinStepGenerator:
    """Converts Gherkin scenarios to executable test steps."""

    def __init__(self, use_parameters: bool = True):
        self.use_parameters = use_parameters  # Replace hardcoded values with %field% placeholders
        self.wait_patterns = {
            "navigates": 1,
            "opens": 2,
            "clicks": 0,
            "enters": 0,
            "selects": 0,
        }

    def parse_and_generate(self, gherkin_text: str) -> Dict[str, Any]:
        """Parse Gherkin text and generate executable test steps."""
        # Parse Gherkin into structured steps
        gherkin_steps = self._parse_gherkin(gherkin_text)
        
        # Convert to executable steps
        executable_steps = []
        for step in gherkin_steps:
            converted = self._convert_step(step)
            executable_steps.extend(converted)
        
        return {
            "total_steps": len(executable_steps),
            "steps": executable_steps,
            "gherkin_count": len(gherkin_steps),
        }

    def _parse_gherkin(self, text: str) -> List[GherkinStep]:
        """Parse Gherkin text into structured steps."""
        steps = []
        lines = text.strip().split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                i += 1
                continue
            
            # Check for Gherkin keywords
            match = re.match(r'^(Given|When|Then|And)\s+(.+)$', line, re.IGNORECASE)
            if match:
                keyword = match.group(1)
                step_text = match.group(2)
                
                # Check if next lines contain a data table
                table_data = []
                j = i + 1
                while j < len(lines) and lines[j].strip().startswith('|'):
                    row = [cell.strip() for cell in lines[j].strip().split('|')[1:-1]]
                    if row:
                        table_data.append(row)
                    j += 1
                
                # Convert table to dict format
                parsed_table = None
                if table_data and len(table_data) > 0:
                    # First row is headers, rest are data
                    if len(table_data) == 1:
                        # Single row table (no headers, just data)
                        parsed_table = [{"field": table_data[0][0], "value": table_data[0][1]}]
                    else:
                        # Multi-row table with headers
                        headers = table_data[0]
                        parsed_table = []
                        for row in table_data[1:]:
                            if len(row) == len(headers):
                                parsed_table.append(dict(zip(headers, row)))
                
                steps.append(GherkinStep(
                    keyword=keyword,
                    text=step_text,
                    table_data=parsed_table
                ))
                
                i = j  # Skip table lines
            else:
                i += 1
        
        return steps

    def _convert_step(self, step: GherkinStep) -> List[str]:
        """Convert a single Gherkin step to executable test steps."""
        text = step.text
        text_lower = text.lower()
        results = []
        
        # Pattern: I see "button" (verification)
        match = re.search(r'I see\s+[\'"]([^\'"]+)[\'"]', text, re.IGNORECASE)
        if match:
            results.append(f'Verify "{match.group(1)}"')
            return results
        
        # Pattern: I click 'Edit' of 'Form name'
        match = re.search(r'I click\s+[\'"]Edit[\'"]\s+of\s+[\'"]([^\'"]+)[\'"]', text, re.IGNORECASE)
        if match:
            form_name = match.group(1)
            results.append(f'Click "{form_name}"')
            results.append('Wait for 2 seconds')
            return results
        
        # Pattern: enters the username "value"
        match = re.search(r'enters the username\s+"([^"]+)"', text, re.IGNORECASE)
        if match:
            value = "%Username%" if self.use_parameters else match.group(1)
            results.append(f'Type "{value}" into "Username"')
            return results
        
        # Pattern: enters the password "value"
        match = re.search(r'enters the password\s+"([^"]+)"', text, re.IGNORECASE)
        if match:
            value = "%Password%" if self.use_parameters else match.group(1)
            results.append(f'Type "{value}" into "Password"')
            return results
        
        # Pattern: clicks "button"
        match = re.search(r'clicks?\s+"([^"]+)"', text, re.IGNORECASE)
        if match:
            button = match.group(1)
            results.append(f'Click "{button}"')
            # Add wait if appropriate
            if any(kw in text_lower for kw in ["navigates", "opens"]):
                results.append("Wait for 2 seconds")
            return results
        
        # Pattern: navigates to "page"
        match = re.search(r'navigates to\s+"([^"]+)"', text, re.IGNORECASE)
        if match:
            results.append(f'Click "{match.group(1)}"')
            results.append("Wait for 1 seconds")
            return results
        
        # Pattern: selects "option"
        match = re.search(r'selects\s+"([^"]+)"', text, re.IGNORECASE)
        if match:
            results.append(f'Click "{match.group(1)}"')
            results.append("Wait for 1 seconds")
            return results
        
        # Pattern: opens "item"
        match = re.search(r'opens\s+(?:the\s+)?(?:report\s+)?"([^"]+)"', text, re.IGNORECASE)
        if match:
            results.append(f'Click "{match.group(1)}"')
            results.append("Wait for 2 seconds")
            return results
        
        # Pattern: should see "text"
        match = re.search(r'should see\s+"([^"]+)"', text, re.IGNORECASE)
        if match:
            results.append(f'Verify "{match.group(1)}"')
            return results
        
        # Pattern: displays the ... text
        if "displays" in text_lower:
            # Extract text after "displays"
            match = re.search(r'displays\s+(?:the\s+)?(.+?)(?:\s+text)?$', text, re.IGNORECASE)
            if match:
                # This is typically a verify step with long text - extract from context
                results.append(f'Verify "The purpose of this collection is to collect information..."')
                return results
        
        # Pattern: enters "value" into field
        match = re.search(r'enters\s+"([^"]+)"\s+into\s+(?:the\s+)?(.+?)(?:\s+field)?$', text, re.IGNORECASE)
        if match:
            field = match.group(2).strip()
            value = f"%{field}%" if self.use_parameters else match.group(1)
            results.append(f'Type "{value}" into "{field}"')
            return results
        
        # Pattern: enters ... data: (with table)
        if step.table_data and ("enters" in text_lower or "enter" in text_lower):
            for row in step.table_data:
                if "field" in row and "value" in row:
                    field = row["field"]
                    value = f"%{field}%" if self.use_parameters else row["value"]
                    results.append(f'Type "{value}" into "{field}"')
                else:
                    # Use first two columns as field/value
                    keys = list(row.keys())
                    if len(keys) >= 2:
                        field = row[keys[0]]
                        value = f"%{field}%" if self.use_parameters else row[keys[1]]
                        results.append(f'Type "{value}" into "{field}"')
            
            # Add Next click after data entry
            if results:
                results.append('Click "Next"')
                results.append('Wait for 3 seconds')
            return results
        
        # Pattern: uploads the ... file
        match = re.search(r'uploads?\s+(?:the\s+)?(.+?)(?:\s+file)?$', text, re.IGNORECASE)
        if match:
            file_type = match.group(1).strip()
            results.append(f'Upload file "Y:\\SalesforceAutomationRecorder\\test.txt" to "Upload Files"')
            results.append('Click "Done"')
            results.append('Wait for 2 seconds')
            return results
        
        # Pattern: checks "checkbox"
        match = re.search(r'checks?\s+"([^"]+)"', text, re.IGNORECASE)
        if match:
            results.append(f'Check "{match.group(1)}"')
            return results
        
        # Pattern: selects "option" for field
        match = re.search(r'selects\s+"([^"]+)"\s+for\s+(.+)$', text, re.IGNORECASE)
        if match:
            option = match.group(1)
            field = match.group(2).strip()
            results.append(f'select "{option}" from Dropdown "{field}"')
            return results
        
        # Pattern: acknowledges ... by clicking "button"
        match = re.search(r'acknowledges.+by clicking\s+"([^"]+)"', text, re.IGNORECASE)
        if match:
            results.append(f'Click "{match.group(1)}"')
            return results
        
        # Pattern: is on the ... page (Given step - usually no action)
        if "is on the" in text_lower and step.keyword.lower() == "given":
            # Skip - this is context, not an action
            return []
        
        # Default: create a comment for unrecognized patterns
        if not results:
            results.append(f'# {step.keyword}: {step.text}')
        
        return results
