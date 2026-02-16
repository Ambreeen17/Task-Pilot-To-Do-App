"""
Phase 3: AI-Assisted Todo - AIMessage Model

Individual message in a conversation (user or assistant role).
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .ai_conversation import AIConversation
    from .parsed_task_intent import ParsedTaskIntent


class AIMessage(SQLModel, table=True):
    """
    Single message in a conversation.

    Role:
    - 'user': Message from the user
    - 'assistant': Response from Claude AI

    Constraints:
    - Content max 10,000 characters
    - Conversation must be active for new messages
    """

    __tablename__ = "ai_messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="ai_conversations.id", index=True)
    role: str = Field(max_length=20)
    content: str = Field(max_length=10000)
    timestamp: datetime = Field(default_factory=datetime.now)
    token_count: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    conversation: "AIConversation" = Relationship(back_populates="messages")
    parsed_intent: Optional["ParsedTaskIntent"] = Relationship(back_populates="message")

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": 1,
                "role": "user",
                "content": "Create a task to finish the report by Friday",
                "token_count": 12,
            }
        }
