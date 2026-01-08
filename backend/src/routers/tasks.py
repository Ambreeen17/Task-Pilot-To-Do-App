import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, and_, col, func, or_, select

from ..dependencies import get_current_user, get_db, get_task_or_404
from ..models.task import Task
from ..models.user import User
from ..schemas.task import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _task_to_response(task: Task) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        priority=task.priority,  # type: ignore[arg-type]
        due_date=task.due_date,
        completed=task.completed,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.get("", response_model=TaskListResponse)
def list_tasks(
    search: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None, pattern="^(completed|incomplete)$"),
    priority: Optional[str] = Query(default=None, pattern="^(Low|Medium|High)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskListResponse:
    filters = [Task.user_id == current_user.id]

    if status == "completed":
        filters.append(Task.completed == True)  # noqa: E712
    if status == "incomplete":
        filters.append(Task.completed == False)  # noqa: E712
    if priority:
        filters.append(Task.priority == priority)
    if search:
        like = f"%{search}%"
        filters.append(or_(col(Task.title).ilike(like), col(Task.description).ilike(like)))

    stmt = select(Task).where(and_(*filters)).order_by(Task.created_at.desc())

    total = db.exec(select(func.count()).select_from(stmt.subquery())).one()

    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    tasks = db.exec(stmt).all()

    return TaskListResponse(
        tasks=[_task_to_response(t) for t in tasks],
        total=int(total),
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(
    payload: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskResponse:
    task = Task(
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        due_date=payload.due_date,
        completed=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return _task_to_response(task)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task: Task = Depends(get_task_or_404)) -> TaskResponse:
    return _task_to_response(task)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    payload: TaskUpdate,
    task: Task = Depends(get_task_or_404),
    db: Session = Depends(get_db),
) -> TaskResponse:
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(task, k, v)
    task.updated_at = datetime.now(timezone.utc)
    db.add(task)
    db.commit()
    db.refresh(task)
    return _task_to_response(task)


@router.patch("/{task_id}/toggle", response_model=dict)
def toggle_task(
    task: Task = Depends(get_task_or_404),
    db: Session = Depends(get_db),
) -> dict:
    task.completed = not task.completed
    task.updated_at = datetime.now(timezone.utc)
    db.add(task)
    db.commit()
    db.refresh(task)
    return {"id": str(task.id), "completed": task.completed, "updated_at": task.updated_at.isoformat()}


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task: Task = Depends(get_task_or_404),
    db: Session = Depends(get_db),
):
    db.delete(task)
    db.commit()
    return None
