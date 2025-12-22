"""
Auto-Healing System - Learns from failures and adapts selectors
Tracks selector success/failure patterns and automatically fixes broken tests
"""

import json
import os
from datetime import datetime
from pathlib import Path
from collections import defaultdict

class AutoHealer:
    def __init__(self, storage_path="auto_heal_data.json"):
        """Initialize Auto-Healing system"""
        self.storage_path = storage_path
        self.selector_history = defaultdict(lambda: {
            'successes': 0,
            'failures': 0,
            'last_success': None,
            'last_failure': None,
            'working_alternatives': [],
            'failed_selectors': []
        })
        self.healing_suggestions = []
        self.load_history()
    
    def load_history(self):
        """Load selector history from disk"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.selector_history = defaultdict(lambda: {
                        'successes': 0,
                        'failures': 0,
                        'last_success': None,
                        'last_failure': None,
                        'working_alternatives': [],
                        'failed_selectors': []
                    }, data)
            except Exception as e:
                print(f"⚠️ Could not load auto-heal history: {e}")
    
    def save_history(self):
        """Save selector history to disk"""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(dict(self.selector_history), f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save auto-heal history: {e}")
    
    def record_success(self, element_key, selector, action):
        """Record successful selector usage"""
        key = f"{action}:{element_key}"
        self.selector_history[key]['successes'] += 1
        self.selector_history[key]['last_success'] = datetime.now().isoformat()
        
        # Add to working alternatives if not already there
        if selector not in self.selector_history[key]['working_alternatives']:
            self.selector_history[key]['working_alternatives'].insert(0, selector)
            # Keep only top 5 working alternatives
            self.selector_history[key]['working_alternatives'] = \
                self.selector_history[key]['working_alternatives'][:5]
        
        self.save_history()
    
    def record_failure(self, element_key, selector, action, error_msg=""):
        """Record failed selector usage"""
        key = f"{action}:{element_key}"
        self.selector_history[key]['failures'] += 1
        self.selector_history[key]['last_failure'] = datetime.now().isoformat()
        
        # Track failed selector
        if selector not in self.selector_history[key]['failed_selectors']:
            self.selector_history[key]['failed_selectors'].append(selector)
        
        self.save_history()
    
    def get_healing_selector(self, element_key, action, failed_selector):
        """Get a healing selector suggestion based on history"""
        key = f"{action}:{element_key}"
        history = self.selector_history[key]
        
        # Return working alternatives that aren't the failed one
        alternatives = [s for s in history['working_alternatives'] 
                       if s != failed_selector]
        
        if alternatives:
            return alternatives[0]  # Return best working alternative
        
        return None
    
    def get_health_score(self, element_key, action):
        """Calculate health score for an element (0-100)"""
        key = f"{action}:{element_key}"
        history = self.selector_history[key]
        
        total = history['successes'] + history['failures']
        if total == 0:
            return 100  # New element, assume healthy
        
        score = (history['successes'] / total) * 100
        return round(score, 1)
    
    def analyze_test_health(self, test_steps):
        """Analyze overall test health and provide suggestions"""
        issues = []
        suggestions = []
        
        for step in test_steps:
            action = step.get('action')
            selector = step.get('selector', '')
            
            # Try to extract element key
            element_key = self._extract_element_key(selector)
            if not element_key:
                continue
            
            health_score = self.get_health_score(element_key, action)
            
            if health_score < 80:
                issues.append({
                    'step': step,
                    'health_score': health_score,
                    'element': element_key,
                    'action': action
                })
                
                # Get healing suggestion
                healing_selector = self.get_healing_selector(element_key, action, selector)
                if healing_selector:
                    suggestions.append({
                        'element': element_key,
                        'action': action,
                        'current_selector': selector,
                        'suggested_selector': healing_selector,
                        'reason': f'Health score: {health_score}%'
                    })
        
        return {
            'issues': issues,
            'suggestions': suggestions,
            'overall_health': self._calculate_overall_health(test_steps)
        }
    
    def _extract_element_key(self, selector):
        """Extract a meaningful key from selector"""
        import re
        
        # Try to extract text from has-text or text= selectors
        if 'text=' in selector:
            return selector.replace('text=', '').strip('"\'')
        
        match = re.search(r':has-text\(["\'](.+?)["\']\)', selector)
        if match:
            return match.group(1)
        
        match = re.search(r'placeholder="([^"]+)"', selector)
        if match:
            return match.group(1)
        
        match = re.search(r'label:has-text\(["\'](.+?)["\']\)', selector)
        if match:
            return match.group(1)
        
        # Return first 50 chars of selector as fallback
        return selector[:50]
    
    def _calculate_overall_health(self, test_steps):
        """Calculate overall test health score"""
        if not test_steps:
            return 100
        
        total_score = 0
        count = 0
        
        for step in test_steps:
            action = step.get('action')
            selector = step.get('selector', '')
            element_key = self._extract_element_key(selector)
            
            if element_key:
                score = self.get_health_score(element_key, action)
                total_score += score
                count += 1
        
        if count == 0:
            return 100
        
        return round(total_score / count, 1)
    
    def get_statistics(self):
        """Get auto-healing statistics"""
        total_elements = len(self.selector_history)
        total_successes = sum(h['successes'] for h in self.selector_history.values())
        total_failures = sum(h['failures'] for h in self.selector_history.values())
        
        healed_elements = sum(1 for h in self.selector_history.values() 
                             if len(h['working_alternatives']) > 1)
        
        return {
            'total_elements': total_elements,
            'total_successes': total_successes,
            'total_failures': total_failures,
            'healed_elements': healed_elements,
            'success_rate': round((total_successes / (total_successes + total_failures) * 100), 1) 
                           if (total_successes + total_failures) > 0 else 0
        }


# Singleton instance
_auto_healer = None

def get_auto_healer():
    """Get or create AutoHealer instance"""
    global _auto_healer
    if _auto_healer is None:
        _auto_healer = AutoHealer()
    return _auto_healer
