"""PatternDetector for Phase 4 Autonomy

Detects behavioral patterns in user task history."""

from typing import List, Dict, Any, Optional
from collections import Counter

class PatternDetector:
    @staticmethod
    def detect_patterns(tasks: List[Dict], days_back: int = 7) -> List[Dict]:
        patterns = []

        # Example: Recurring tasks at same time/day
        task_times = [t['created_at'].hour for t in tasks if 'created_at' in t]
        if len(task_times) > 3:
            common_hour = Counter(task_times).most_common(1)[0][0]
            patterns.append({
                'type': 'recurring_time',
                'pattern': f"Tasks created at {common_hour}:00",
                'confidence': 0.8
            })

        # Example: Priority patterns
        priorities = [t.get('priority', 'medium') for t in tasks]
        priority_dist = Counter(priorities)
        if priority_dist['high'] / len(tasks) > 0.3:
            patterns.append({
                'type': 'high_priority_bias',
                'pattern': 'User sets high priority >30% of tasks',
                'confidence': 0.7
            })

        return patterns