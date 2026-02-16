# Data Model: Phase 1 — Foundation Todo System

This document describes the data model for the Phase 1 Todo system.

## Task Entity

### Attributes

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `id` | string | Yes | Auto-generated | Unique identifier for the task |
| `title` | string | Yes | N/A | Short description of the task |
| `description` | string | No | `""` | Detailed information about the task |
| `completed` | boolean | No | `False` | Whether the task has been completed |

### Class Definition

```python
class Task:
    """Represents a single todo item."""

    def __init__(self, id: str, title: str, description: str = "", completed: bool = False):
        self.id = id
        self.title = title
        self.description = description
        self.completed = completed

    def to_dict(self) -> dict:
        """Convert task to dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Create Task from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            completed=data.get("completed", False)
        )
```

## Storage Model

### TaskStorage Class

```python
class TaskStorage:
    """In-memory storage for tasks."""

    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        self._next_id: int = 1

    def add(self, task: Task) -> None:
        """Add a task to storage."""
        self._tasks[task.id] = task

    def get(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by ID."""
        return self._tasks.get(task_id)

    def get_all(self) -> List[Task]:
        """Retrieve all tasks."""
        return list(self._tasks.values())

    def update(self, task_id: str, task: Task) -> bool:
        """Update an existing task."""
        if task_id not in self._tasks:
            return False
        self._tasks[task_id] = task
        return True

    def delete(self, task_id: str) -> bool:
        """Delete a task by ID."""
        if task_id not in self._tasks:
            return False
        del self._tasks[task_id]
        return True

    def exists(self, task_id: str) -> bool:
        """Check if a task exists."""
        return task_id in self._tasks

    def generate_id(self) -> str:
        """Generate a unique task ID."""
        task_id = str(self._next_id)
        self._next_id += 1
        return task_id
```

### Storage Characteristics

- **Backend**: In-memory dictionary
- **Session Scope**: Data persists only while program runs
- **ID Generation**: Sequential integers (1, 2, 3, ...)
- **Lookup Complexity**: O(1) for all operations

## Validation Rules

### Title Validation

| Rule | Constraint |
|------|------------|
| Minimum length | 1 character |
| Maximum length | 500 characters |
| Allowed characters | All Unicode characters except control characters |
| Empty check | Must not be empty or whitespace-only |

### Description Validation

| Rule | Constraint |
|------|------------|
| Minimum length | 0 characters |
| Maximum length | 5000 characters |
| Allowed characters | All Unicode characters |
| Default value | Empty string (`""`) |

### Task ID Validation

| Rule | Constraint |
|------|------------|
| Format | String matching existing task IDs |
| Existence | Must exist in storage for read/update/delete operations |
| Case sensitivity | Case-sensitive (string comparison) |

## State Transitions

### Task Lifecycle

```
┌─────────────┐
│   Created   │ ← New task enters here
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│   Active    │ ──▶ │  Completed  │
│ (default)   │     │             │
└─────────────┘     └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Deleted   │ ← Removed from storage
                    └─────────────┘
```

### Allowed Transitions

| From | To | Allowed |
|------|-----|---------|
| Created | Active | Yes (implicit) |
| Active | Completed | Yes (mark_complete) |
| Completed | Active | Yes (mark_incomplete) |
| Any | Deleted | Yes (delete) |

### Forbidden Transitions

| From | To | Reason |
|------|-----|--------|
| Deleted | Any | Task no longer exists |
| None | Active | Must be created first |

## Data Constraints

### Invariants

1. **INV-001**: Task IDs remain unique throughout the session
2. **INV-002**: No task is automatically modified or deleted
3. **INV-003**: All task attributes preserve their values until explicitly changed
4. **INV-004**: Operations produce consistent, deterministic results

### Future Extension Points

The data model is designed to support future phases:

| Future Feature | Extension Point |
|----------------|-----------------|
| Priority levels | Add `priority` field to Task |
| Due dates | Add `due_date` field to Task |
| Categories | Add `category` field to Task |
| User ownership | Add `user_id` field to Task |
| Tags | Add `tags` list field to Task |

## Serialization

### Dictionary Format

```python
{
    "id": "1",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": False
}
```

### Display Format

```
ID: 1
Title: Buy groceries
Description: Milk, eggs, bread
Completed: No
```
