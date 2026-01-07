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

engine = create_engine(DATABASE_URL, pool_pre_ping=True)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
