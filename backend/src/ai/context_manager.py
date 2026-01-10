"""
Phase 3: AI-Assisted Todo - Context Manager

Manages conversation context with hybrid storage (in-memory + database).
"""

import os
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from dataclasses import dataclass, field

from sqlmodel import Session, select

logger = logging.getLogger(__name__)


@dataclass
class ConversationContext:
    """
    In-memory conversation state.

    Maintains last 10 messages and referenced task IDs for a user.
    """

    user_id: uuid.UUID
    conversation_id: Optional[int] = None
    messages: List[dict] = field(default_factory=list)  # Last 10 messages
    referenced_task_ids: List[uuid.UUID] = field(default_factory=list)  # Last 50 tasks
    last_topic: Optional[str] = None
    last_activity: datetime = field(default_factory=datetime.now)

    def add_message(self, role: str, content: str, timestamp: Optional[datetime] = None):
        """
        Add message to context and maintain 10-message window.

        Args:
            role: 'user' or 'assistant'
            content: Message text
            timestamp: Message timestamp (default: now)
        """
        msg = {
            "role": role,
            "content": content,
            "timestamp": (timestamp or datetime.now()).isoformat(),
        }
        self.messages.append(msg)
        self.messages = self.messages[-10:]  # Keep last 10
        self.last_activity = datetime.now()

    def add_task_reference(self, task_id: uuid.UUID):
        """
        Track referenced task ID.

        Args:
            task_id: Task UUID
        """
        if task_id not in self.referenced_task_ids:
            self.referenced_task_ids.append(task_id)
            # Keep last 50 task references
            if len(self.referenced_task_ids) > 50:
                self.referenced_task_ids = self.referenced_task_ids[-50:]

    def is_active(self, timeout_minutes: int = 10) -> bool:
        """
        Check if context is still active (not timed out).

        Args:
            timeout_minutes: Idle timeout in minutes

        Returns:
            True if active, False if timed out
        """
        elapsed = datetime.now() - self.last_activity
        return elapsed < timedelta(minutes=timeout_minutes)


