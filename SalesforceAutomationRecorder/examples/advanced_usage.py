"""
Advanced Usage Example - Salesforce Automation Recorder

This example demonstrates advanced features like custom configuration,
data analysis, and automated test generation.
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automation_recorder import SalesforceRecorder


async def advanced_recording_example():
    """
    Advanced example with custom configuration and analysis
    """
    print("=" * 60)
    print("Salesforce Automation Recorder - Advanced Usage Example")
    print("=" * 60)
    
    # Initialize recorder with custom config
    recorder = SalesforceRecorder(config_path="config.json")
    
    # Your Salesforce URL (replace with your actual instance)
    salesforce_url = "https://your-instance.lightning.force.com"
    
    print(f"\nRecording session starting...")
    print(f"Target: {salesforce_url}\n")
    
    try:
        # Start recording
        await recorder.start_recording(salesforce_url)
        
        # Get captured data
        captured_data = recorder.get_captured_data()
        
        print(f"\n✓ Recording completed!")
        print(f"✓ Captured {len(captured_data)} interactions\n")
        
        # Analyze captured data
        analysis = analyze_interactions(captured_data)
        print_analysis(analysis)
        
        # Export with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"recordings/advanced_recording_{timestamp}.json"
        recorder.export_json(output_file)
        
        # Generate automation script
        generate_automation_script(captured_data, f"recordings/automation_script_{timestamp}.py")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await recorder.close()


def analyze_interactions(interactions):
    """
    Analyze captured interactions and generate insights
    """
    analysis = {
        'total': len(interactions),
        'by_framework': {},
        'by_action': {},
        'by_component': {},
        'nested_components': 0,
        'unique_selectors': set(),
        'timeline': []
    }
    
    for interaction in interactions:
        # Framework distribution
        framework = interaction.get('framework', 'Unknown')
        analysis['by_framework'][framework] = analysis['by_framework'].get(framework, 0) + 1
        
        # Action distribution
        action = interaction.get('action', 'unknown')
        analysis['by_action'][action] = analysis['by_action'].get(action, 0) + 1
        
        # Component type distribution
        component = interaction.get('componentType', 'unknown')
        analysis['by_component'][component] = analysis['by_component'].get(component, 0) + 1
        
        # Nested components
        if interaction.get('isNested', False):
            analysis['nested_components'] += 1
        
        # Unique selectors
        if interaction.get('selector'):
            analysis['unique_selectors'].add(interaction['selector'])
        
        # Timeline
        analysis['timeline'].append({
            'timestamp': interaction.get('timestamp'),
            'action': action,
            'label': interaction.get('label', 'Unlabeled')
        })
    
    analysis['unique_selectors'] = len(analysis['unique_selectors'])
    
    return analysis


def print_analysis(analysis):
    """
    Print analysis results in a formatted way
    """
    print("=" * 60)
    print("INTERACTION ANALYSIS")
    print("=" * 60)
    
    print(f"\n📊 Total Interactions: {analysis['total']}")
    
    print("\n🎯 Framework Distribution:")
    for framework, count in analysis['by_framework'].items():
        percentage = (count / analysis['total'] * 100) if analysis['total'] > 0 else 0
        print(f"  - {framework}: {count} ({percentage:.1f}%)")
    
    print("\n⚡ Action Distribution:")
    for action, count in analysis['by_action'].items():
        percentage = (count / analysis['total'] * 100) if analysis['total'] > 0 else 0
        print(f"  - {action}: {count} ({percentage:.1f}%)")
    
    print("\n🧩 Component Types:")
    for component, count in sorted(analysis['by_component'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  - {component}: {count}")
    
    print(f"\n🔗 Nested Components: {analysis['nested_components']}")
    print(f"🎨 Unique Selectors: {analysis['unique_selectors']}")
    
    print("\n⏱️ Interaction Timeline (first 5):")
    for item in analysis['timeline'][:5]:
        time = datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00')).strftime('%H:%M:%S')
        print(f"  [{time}] {item['action']}: {item['label']}")
    
    print("=" * 60)


def generate_automation_script(interactions, output_file):
    """
    Generate a Python automation script from captured interactions
    """
    script_lines = [
        '"""',
        'Auto-generated Salesforce Automation Script',
        f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        f'Total interactions: {len(interactions)}',
        '"""',
        '',
        'import asyncio',
        'from playwright.async_api import async_playwright',
        '',
        '',
        'async def run_automation():',
        '    """Execute recorded automation"""',
        '    async with async_playwright() as p:',
        '        browser = await p.chromium.launch(headless=False)',
        '        page = await browser.new_page()',
        '        ',
        '        # TODO: Add login logic here',
        '        # await page.goto("https://your-instance.lightning.force.com")',
        '        ',
    ]
    
    for i, interaction in enumerate(interactions, 1):
        action = interaction.get('action')
        selector = interaction.get('selector', '')
        label = interaction.get('label', 'Unlabeled')
        
        script_lines.append(f'        # Step {i}: {action} - {label}')
        
        if action == 'click':
            script_lines.append(f'        await page.click("{selector}")')
            script_lines.append('        await page.wait_for_timeout(500)')
        elif action == 'input':
            script_lines.append(f'        await page.fill("{selector}", "YOUR_INPUT_HERE")')
        elif action == 'change':
            script_lines.append(f'        await page.select_option("{selector}", "YOUR_OPTION_HERE")')
        
        script_lines.append('')
    
    script_lines.extend([
        '        # Close browser',
        '        await browser.close()',
        '',
        '',
        'if __name__ == "__main__":',
        '    asyncio.run(run_automation())',
    ])
    
    # Write to file
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(script_lines))
    
    print(f"\n✓ Generated automation script: {output_file}")


if __name__ == "__main__":
    asyncio.run(advanced_recording_example())
