"""
Learning & Feedback System
Captures manual corrections and continuously improves selector intelligence
"""

import json
import sqlite3
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import os

from ai_selector_engine import get_selector_engine


class LearningFeedbackSystem:
    """
    Manages user feedback and continuous learning
    Stores corrections and improves selector generation over time
    """
    
    def __init__(self, db_path: str = "learning_feedback.db"):
        self.db_path = db_path
        self.selector_engine = get_selector_engine()
        self.feedback_cache = []
        self.pattern_library = defaultdict(list)
        self._init_database()
        self._load_patterns()
    
    def _init_database(self):
        """Initialize SQLite database for feedback storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                incorrect_selector TEXT NOT NULL,
                correct_selector TEXT NOT NULL,
                element_type TEXT,
                element_text TEXT,
                page_url TEXT,
                page_context TEXT,
                framework TEXT,
                correction_reason TEXT,
                user_id TEXT,
                session_id TEXT
            )
        """)
        
        # Pattern library table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                element_type TEXT NOT NULL,
                selector_strategy TEXT NOT NULL,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                confidence_score REAL DEFAULT 0.5,
                last_used TEXT,
                metadata TEXT
            )
        """)
        
        # Selector performance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS selector_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                selector TEXT NOT NULL,
                element_type TEXT,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                avg_execution_time_ms REAL DEFAULT 0,
                last_success TEXT,
                last_failure TEXT,
                UNIQUE(selector, element_type)
            )
        """)
        
        # Learning sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                feedback_count INTEGER DEFAULT 0,
                improvements_applied INTEGER DEFAULT 0,
                notes TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Learning database initialized")
    
    def record_feedback(
        self,
        incorrect_selector: str,
        correct_selector: str,
        element_data: Dict,
        page_context: Optional[Dict] = None,
        reason: Optional[str] = None
    ) -> Dict:
        """
        Record user correction/feedback
        
        Args:
            incorrect_selector: The selector that didn't work
            correct_selector: The corrected selector
            element_data: Element information
            page_context: Optional page context
            reason: Optional reason for correction
            
        Returns:
            Feedback record with learning insights
        """
        timestamp = datetime.now().isoformat()
        
        # Extract element details
        element_type = element_data.get('tagName', 'unknown')
        element_text = self.selector_engine._extract_element_text(element_data)
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO feedback (
                timestamp, incorrect_selector, correct_selector,
                element_type, element_text, page_url, page_context,
                framework, correction_reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp,
            incorrect_selector,
            correct_selector,
            element_type,
            element_text,
            page_context.get('url', '') if page_context else '',
            json.dumps(page_context) if page_context else '{}',
            page_context.get('framework', 'unknown') if page_context else 'unknown',
            reason or 'user_correction'
        ))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Analyze correction and update patterns
        learning_insights = self._analyze_correction(
            incorrect_selector,
            correct_selector,
            element_data
        )
        
        # Update selector engine preferences
        self._update_selector_preferences(
            element_type,
            correct_selector,
            learning_insights
        )
        
        print(f"✅ Feedback recorded (ID: {feedback_id})")
        print(f"   Learned: {learning_insights['key_insight']}")
        
        return {
            'feedback_id': feedback_id,
            'timestamp': timestamp,
            'learning_insights': learning_insights,
            'patterns_updated': learning_insights.get('patterns_updated', 0)
        }
    
    def _analyze_correction(
        self,
        incorrect: str,
        correct: str,
        element_data: Dict
    ) -> Dict:
        """
        Analyze what was wrong and what was corrected
        Extract learning insights
        """
        insights = {
            'key_insight': '',
            'strategy_change': '',
            'patterns_updated': 0
        }
        
        # Detect strategy change
        if '#' in correct and '#' not in incorrect:
            insights['strategy_change'] = 'prefer_id_selectors'
            insights['key_insight'] = 'ID selectors are more reliable for this element type'
        
        elif 'data-' in correct and 'data-' not in incorrect:
            insights['strategy_change'] = 'prefer_data_attributes'
            insights['key_insight'] = 'Data attributes are more stable than classes'
        
        elif 'aria-' in correct and 'aria-' not in incorrect:
            insights['strategy_change'] = 'prefer_aria_attributes'
            insights['key_insight'] = 'ARIA attributes provide better accessibility'
        
        elif 'text=' in correct and 'text=' not in incorrect:
            insights['strategy_change'] = 'prefer_text_selectors'
            insights['key_insight'] = 'Text-based selectors work better for this element'
        
        elif 'lightning-' in correct:
            insights['strategy_change'] = 'prefer_lightning_components'
            insights['key_insight'] = 'Lightning component selectors are more specific'
        
        else:
            insights['strategy_change'] = 'general_improvement'
            insights['key_insight'] = 'Selector specificity improved'
        
        return insights
    
    def _update_selector_preferences(
        self,
        element_type: str,
        preferred_selector: str,
        insights: Dict
    ):
        """
        Update selector generation preferences based on feedback
        """
        strategy = insights.get('strategy_change', '')
        
        if not strategy:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if pattern exists
        cursor.execute("""
            SELECT id, success_count FROM patterns
            WHERE pattern_type = ? AND element_type = ?
        """, (strategy, element_type))
        
        result = cursor.fetchone()
        
        if result:
            # Update existing pattern
            cursor.execute("""
                UPDATE patterns
                SET success_count = success_count + 1,
                    confidence_score = MIN(confidence_score + 0.05, 1.0),
                    last_used = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), result[0]))
        else:
            # Create new pattern
            cursor.execute("""
                INSERT INTO patterns (
                    pattern_type, element_type, selector_strategy,
                    success_count, confidence_score, last_used, metadata
                ) VALUES (?, ?, ?, 1, 0.6, ?, ?)
            """, (
                strategy,
                element_type,
                preferred_selector,
                datetime.now().isoformat(),
                json.dumps(insights)
            ))
        
        conn.commit()
        conn.close()
    
    def get_preferred_strategy(
        self,
        element_type: str
    ) -> Optional[Dict]:
        """
        Get the preferred selector strategy for an element type
        based on learned feedback
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT pattern_type, selector_strategy, confidence_score, success_count
            FROM patterns
            WHERE element_type = ?
            ORDER BY confidence_score DESC, success_count DESC
            LIMIT 1
        """, (element_type,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'pattern_type': result[0],
                'selector_strategy': result[1],
                'confidence': result[2],
                'success_count': result[3]
            }
        
        return None
    
    def record_selector_execution(
        self,
        selector: str,
        element_type: str,
        success: bool,
        execution_time_ms: float = 0
    ):
        """
        Record selector execution result for performance tracking
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        # Check if record exists
        cursor.execute("""
            SELECT id, success_count, failure_count, avg_execution_time_ms
            FROM selector_performance
            WHERE selector = ? AND element_type = ?
        """, (selector, element_type))
        
        result = cursor.fetchone()
        
        if result:
            # Update existing record
            record_id, success_count, failure_count, avg_time = result
            
            if success:
                new_success = success_count + 1
                new_failure = failure_count
                # Update average execution time
                new_avg_time = (avg_time * success_count + execution_time_ms) / new_success
                
                cursor.execute("""
                    UPDATE selector_performance
                    SET success_count = ?,
                        avg_execution_time_ms = ?,
                        last_success = ?
                    WHERE id = ?
                """, (new_success, new_avg_time, timestamp, record_id))
            else:
                cursor.execute("""
                    UPDATE selector_performance
                    SET failure_count = failure_count + 1,
                        last_failure = ?
                    WHERE id = ?
                """, (timestamp, record_id))
        else:
            # Create new record
            cursor.execute("""
                INSERT INTO selector_performance (
                    selector, element_type, success_count, failure_count,
                    avg_execution_time_ms, last_success, last_failure
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                selector,
                element_type,
                1 if success else 0,
                0 if success else 1,
                execution_time_ms if success else 0,
                timestamp if success else None,
                None if success else timestamp
            ))
        
        conn.commit()
        conn.close()
        
        # Also update selector engine
        self.selector_engine.record_selector_result(selector, success, execution_time_ms)
    
    def get_learning_statistics(self) -> Dict:
        """Get comprehensive learning statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total feedback count
        cursor.execute("SELECT COUNT(*) FROM feedback")
        total_feedback = cursor.fetchone()[0]
        
        # Feedback by element type
        cursor.execute("""
            SELECT element_type, COUNT(*) as count
            FROM feedback
            GROUP BY element_type
            ORDER BY count DESC
            LIMIT 10
        """)
        feedback_by_type = dict(cursor.fetchall())
        
        # Most common corrections
        cursor.execute("""
            SELECT correction_reason, COUNT(*) as count
            FROM feedback
            GROUP BY correction_reason
            ORDER BY count DESC
            LIMIT 5
        """)
        common_corrections = dict(cursor.fetchall())
        
        # Pattern library stats
        cursor.execute("""
            SELECT COUNT(*), AVG(confidence_score), SUM(success_count)
            FROM patterns
        """)
        pattern_stats = cursor.fetchone()
        
        # Recent feedback (last 7 days)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute("""
            SELECT COUNT(*) FROM feedback
            WHERE timestamp > ?
        """, (week_ago,))
        recent_feedback = cursor.fetchone()[0]
        
        # Selector performance summary
        cursor.execute("""
            SELECT 
                COUNT(*) as total_selectors,
                SUM(success_count) as total_successes,
                SUM(failure_count) as total_failures,
                AVG(avg_execution_time_ms) as avg_time
            FROM selector_performance
        """)
        perf_stats = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_feedback_records': total_feedback,
            'feedback_by_element_type': feedback_by_type,
            'common_correction_reasons': common_corrections,
            'pattern_library': {
                'total_patterns': pattern_stats[0] or 0,
                'average_confidence': round(pattern_stats[1] or 0, 3),
                'total_successes': pattern_stats[2] or 0
            },
            'recent_activity': {
                'feedback_last_7_days': recent_feedback
            },
            'selector_performance': {
                'total_selectors_tracked': perf_stats[0] or 0,
                'total_successes': perf_stats[1] or 0,
                'total_failures': perf_stats[2] or 0,
                'average_execution_time_ms': round(perf_stats[3] or 0, 2)
            }
        }
    
    def get_improvement_suggestions(self) -> List[Dict]:
        """
        Analyze feedback and suggest improvements to test suite
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        suggestions = []
        
        # Find frequently corrected selectors
        cursor.execute("""
            SELECT incorrect_selector, COUNT(*) as correction_count,
                   element_type, element_text
            FROM feedback
            GROUP BY incorrect_selector
            HAVING correction_count > 2
            ORDER BY correction_count DESC
            LIMIT 10
        """)
        
        for row in cursor.fetchall():
            selector, count, elem_type, elem_text = row
            
            # Get the most recent correction
            cursor.execute("""
                SELECT correct_selector, correction_reason
                FROM feedback
                WHERE incorrect_selector = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (selector,))
            
            correction = cursor.fetchone()
            
            suggestions.append({
                'type': 'frequently_corrected',
                'priority': 'high',
                'selector': selector,
                'correction_count': count,
                'suggested_replacement': correction[0] if correction else None,
                'reason': correction[1] if correction else 'Multiple corrections needed',
                'element_type': elem_type,
                'element_text': elem_text
            })
        
        # Find low-performing selectors
        cursor.execute("""
            SELECT selector, element_type, success_count, failure_count
            FROM selector_performance
            WHERE failure_count > success_count
                AND (success_count + failure_count) > 5
            ORDER BY failure_count DESC
            LIMIT 10
        """)
        
        for row in cursor.fetchall():
            selector, elem_type, success, failure = row
            
            suggestions.append({
                'type': 'low_performance',
                'priority': 'medium',
                'selector': selector,
                'success_rate': round(success / (success + failure) * 100, 1),
                'total_attempts': success + failure,
                'reason': 'High failure rate detected',
                'element_type': elem_type
            })
        
        conn.close()
        
        return suggestions
    
    def export_learning_report(self, filepath: str):
        """Export comprehensive learning report"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'statistics': self.get_learning_statistics(),
            'improvement_suggestions': self.get_improvement_suggestions(),
            'top_patterns': self._get_top_patterns()
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Learning report exported to {filepath}")
    
    def _get_top_patterns(self, limit: int = 20) -> List[Dict]:
        """Get top performing patterns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT pattern_type, element_type, selector_strategy,
                   success_count, confidence_score, last_used
            FROM patterns
            ORDER BY confidence_score DESC, success_count DESC
            LIMIT ?
        """, (limit,))
        
        patterns = []
        for row in cursor.fetchall():
            patterns.append({
                'pattern_type': row[0],
                'element_type': row[1],
                'selector_strategy': row[2],
                'success_count': row[3],
                'confidence_score': row[4],
                'last_used': row[5]
            })
        
        conn.close()
        return patterns
    
    def _load_patterns(self):
        """Load patterns into memory for quick access"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT pattern_type, element_type, selector_strategy, confidence_score
            FROM patterns
            WHERE confidence_score > 0.7
        """)
        
        for row in cursor.fetchall():
            pattern_type, element_type, strategy, confidence = row
            self.pattern_library[element_type].append({
                'pattern_type': pattern_type,
                'strategy': strategy,
                'confidence': confidence
            })
        
        conn.close()


# Singleton instance
_learning_system = None

def get_learning_system() -> LearningFeedbackSystem:
    """Get or create LearningFeedbackSystem instance"""
    global _learning_system
    if _learning_system is None:
        _learning_system = LearningFeedbackSystem()
    return _learning_system
