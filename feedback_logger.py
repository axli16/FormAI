"""
Feedback Logger - Stores all AI feedback for review
This module provides functionality to:
1. Log all AI-generated feedback with timestamps
2. Store feedback in structured JSON format
3. Provide utilities to query and review feedback history
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import threading

class FeedbackLogger:
    """Thread-safe logger for AI feedback"""
    
    def __init__(self, log_dir: str = "feedback_logs"):
        """
        Initialize the feedback logger
        
        Args:
            log_dir: Directory to store feedback logs (default: feedback_logs)
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create separate log files for different purposes
        self.main_log = self.log_dir / "feedback_history.jsonl"  # JSONL format for easy appending
        self.summary_log = self.log_dir / "feedback_summary.json"
        
        # Thread lock for safe concurrent writes
        self.lock = threading.Lock()
        
        # Statistics
        self.stats = self._load_stats()
        
        print(f"✅ Feedback logger initialized. Logs stored in: {self.log_dir.absolute()}")
    
    def log_feedback(self, feedback: Dict, metadata: Optional[Dict] = None):
        """
        Log a single feedback entry
        
        Args:
            feedback: The feedback dict containing skill, grade, tips
            metadata: Optional additional metadata (user_id, session_id, etc.)
        """
        with self.lock:
            timestamp = datetime.now().isoformat()
            
            # Create log entry
            entry = {
                "timestamp": timestamp,
                "feedback": feedback,
                "metadata": metadata or {}
            }
            
            # Append to JSONL file (one JSON object per line)
            with open(self.main_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
            
            # Update statistics
            self._update_stats(feedback)
            
            print(f"📝 Logged feedback: {feedback.get('skill', 'Unknown')} - Grade: {feedback.get('grade', 'N/A')}")
    
    def _load_stats(self) -> Dict:
        """Load statistics from summary file"""
        if self.summary_log.exists():
            try:
                with open(self.summary_log, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "total_feedback_count": 0,
            "skill_counts": {},
            "average_grades": {},
            "first_logged": None,
            "last_logged": None
        }
    
    def _update_stats(self, feedback: Dict):
        """Update statistics with new feedback"""
        skill = feedback.get('skill', 'Unknown')
        grade_str = feedback.get('grade', '0')
        
        # Parse grade (handle both string and numeric)
        try:
            grade = float(grade_str.replace('%', '').strip())
        except:
            grade = 0
        
        # Update counts
        self.stats['total_feedback_count'] += 1
        self.stats['skill_counts'][skill] = self.stats['skill_counts'].get(skill, 0) + 1
        
        # Update average grades
        if skill not in self.stats['average_grades']:
            self.stats['average_grades'][skill] = {'sum': 0, 'count': 0, 'average': 0}
        
        self.stats['average_grades'][skill]['sum'] += grade
        self.stats['average_grades'][skill]['count'] += 1
        self.stats['average_grades'][skill]['average'] = (
            self.stats['average_grades'][skill]['sum'] / 
            self.stats['average_grades'][skill]['count']
        )
        
        # Update timestamps
        now = datetime.now().isoformat()
        if not self.stats['first_logged']:
            self.stats['first_logged'] = now
        self.stats['last_logged'] = now
        
        # Save stats
        with open(self.summary_log, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2)
    
    def get_recent_feedback(self, count: int = 10) -> List[Dict]:
        """
        Get the most recent feedback entries
        
        Args:
            count: Number of recent entries to retrieve
            
        Returns:
            List of feedback entries
        """
        if not self.main_log.exists():
            return []
        
        entries = []
        with open(self.main_log, 'r', encoding='utf-8') as f:
            # Read all lines and get the last N
            lines = f.readlines()
            for line in lines[-count:]:
                try:
                    entries.append(json.loads(line))
                except:
                    continue
        
        return entries
    
    def get_feedback_by_skill(self, skill: str) -> List[Dict]:
        """
        Get all feedback for a specific skill
        
        Args:
            skill: The skill name to filter by
            
        Returns:
            List of feedback entries for that skill
        """
        if not self.main_log.exists():
            return []
        
        entries = []
        with open(self.main_log, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get('feedback', {}).get('skill', '').lower() == skill.lower():
                        entries.append(entry)
                except:
                    continue
        
        return entries
    
    def get_feedback_by_date(self, date_str: str) -> List[Dict]:
        """
        Get all feedback from a specific date
        
        Args:
            date_str: Date string in YYYY-MM-DD format
            
        Returns:
            List of feedback entries from that date
        """
        if not self.main_log.exists():
            return []
        
        entries = []
        with open(self.main_log, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get('timestamp', '').startswith(date_str):
                        entries.append(entry)
                except:
                    continue
        
        return entries
    
    def get_statistics(self) -> Dict:
        """Get current statistics"""
        return self.stats.copy()
    
    def export_to_csv(self, output_file: str = None):
        """
        Export feedback logs to CSV format
        
        Args:
            output_file: Path to output CSV file (default: feedback_logs/export.csv)
        """
        import csv
        
        if output_file is None:
            output_file = self.log_dir / "export.csv"
        
        if not self.main_log.exists():
            print("No feedback logs to export")
            return
        
        with open(self.main_log, 'r', encoding='utf-8') as f_in:
            with open(output_file, 'w', newline='', encoding='utf-8') as f_out:
                writer = csv.writer(f_out)
                writer.writerow(['Timestamp', 'Skill', 'Grade', 'Tips', 'Source', 'User ID'])
                
                for line in f_in:
                    try:
                        entry = json.loads(line)
                        feedback = entry.get('feedback', {})
                        metadata = entry.get('metadata', {})
                        
                        writer.writerow([
                            entry.get('timestamp', ''),
                            feedback.get('skill', ''),
                            feedback.get('grade', ''),
                            ' | '.join(feedback.get('tips', [])),
                            feedback.get('source', 'unknown'),
                            metadata.get('user_id', '')
                        ])
                    except:
                        continue
        
        print(f"✅ Exported to: {output_file}")
    
    def clear_logs(self, confirm: bool = False):
        """
        Clear all feedback logs (use with caution!)
        
        Args:
            confirm: Must be True to actually clear logs
        """
        if not confirm:
            print("⚠️  Must pass confirm=True to clear logs")
            return
        
        with self.lock:
            if self.main_log.exists():
                self.main_log.unlink()
            if self.summary_log.exists():
                self.summary_log.unlink()
            
            self.stats = {
                "total_feedback_count": 0,
                "skill_counts": {},
                "average_grades": {},
                "first_logged": None,
                "last_logged": None
            }
            
            print("✅ All logs cleared")


# Global logger instance
_logger_instance = None

def get_logger(log_dir: str = "feedback_logs") -> FeedbackLogger:
    """Get or create the global logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = FeedbackLogger(log_dir)
    return _logger_instance


if __name__ == "__main__":
    # Test the logger
    logger = get_logger()
    
    # Log some test feedback
    test_feedback = {
        "skill": "Handstand",
        "grade": "85",
        "tips": ["Straighten your arms", "Keep your core tight"],
        "source": "ai"
    }
    
    logger.log_feedback(test_feedback, metadata={"user_id": "test_user"})
    
    # Display stats
    print("\n" + "="*60)
    print("Statistics:")
    print(json.dumps(logger.get_statistics(), indent=2))
