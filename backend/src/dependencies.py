import uuid
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from .auth import decode_token
from .database import get_session
from .models.task import Task
from .models.user import User

security = HTTPBearer()

# Alias so FastAPI dependency overrides for get_session apply.
get_db = get_session


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        uid = uuid.UUID(str(user_id))
    except ValueError:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = db.exec(select(User).where(User.id == uid)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


def get_task_or_404(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Task:
    task = db.exec(select(Task).where(Task.id == task_id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this task")
    return task
