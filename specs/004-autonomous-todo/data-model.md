# Data Model - Phase 4

## Entities

### UserPreferences
Stores configuration for autonomy behavior.

```python
class UserPreferences(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    autonomy_level: str = Field(default="low") # "low", "medium", "high"
    enabled_categories: str = Field(default="[\"reminders\", \"scheduling\"]") # JSON string
    work_start_hour: int = Field(default=9)
    work_end_hour: int = Field(default=17)
```

### AIActivityLog
Audit record for all autonomous decisions.

```python
class AIActivityLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    action_type: str # "suggestion", "notification", "auto_action"
    entity_target: str # e.g. "Task:123"
    reasoning: str # "Task due in 1h, user inactive"
    status: str # "pending", "accepted", "rejected", "displayed"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

### PatternDetection
Cache of learned habits.

```python
class PatternDetection(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    pattern_type: str # "recurring_task", "work_habit"
    pattern_data: str # JSON: {"title": "Gym", "day": "Mon"}
    confidence_score: float
    last_detected: datetime
```
