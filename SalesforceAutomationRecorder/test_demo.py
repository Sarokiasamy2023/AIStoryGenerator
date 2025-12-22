"""
Demo Script - Test the Salesforce Automation Recorder

This script demonstrates the recorder functionality without needing
an actual Salesforce instance. It opens a test HTML page and captures interactions.
"""

import asyncio
import os
from pathlib import Path
from automation_recorder import SalesforceRecorder


async def create_demo_page():
    """Create a demo HTML page for testing"""
    
    demo_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Salesforce Demo Page</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Salesforce Sans', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 600px;
            width: 100%;
        }
        h1 {
            color: #032d60;
            margin-bottom: 10px;
            font-size: 28px;
        }
        .subtitle {
            color: #706e6b;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .slds-form-element {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #3e3e3c;
            font-weight: 600;
            font-size: 14px;
        }
        input, select {
            width: 100%;
            padding: 12px;
            border: 1px solid #c9c7c5;
            border-radius: 4px;
            font-size: 14px;
            transition: all 0.2s;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #1589ee;
            box-shadow: 0 0 3px #1589ee;
        }
        .slds-button {
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            margin-right: 10px;
        }
        .slds-button_brand {
            background: #0176d3;
            color: white;
        }
        .slds-button_brand:hover {
            background: #014486;
        }
        .slds-button_neutral {
            background: #f3f2f2;
            color: #0176d3;
            border: 1px solid #c9c7c5;
        }
        .slds-button_neutral:hover {
            background: #e5e5e5;
        }
        .lightning-section {
            background: #f3f3f3;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .omniscript-section {
            background: #fff5e6;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #ff6b35;
        }
        .section-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 15px;
            color: #032d60;
        }
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            margin-left: 10px;
        }
        .badge-lightning {
            background: #e6f7ff;
            color: #00a1e0;
        }
        .badge-omniscript {
            background: #ffe6e0;
            color: #ff6b35;
        }
        .success-message {
            background: #4bca81;
            color: white;
            padding: 15px;
            border-radius: 4px;
            margin-top: 20px;
            display: none;
        }
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Salesforce Recorder Demo</h1>
        <p class="subtitle">Interact with this page to test the recorder</p>

        <!-- Standard Login Section -->
        <div class="slds-form-element">
            <label for="username">Username</label>
            <input type="text" id="username" name="username" placeholder="Enter username">
        </div>

        <div class="slds-form-element">
            <label for="password">Password</label>
            <input type="password" id="password" name="password" placeholder="Enter password">
        </div>

        <button class="slds-button slds-button_brand" id="login-btn">Log In</button>

        <!-- Lightning Section -->
        <div class="lightning-section" data-aura-rendered-by="lightningSection">
            <div class="section-title">
                Lightning Components
                <span class="badge badge-lightning">Lightning</span>
            </div>

            <div class="slds-form-element">
                <label for="firstName">First Name</label>
                <input type="text" 
                       id="firstName" 
                       name="firstName" 
                       class="slds-input"
                       data-lightning-field="firstName"
                       placeholder="Enter first name">
            </div>

            <div class="slds-form-element">
                <label for="lastName">Last Name</label>
                <input type="text" 
                       id="lastName" 
                       name="lastName" 
                       class="slds-input"
                       data-lightning-field="lastName"
                       placeholder="Enter last name"
                       required>
            </div>

            <div class="slds-form-element">
                <label for="email">Email</label>
                <input type="email" 
                       id="email" 
                       name="email" 
                       class="slds-input"
                       data-lightning-field="email"
                       placeholder="Enter email">
            </div>

            <div class="button-group">
                <button class="slds-button slds-button_brand" 
                        data-aura-class="forceActionButton">
                    Save Contact
                </button>
                <button class="slds-button slds-button_neutral" 
                        data-aura-class="forceActionButton">
                    Cancel
                </button>
            </div>
        </div>

        <!-- OmniScript Section -->
        <div class="omniscript-section" data-omnistudio-section="customerInfo">
            <div class="section-title">
                OmniScript Components
                <span class="badge badge-omniscript">OmniScript</span>
            </div>

            <div class="slds-form-element">
                <label for="customerName">Customer Name</label>
                <input type="text" 
                       id="customerName" 
                       class="nds-input"
                       data-omnistudio-field="CustomerName"
                       placeholder="Enter customer name"
                       required>
            </div>

            <div class="slds-form-element">
                <label for="customerType">Customer Type</label>
                <select id="customerType" 
                        class="nds-select"
                        data-omnistudio-field="CustomerType">
                    <option value="">Select type...</option>
                    <option value="individual">Individual</option>
                    <option value="business">Business</option>
                    <option value="enterprise">Enterprise</option>
                </select>
            </div>

            <div class="slds-form-element">
                <label for="accountNumber">Account Number</label>
                <input type="text" 
                       id="accountNumber" 
                       class="nds-input vlocity_input"
                       data-omnistudio-field="AccountNumber"
                       placeholder="Enter account number">
            </div>

            <div class="button-group">
                <button class="slds-button slds-button_brand omnistudio-button-next" 
                        data-omni-action="next">
                    Next Step
                </button>
                <button class="slds-button slds-button_neutral omnistudio-button-previous" 
                        data-omni-action="previous">
                    Previous
                </button>
            </div>
        </div>

        <div class="success-message" id="successMessage">
            ✓ Form submitted successfully! Check the recorder output.
        </div>
    </div>

    <script>
        // Add some interactivity
        document.getElementById('login-btn').addEventListener('click', function() {
            console.log('Login button clicked');
            document.getElementById('successMessage').style.display = 'block';
            setTimeout(() => {
                document.getElementById('successMessage').style.display = 'none';
            }, 3000);
        });

        document.querySelectorAll('.slds-button_brand').forEach(btn => {
            btn.addEventListener('click', function() {
                console.log('Button clicked:', this.textContent);
            });
        });

        document.querySelectorAll('input, select').forEach(field => {
            field.addEventListener('change', function() {
                console.log('Field changed:', this.name || this.id, '=', this.value);
            });
        });
    </script>
