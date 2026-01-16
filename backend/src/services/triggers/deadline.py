"""DeadlineDetector for Phase 4 Autonomy

Detects tasks at risk of missing deadlines."""

from datetime import datetime, timedelta
from typing import List, Dict, Any
from ..models import Task  # Assume Task model exists from Phase 1-3

class DeadlineDetector:
    @staticmethod
    def detect_urgent_tasks(tasks: List[Dict], hours_threshold: int = 24) -> List[Dict]:
        urgent = []
        now = datetime.utcnow()
        threshold = now + timedelta(hours=hours_threshold)

        for task in tasks:
            due = datetime.fromisoformat(task.get('due_date'))
            if due <= threshold and not task.get('completed'):
                urgent.append({
                    'task_id': task['id'],
                    'reason': f"Due in < {hours_threshold}h",
                    'urgency': 'high' if due < now + timedelta(hours=2) else 'medium'
                })
        return urgent