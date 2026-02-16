"""ActionValidator for Phase 4 Autonomy

Validates suggestions against user preferences and safety rules."""

from typing import Dict, Any, List

class ActionValidator:
    PROHIBITED_ACTIONS = [
        'delete_all_tasks',
        'modify_critical_data',
        'external_api_calls'
    ]

    @staticmethod
    def validate(suggestion: Dict, user_prefs: Dict) -> bool:
        # Check autonomy level
        level_map = {'low': 0.9, 'medium': 0.7, 'high': 0.5}
        confidence = suggestion.get('confidence', 0.5)
        if confidence < level_map.get(user_prefs.get('autonomy_level', 'low'), 0.5):
            return False

        # Check prohibited actions
        action_type = suggestion.get('action_type', '')
        if any(prohibited in action_type.lower() for prohibited in ActionValidator.PROHIBITED_ACTIONS):
            return False

        # Check enabled categories
        enabled = user_prefs.get('enabled_categories', [])
        if not any(cat in suggestion.get('category', '') for cat in enabled):
            return False

        return True