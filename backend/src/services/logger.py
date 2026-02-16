"\"\"
LogService for Phase 4 Autonomy - Structured audit logging for AI actions
\"\"\"

from typing import Optional, Dict, Any
from datetime import datetime, timezone
from sqlmodel import Session
import uuid
import logging

from ..database import get_session
from ..models.activity import AIActivityLog

logger = logging.getLogger(__name__)

class LogService:
    @classmethod
    def log_ai_action(
        cls,
        session: Session,
        user_id: uuid.UUID,
        action_type: str,
        entity_target: str,
        reasoning: str,
        status: str = 'pending',
        metadata: Optional[Dict[str, Any]] = None
    ) -> AIActivityLog:
        \"\"\"
        Log an AI autonomous action to ai_activity_log table

        Args:
            user_id: User UUID
            action_type: 'suggestion', 'notification', 'auto_action'
            entity_target: 'Task:123' or 'UserSettings'
            reasoning: Why the AI took this action
            status: 'pending', 'accepted', 'rejected', 'completed'
            metadata: Additional context

        Returns:
            Created AIActivityLog instance
        \"\"\"
        log_entry = AIActivityLog(
            user_id=user_id,
            action_type=action_type,
            entity_target=entity_target,
            reasoning=reasoning,
            status=status,
            timestamp=datetime.now(timezone.utc),
            metadata=metadata or {}
        )
        session.add(log_entry)
        session.commit()
        session.refresh(log_entry)
        logger.info(f\"Logged AI action: {action_type} for {entity_target} (status: {status})\")
        return log_entry

    @classmethod
    def get_recent_logs(cls, user_id: uuid.UUID, session: Session, limit: int = 50) -> list[AIActivityLog]:
        \"\"\"
        Retrieve recent AI activity logs for user
        \"\"\"
        from sqlmodel import select, desc
        query = select(AIActivityLog).where(
            AIActivityLog.user_id == user_id
        ).order_by(desc(AIActivityLog.timestamp)).limit(limit)
        return session.exec(query).all()