class ContextManager:
    """
    Manages conversation contexts with hybrid storage.

    Strategy:
    - Active contexts (<10 min idle) kept in-memory
    - After timeout or explicit close, persist to database
    - Load from database on conversation resume
    """

    def __init__(self, timeout_minutes: Optional[int] = None):
        """
        Initialize context manager.

        Args:
            timeout_minutes: Idle timeout (default: from AI_CONTEXT_TIMEOUT_MINUTES env)
        """
        self.active_contexts: Dict[uuid.UUID, ConversationContext] = {}
        self.timeout_minutes = timeout_minutes or int(
            os.getenv("AI_CONTEXT_TIMEOUT_MINUTES", "10")
        )
        logger.info(
            f"Context manager initialized: {self.timeout_minutes} minute timeout"
        )

    def get_context(
        self, user_id: uuid.UUID, session: Session
    ) -> ConversationContext:
        """
        Get or create context for user.

        Args:
            user_id: User UUID
            session: Database session

        Returns:
            ConversationContext for user
        """
        # Check in-memory first
        if user_id in self.active_contexts:
            ctx = self.active_contexts[user_id]
            if ctx.is_active(self.timeout_minutes):
                logger.debug(f"Retrieved active context from memory for user {user_id}")
                return ctx
            else:
                # Timeout: persist to DB and remove from memory
                logger.info(
                    f"Context timed out for user {user_id}, persisting to database"
                )
                self.persist_context(ctx, session)
                del self.active_contexts[user_id]

        # Load from database or create new
        ctx = self._load_from_db(user_id, session)
        if ctx is None:
            logger.info(f"Creating new context for user {user_id}")
            ctx = ConversationContext(user_id=user_id)

        # Store in memory
        self.active_contexts[user_id] = ctx
        return ctx

    def update_context(
        self,
        user_id: uuid.UUID,
        role: str,
        content: str,
        session: Session,
        task_refs: Optional[List[uuid.UUID]] = None,
        topic: Optional[str] = None,
    ):
        """
        Update context with new message.

        Args:
            user_id: User UUID
            role: Message role ('user' or 'assistant')
            content: Message content
            session: Database session
            task_refs: Optional list of referenced task IDs
            topic: Optional conversation topic
        """
        ctx = self.get_context(user_id, session)
        ctx.add_message(role, content)

        if task_refs:
            for task_id in task_refs:
                ctx.add_task_reference(task_id)

        if topic:
            ctx.last_topic = topic

        logger.debug(
            f"Updated context for user {user_id}: {len(ctx.messages)} messages, {len(ctx.referenced_task_ids)} task refs"
        )

    def persist_context(self, ctx: ConversationContext, session: Session):
        """
        Persist context to database.

        Args:
            ctx: ConversationContext to persist
            session: Database session
        """
        from ..models import UserContext

        # Check if user context exists
        user_ctx = session.exec(
            select(UserContext).where(UserContext.user_id == ctx.user_id)
        ).first()

        if user_ctx:
            # Update existing
            user_ctx.active_conversation_id = ctx.conversation_id
            user_ctx.referenced_task_ids = [str(tid) for tid in ctx.referenced_task_ids]
            user_ctx.last_topic = ctx.last_topic
            user_ctx.last_updated = datetime.now()
            user_ctx.context_data = {"messages": ctx.messages}
        else:
            # Create new
            user_ctx = UserContext(
                user_id=ctx.user_id,
                active_conversation_id=ctx.conversation_id,
                referenced_task_ids=[str(tid) for tid in ctx.referenced_task_ids],
                last_topic=ctx.last_topic,
                last_updated=datetime.now(),
                context_data={"messages": ctx.messages},
            )
            session.add(user_ctx)

        session.commit()
        logger.info(f"Persisted context for user {ctx.user_id} to database")

    def _load_from_db(
        self, user_id: uuid.UUID, session: Session
    ) -> Optional[ConversationContext]:
        """
        Load context from database.

        Args:
            user_id: User UUID
            session: Database session

        Returns:
            ConversationContext if found, None otherwise
        """
        from ..models import UserContext

        user_ctx = session.exec(
            select(UserContext).where(UserContext.user_id == user_id)
        ).first()

        if not user_ctx:
            return None

        # Reconstruct context from database
        ctx = ConversationContext(
            user_id=user_id,
            conversation_id=user_ctx.active_conversation_id,
            referenced_task_ids=[
                uuid.UUID(tid) for tid in user_ctx.referenced_task_ids
            ],
            last_topic=user_ctx.last_topic,
            last_activity=user_ctx.last_updated,
        )

        # Load messages from context_data
        if user_ctx.context_data and "messages" in user_ctx.context_data:
            ctx.messages = user_ctx.context_data["messages"]

        logger.info(f"Loaded context from database for user {user_id}")
        return ctx

    def close_context(self, user_id: uuid.UUID, session: Session):
        """
        Explicitly close context and persist to database.

        Args:
            user_id: User UUID
            session: Database session
        """
        if user_id in self.active_contexts:
            ctx = self.active_contexts[user_id]
            self.persist_context(ctx, session)
            del self.active_contexts[user_id]
            logger.info(f"Closed context for user {user_id}")

    def clear_context(self, user_id: uuid.UUID, session: Session):
        """
        Clear context for user (reset conversation).

        Args:
            user_id: User UUID
            session: Database session
        """
        from ..models import UserContext

        # Remove from memory
        if user_id in self.active_contexts:
            del self.active_contexts[user_id]

        # Remove from database
        user_ctx = session.exec(
            select(UserContext).where(UserContext.user_id == user_id)
        ).first()
        if user_ctx:
            session.delete(user_ctx)
            session.commit()

        logger.info(f"Cleared context for user {user_id}")

    def get_active_count(self) -> int:
        """
        Get number of active contexts in memory.

        Returns:
            Count of active contexts
        """
        return len(self.active_contexts)


# Global context manager instance
_context_manager: Optional[ContextManager] = None


def get_context_manager() -> ContextManager:
    """
    Get or create global context manager instance.

    Returns:
        ContextManager instance
    """
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager


def reset_context_manager():
    """Reset global context manager instance (useful for testing)."""
    global _context_manager
    _context_manager = None
