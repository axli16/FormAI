"""
Feedback Log Viewer - Interactive tool to review AI feedback history
Run this script to view and analyze your feedback logs
"""

import json
from datetime import datetime
from pathlib import Path
from feedback_logger import get_logger
from typing import List, Dict
import sys

class FeedbackViewer:
    """Interactive viewer for feedback logs"""
    
    def __init__(self):
        self.logger = get_logger()
    
    def display_header(self):
        """Display viewer header"""
        print("\n" + "="*80)
        print(" 📊 AI FEEDBACK LOG VIEWER ".center(80, "="))
        print("="*80 + "\n")
    
    def display_statistics(self):
        """Display overall statistics"""
        stats = self.logger.get_statistics()
        
        print("📈 OVERALL STATISTICS")
        print("-" * 80)
        print(f"Total Feedback Entries: {stats['total_feedback_count']}")
        
        if stats['first_logged']:
            first = datetime.fromisoformat(stats['first_logged']).strftime('%Y-%m-%d %H:%M:%S')
            last = datetime.fromisoformat(stats['last_logged']).strftime('%Y-%m-%d %H:%M:%S')
            print(f"First Logged: {first}")
            print(f"Last Logged:  {last}")
        
        print("\n📊 FEEDBACK BY SKILL")
        print("-" * 80)
        for skill, count in stats['skill_counts'].items():
            avg_grade = stats['average_grades'].get(skill, {}).get('average', 0)
            print(f"  {skill:20s} - Count: {count:4d} | Avg Grade: {avg_grade:.1f}%")
        
        print()
    
    def display_recent_feedback(self, count: int = 10):
        """Display recent feedback entries"""
        entries = self.logger.get_recent_feedback(count)
        
        if not entries:
            print("❌ No feedback logs found\n")
            return
        
        print(f"🕐 RECENT FEEDBACK (Last {len(entries)} entries)")
        print("-" * 80)
        
        for i, entry in enumerate(reversed(entries), 1):
            self._display_entry(entry, i)
        
        print()
    
    def display_skill_feedback(self, skill: str):
        """Display all feedback for a specific skill"""
        entries = self.logger.get_feedback_by_skill(skill)
        
        if not entries:
            print(f"❌ No feedback found for skill: {skill}\n")
            return
        
        print(f"🎯 FEEDBACK FOR: {skill.upper()}")
        print("-" * 80)
        print(f"Total entries: {len(entries)}\n")
        
        for i, entry in enumerate(entries, 1):
            self._display_entry(entry, i)
        
        print()
    
    def display_date_feedback(self, date_str: str):
        """Display feedback from a specific date"""
        entries = self.logger.get_feedback_by_date(date_str)
        
        if not entries:
            print(f"❌ No feedback found for date: {date_str}\n")
            return
        
        print(f"📅 FEEDBACK FROM: {date_str}")
        print("-" * 80)
        print(f"Total entries: {len(entries)}\n")
        
        for i, entry in enumerate(entries, 1):
            self._display_entry(entry, i)
        
        print()
    
    def _display_entry(self, entry: Dict, index: int = None):
        """Display a single feedback entry"""
        timestamp = entry.get('timestamp', '')
        feedback = entry.get('feedback', {})
        metadata = entry.get('metadata', {})
        
        # Format timestamp
        try:
            dt = datetime.fromisoformat(timestamp)
            time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            time_str = timestamp
        
        # Display entry
        if index:
            print(f"[{index}] ", end="")
        
        print(f"⏰ {time_str}")
        print(f"    Skill:  {feedback.get('skill', 'Unknown')}")
        print(f"    Grade:  {feedback.get('grade', 'N/A')}")
        print(f"    Source: {feedback.get('source', 'unknown')}")
        
        tips = feedback.get('tips', [])
        if tips:
            print(f"    Tips:")
            for tip in tips:
                print(f"      • {tip}")
        
        if metadata:
            print(f"    Metadata: {metadata}")
        
        print()
    
    def search_by_grade_range(self, min_grade: float, max_grade: float):
        """Search for feedback within a grade range"""
        log_file = self.logger.main_log
        
        if not log_file.exists():
            print("❌ No feedback logs found\n")
            return
        
        entries = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    feedback = entry.get('feedback', {})
                    grade_str = feedback.get('grade', '0')
                    
                    # Parse grade
                    try:
                        grade = float(grade_str.replace('%', '').strip())
                        if min_grade <= grade <= max_grade:
                            entries.append(entry)
                    except:
                        continue
                except:
                    continue
        
        if not entries:
            print(f"❌ No feedback found with grade between {min_grade} and {max_grade}\n")
            return
        
        print(f"🔍 FEEDBACK WITH GRADE {min_grade}-{max_grade}")
        print("-" * 80)
        print(f"Total entries: {len(entries)}\n")
        
        for i, entry in enumerate(entries, 1):
            self._display_entry(entry, i)
        
        print()
    
    def export_logs(self):
        """Export logs to CSV"""
        self.logger.export_to_csv()
    
    def interactive_menu(self):
        """Display interactive menu"""
        while True:
            print("\n" + "="*80)
            print("MENU OPTIONS:")
            print("  1. View Statistics")
            print("  2. View Recent Feedback (last 10)")
            print("  3. View Recent Feedback (last 50)")
            print("  4. View Feedback by Skill")
            print("  5. View Feedback by Date (YYYY-MM-DD)")
            print("  6. Search by Grade Range")
            print("  7. Export to CSV")
            print("  8. Exit")
            print("="*80)
            
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == '1':
                self.display_header()
                self.display_statistics()
            
            elif choice == '2':
                self.display_header()
                self.display_recent_feedback(10)
            
            elif choice == '3':
                self.display_header()
                self.display_recent_feedback(50)
            
            elif choice == '4':
                skill = input("Enter skill name (e.g., handstand, front_lever): ").strip()
                self.display_header()
                self.display_skill_feedback(skill)
            
            elif choice == '5':
                date = input("Enter date (YYYY-MM-DD): ").strip()
                self.display_header()
                self.display_date_feedback(date)
            
            elif choice == '6':
                try:
                    min_grade = float(input("Enter minimum grade: ").strip())
                    max_grade = float(input("Enter maximum grade: ").strip())
                    self.display_header()
                    self.search_by_grade_range(min_grade, max_grade)
                except ValueError:
                    print("❌ Invalid grade values")
            
            elif choice == '7':
                self.export_logs()
            
            elif choice == '8':
                print("\n👋 Goodbye!\n")
                break
            
            else:
                print("❌ Invalid choice. Please try again.")


def main():
    """Main entry point"""
    viewer = FeedbackViewer()
    
    # Check if command line arguments provided
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'stats':
            viewer.display_header()
            viewer.display_statistics()
        
        elif command == 'recent':
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            viewer.display_header()
            viewer.display_recent_feedback(count)
        
        elif command == 'skill':
            if len(sys.argv) < 3:
                print("Usage: python view_feedback_logs.py skill <skill_name>")
                return
            skill = sys.argv[2]
            viewer.display_header()
            viewer.display_skill_feedback(skill)
        
        elif command == 'date':
            if len(sys.argv) < 3:
                print("Usage: python view_feedback_logs.py date YYYY-MM-DD")
                return
            date = sys.argv[2]
            viewer.display_header()
            viewer.display_date_feedback(date)
        
        elif command == 'export':
            viewer.export_logs()
        
        else:
            print(f"Unknown command: {command}")
            print("Available commands: stats, recent, skill, date, export")
    
    else:
        # No arguments - show interactive menu
        viewer.display_header()
        viewer.display_statistics()
        viewer.interactive_menu()


if __name__ == "__main__":
    main()
