import os
from typing import Generator

from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# For local development/tests we allow the app to boot without DATABASE_URL.
# Tests override the session/engine; production must set DATABASE_URL.
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./dev.db"

engine = None  # Will be initialized in init_engine()


def init_engine():
    """Initialize the database engine. Call this after import if needed."""
    global engine
    if engine is None:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    return engine


# Initialize engine on module load
init_engine()


def init_db() -> None:
    # Use explicit imports to ensure all models are registered with SQLModel
    from .models.user import User
    from .models.task import Task
    from .models.activity import AIActivityLog
    from .models.preferences import UserPreferences
    from .models.ai_conversation import AIConversation
    from .models.ai_message import AIMessage
    from .models.parsed_task_intent import ParsedTaskIntent
    from .models.ai_insight import AIInsight
    from .models.task_summary import TaskSummary
    from .models.user_context import UserContext

    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
