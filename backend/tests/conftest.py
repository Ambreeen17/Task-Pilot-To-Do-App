import os
import uuid
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

# Ensure required env vars exist for import time
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_EXPIRATION_HOURS", "24")

from backend.src.main import app  # noqa: E402
from backend.src.database import get_session, engine as global_engine  # noqa: E402


@pytest.fixture(name="engine")
def engine_fixture():
    # Use StaticPool so all sessions share the same in-memory DB connection.
    from sqlalchemy.pool import StaticPool

    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Override the global engine in database.py so all code uses the same engine
    from backend.src import database
    database.engine = test_engine
    SQLModel.metadata.create_all(test_engine)
    return test_engine


@pytest.fixture(name="db")
def db_fixture(engine):
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(engine):
    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
