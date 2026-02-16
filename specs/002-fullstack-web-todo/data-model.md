# Data Model: Phase 2 — Full Stack Web Todo

**Feature Branch**: `002-fullstack-web-todo`
**Created**: 2026-01-06
**Related Spec**: [spec.md](spec.md)

## Overview

This document defines the data model for the Phase 2 full-stack web todo application. The data model is implemented using SQLModel (SQLAlchemy + Pydantic) for the FastAPI backend with PostgreSQL as the database.

## Entity Relationship Diagram

```
+-----------------+         +-----------------+
|     Users       |         |     Tasks       |
+-----------------+         +-----------------+
| id (PK)         |<--------| user_id (FK)    |
| email           |         | id (PK)         |
| password_hash   |         | title           |
| created_at      |         | description     |
| updated_at      |         | priority        |
+-----------------+         | due_date        |
        |                   | completed       |
        |                   | created_at      |
        +-------------------+| updated_at      |
                            +-----------------+
Relationship: One-to-Many (User has many Tasks)
```

## Entities

### User Entity

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique user identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email address |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt hashed password |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation time |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update time |

**Python Model (SQLModel):**

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
import uuid

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, nullable=False, max_length=255)
    password_hash: str = Field(nullable=False, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    tasks: list["Task"] = Relationship(back_populates="user")
```

### Task Entity

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique task identifier |
| user_id | UUID | FOREIGN KEY, NOT NULL | Owner user reference |
| title | VARCHAR(500) | NOT NULL | Task title |
| description | TEXT | NULLABLE | Task description |
| priority | VARCHAR(20) | DEFAULT 'Medium' | Priority level |
| due_date | TIMESTAMP | NULLABLE | Due date for task |
| completed | BOOLEAN | DEFAULT FALSE | Completion status |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Task creation time |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update time |

**Priority Values:** Low, Medium (default), High

**Python Model (SQLModel):**

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
import uuid
from enum import Enum

class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class Task(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", ondelete="CASCADE", nullable=False)
    title: str = Field(nullable=False, max_length=500)
    description: Optional[str] = Field(default=None)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    due_date: Optional[datetime] = Field(default=None)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: User = Relationship(back_populates="tasks")
```

## Database Schema (PostgreSQL)

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    priority VARCHAR(20) DEFAULT 'Medium' CHECK (priority IN ('Low', 'Medium', 'High')),
    due_date TIMESTAMP WITH TIME ZONE,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
```

## API Schemas (Pydantic)

### User Schemas

```python
from pydantic import BaseModel, EmailStr
from datetime import datetime
import uuid

class UserCreate(BaseModel):
    email: EmailStr
    password: str  # Min 8 characters

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str
```

### Task Schemas

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid
from enum import Enum

class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class TaskCreate(BaseModel):
    title: str  # Max 500 chars
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    completed: Optional[bool] = None

class TaskResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: Optional[str]
    priority: TaskPriority
    due_date: Optional[datetime]
    completed: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    total: int
```

## Validation Rules

### User Validation
- **Email**: Must be valid email format (RFC 5322)
- **Password**: Minimum 8 characters
- **Email Uniqueness**: System rejects duplicate emails

### Task Validation
- **Title**: Required, 1-500 characters
- **Description**: Optional, no length limit
- **Priority**: Must be one of: Low, Medium, High
- **Due Date**: Optional, must be valid timestamp

## Data Integrity Invariants

1. **User Isolation**: Tasks.user_id must reference existing users.id
2. **Cascade Delete**: Deleting user deletes all associated tasks
3. **Timestamps**: All timestamps stored in UTC
4. **Passwords**: Never stored in plaintext (bcrypt hash only)
5. **Unique Email**: Single account per email address
