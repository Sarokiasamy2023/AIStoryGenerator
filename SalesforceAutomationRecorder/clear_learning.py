"""
Clear learned selectors database
"""

from pathlib import Path
import json

learning_db = Path("test_learning.json")

if learning_db.exists():
    # Backup first
    backup = Path("test_learning_backup.json")
    with open(learning_db, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with open(backup, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Backed up to: {backup}")
    
    # Clear
    learning_db.unlink()
    print(f"✅ Cleared: {learning_db}")
    print("\n🎯 Ready for fresh learning!")
else:
    print("ℹ️  No learning database found. Nothing to clear.")
