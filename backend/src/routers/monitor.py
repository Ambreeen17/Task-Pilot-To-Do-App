"""Phase 4: Autonomy Monitor Router

Endpoints:
- GET /monitor/settings - Get user autonomy preferences
- PUT /monitor/settings - Update user autonomy preferences
- GET /monitor/logs - Get AI activity logs

"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlmodel import Session, select
from datetime import datetime
import json
import uuid
import logging

from ..database import get_session
from ..dependencies import get_current_user
from ..models import User, UserPreferences, AIActivityLog
from ..services.logger import LogService

logger = logging.getLogger(__name__)
router = APIRouter(prefix=\"/monitor\", tags=[\"monitor\"])

@router.get(\"/settings\")
def get_autonomy_settings(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> Dict[str, Any]:
    prefs = session.exec(select(UserPreferences).where(UserPreferences.user_id == current_user.id)).first()
    if not prefs:
        prefs = UserPreferences(user_id=current_user.id)
        session.add(prefs)
        session.commit()
        session.refresh(prefs)

    return {
        \"autonomy_level\": prefs.autonomy_level,
        \"enabled_categories\": json.loads(prefs.enabled_categories or '[]'),
        \"learning_enabled\": prefs.learning_enabled,
        \"pattern_visibility\": prefs.pattern_visibility
    }

@router.put(\"/settings\")
def update_autonomy_settings(update_data: Dict[str, Any], current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    prefs = session.exec(select(UserPreferences).where(UserPreferences.user_id == current_user.id)).first()
    if not prefs:
        prefs = UserPreferences(user_id=current_user.id)
        session.add(prefs)

    for key, value in update_data.items():
        if hasattr(prefs, key):
            setattr(prefs, key, value)

    session.commit()
    session.refresh(prefs)

    LogService.log_ai_action(session, current_user.id, \"settings_update\", \"UserPreferences\", f\"Updated {list(update_data.keys())}\")

    return {\"message\": \"Settings updated\", \"settings\": get_autonomy_settings(current_user, session)}

@router.get(\"/logs\")
def get_activity_logs(limit: int = Query(50), current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    logs = LogService.get_recent_logs(current_user.id, session, limit)
    return {\"logs\": [log.dict() for log in logs]}