</body>
</html>
    """
    
    # Create demo directory
    demo_dir = Path(__file__).parent / "demo"
    demo_dir.mkdir(exist_ok=True)
    
    demo_file = demo_dir / "demo_page.html"
    with open(demo_file, 'w', encoding='utf-8') as f:
        f.write(demo_html)
    
    return demo_file.absolute()


async def run_demo():
    """Run the demo recording session"""
    
    print("=" * 70)
    print("SALESFORCE AUTOMATION RECORDER - DEMO")
    print("=" * 70)
    print()
    
    # Create demo page
    print("📄 Creating demo page...")
    demo_page = await create_demo_page()
    demo_url = f"file:///{demo_page}".replace("\\", "/")
    print(f"✓ Demo page created: {demo_page}")
    print()
    
    # Initialize recorder
    print("🎬 Initializing recorder...")
    recorder = SalesforceRecorder()
    print("✓ Recorder initialized")
    print()
    
    print("=" * 70)
    print("INSTRUCTIONS")
    print("=" * 70)
    print("1. A browser window will open with a demo Salesforce-like page")
    print("2. You'll see a control panel in the top-right corner")
    print("3. Interact with the page:")
    print("   - Fill in the username and password fields")
    print("   - Click the 'Log In' button")
    print("   - Fill in Lightning component fields (First Name, Last Name, Email)")
    print("   - Click 'Save Contact'")
    print("   - Fill in OmniScript fields (Customer Name, Type, Account Number)")
    print("   - Click 'Next Step'")
    print("4. Click 'Stop Capture' button when done")
    print("5. Recording will be automatically saved")
    print()
    print("Press Enter to start the demo...")
    input()
    
    try:
        # Start recording
        print("\n🎥 Starting recording session...")
        print(f"📍 URL: {demo_url}")
        print()
        
        await recorder.start_recording(demo_url)
        
        # Get results
        captured_data = recorder.get_captured_data()
        
        print("\n" + "=" * 70)
        print("RECORDING COMPLETE")
        print("=" * 70)
        print(f"✓ Captured {len(captured_data)} interactions")
        print()
        
        if captured_data:
            # Analyze results
            frameworks = {}
            actions = {}
            
            for interaction in captured_data:
                fw = interaction.get('framework', 'Unknown')
                action = interaction.get('action', 'unknown')
                
                frameworks[fw] = frameworks.get(fw, 0) + 1
                actions[action] = actions.get(action, 0) + 1
            
            print("📊 Framework Distribution:")
            for framework, count in frameworks.items():
                print(f"   - {framework}: {count} interactions")
            
            print("\n⚡ Action Distribution:")
            for action, count in actions.items():
                print(f"   - {action}: {count} interactions")
            
            print("\n📝 Sample Interactions:")
            for i, interaction in enumerate(captured_data[:5], 1):
                print(f"\n   {i}. {interaction['action'].upper()}: {interaction['label']}")
                print(f"      Framework: {interaction['framework']}")
                print(f"      Selector: {interaction['selector']}")
            
            if len(captured_data) > 5:
                print(f"\n   ... and {len(captured_data) - 5} more interactions")
            
            # Show output file location
            output_dir = Path(__file__).parent / "recordings"
            print(f"\n💾 Recording saved to: {output_dir}")
            print()
        
        print("=" * 70)
        print("NEXT STEPS")
        print("=" * 70)
        print("1. Check the 'recordings' directory for the JSON output")
        print("2. Try generating automation script:")
        print(f"   python ai_automation_generator.py --recording recordings/[filename].json --output test.py")
        print("3. View the examples directory for more usage patterns")
        print("4. Read IMPLEMENTATION_GUIDE.md for technical details")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠ Demo interrupted by user")
    except Exception as e:
        print(f"\n✗ Error during demo: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await recorder.close()
        print("\n✓ Browser closed")
        print("\nThank you for trying the Salesforce Automation Recorder! 🎯")


if __name__ == "__main__":
    asyncio.run(run_demo())
