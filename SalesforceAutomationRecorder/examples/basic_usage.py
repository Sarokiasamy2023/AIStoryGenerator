"""
Basic Usage Example - Salesforce Automation Recorder

This example demonstrates how to use the recorder for a simple recording session.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automation_recorder import SalesforceRecorder


async def basic_recording_example():
    """
    Basic example: Record interactions on a Salesforce page
    """
    print("=" * 60)
    print("Salesforce Automation Recorder - Basic Usage Example")
    print("=" * 60)
    
    # Initialize recorder
    recorder = SalesforceRecorder()
    
    # Your Salesforce URL
    salesforce_url = "https://login.salesforce.com"
    
    print(f"\n1. Starting recording session for: {salesforce_url}")
    print("2. Browser will open automatically")
    print("3. Interact with the page (clicks, inputs, etc.)")
    print("4. Click 'Stop Capture' button in the UI overlay when done")
    print("5. Recording will be automatically saved\n")
    
    try:
        # Start recording - this will open browser and wait for user interactions
        await recorder.start_recording(salesforce_url)
        
        # Get captured data
        captured_data = recorder.get_captured_data()
        
        print(f"\n✓ Recording completed!")
        print(f"✓ Captured {len(captured_data)} interactions")
        
        # Print summary
        if captured_data:
            print("\nSummary:")
            frameworks = {}
            for interaction in captured_data:
                fw = interaction.get('framework', 'Unknown')
                frameworks[fw] = frameworks.get(fw, 0) + 1
            
            for framework, count in frameworks.items():
                print(f"  - {framework}: {count} interactions")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Recording interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Always close the browser
        await recorder.close()
        print("\n✓ Browser closed")


if __name__ == "__main__":
    asyncio.run(basic_recording_example())
