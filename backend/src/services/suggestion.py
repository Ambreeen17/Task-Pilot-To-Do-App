"""SuggestionEngine for Phase 4 Autonomy

Combines triggers to generate actionable suggestions."""

from typing import List, Dict, Any
from .triggers.deadline import DeadlineDetector
from .triggers.pattern import PatternDetector

class SuggestionEngine:
    def __init__(self):
        self.detectors = [DeadlineDetector, PatternDetector]

    def generate_suggestions(self, tasks: List[Dict], user_prefs: Dict) -> List[Dict]:
        suggestions = []

        for detector in self.detectors:
            detector_instance = detector()
            if hasattr(detector_instance, 'detect_urgent_tasks'):
                suggestions.extend(detector_instance.detect_urgent_tasks(tasks))
            elif hasattr(detector_instance, 'detect_patterns'):
                suggestions.extend(detector_instance.detect_patterns(tasks))

        # Filter by user preferences
        enabled_cats = user_prefs.get('enabled_categories', [])
        filtered = [s for s in suggestions if any(cat in s.get('reason', '') for cat in enabled_cats)]

        return filtered[:5]  # Limit to top 5