"""
View Gemini AI Usage Logs
Shows when Gemini AI was used vs traditional selectors
"""

import json
from pathlib import Path
from datetime import datetime

def view_gemini_logs():
    """View Gemini AI usage from test learning data"""
    
    print("=" * 70)
    print("  GEMINI AI USAGE LOGS")
    print("=" * 70)
    print()
    
    # Check if Gemini config exists
    gemini_config = Path("gemini_config.json")
    if gemini_config.exists():
        with open(gemini_config, 'r') as f:
            config = json.load(f)
            print(f"📋 Gemini Status: {'✅ Enabled' if config.get('enabled') else '❌ Disabled'}")
            print(f"🔑 API Key Set: {'✅ Yes' if config.get('api_key') else '❌ No'}")
            print()
    
    # Load test learning data
    learning_file = Path("test_learning.json")
    if not learning_file.exists():
        print("❌ No test learning data found")
        return
    
    with open(learning_file, 'r') as f:
        learning_data = json.load(f)
    
    print(f"📊 Total Learned Selectors: {len(learning_data)}")
    print()
    
    # Analyze usage patterns
    print("-" * 70)
    print("  SELECTOR USAGE ANALYSIS")
    print("-" * 70)
    print()
    
    # Sort by last used (most recent first)
    sorted_selectors = sorted(
        learning_data.items(),
        key=lambda x: x[1].get('last_used', ''),
        reverse=True
    )
    
    print(f"{'Target':<40} {'Action':<10} {'Uses':<8} {'Last Used'}")
    print("-" * 70)
    
    for target, data in sorted_selectors[:20]:  # Show top 20
        action = data.get('action', 'unknown')
        uses = data.get('success_count', 0)
        last_used = data.get('last_used', 'N/A')
        
        # Parse datetime
        if last_used != 'N/A':
            try:
                dt = datetime.fromisoformat(last_used)
                last_used = dt.strftime('%Y-%m-%d %H:%M')
            except:
                pass
        
        # Truncate long target names
        display_target = target[:38] + '..' if len(target) > 40 else target
        
        print(f"{display_target:<40} {action:<10} {uses:<8} {last_used}")
    
    print()
    print("-" * 70)
    print("  GEMINI AI SPECIFIC LOGS")
    print("-" * 70)
    print()
    
    # Note about Gemini logs
    print("ℹ️  Gemini AI logs are stored in memory during test execution.")
    print("   To see real-time Gemini AI usage:")
    print()
    print("   1. Start server: .\\kill_and_start.bat")
    print("   2. Open dashboard: http://localhost:8888")
    print("   3. Click purple button: 🤖 Run with Gemini AI")
    print("   4. Watch server console for:")
    print("      - '🤖 Using Gemini AI Enhanced Executor'")
    print("      - '[AI] Consulting Gemini for element...'")
    print("      - '[AI] Gemini suggested selector...'")
    print()
    print("   5. After test, check dashboard metrics:")
    print("      - 🤖 Gemini AI Usage: X%")
    print("      - 💡 AI Suggestions Used: X/Y")
    print()
    
    # Check for recent Gemini usage
    recent_cutoff = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    recent_selectors = [
        (target, data) for target, data in learning_data.items()
        if datetime.fromisoformat(data.get('last_used', '2000-01-01')) >= recent_cutoff
    ]
    
    if recent_selectors:
        print(f"📅 Selectors used today: {len(recent_selectors)}")
        print()
        for target, data in recent_selectors[:10]:
            print(f"   ✓ {target} ({data.get('action')})")
    else:
        print("📅 No selectors used today")
    
    print()
    print("=" * 70)
    print()
    
    # Summary
    total_uses = sum(data.get('success_count', 0) for data in learning_data.values())
    print(f"📈 Summary:")
    print(f"   - Total selectors learned: {len(learning_data)}")
    print(f"   - Total successful uses: {total_uses}")
    print(f"   - Average uses per selector: {total_uses / len(learning_data):.1f}")
    print()
    
    # Most used selectors
    most_used = sorted(
        learning_data.items(),
        key=lambda x: x[1].get('success_count', 0),
        reverse=True
    )[:5]
    
    print("🏆 Most Used Selectors:")
    for i, (target, data) in enumerate(most_used, 1):
        uses = data.get('success_count', 0)
        print(f"   {i}. {target}: {uses} uses")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    view_gemini_logs()
