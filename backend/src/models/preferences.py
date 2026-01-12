from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
import uuid

class UserPreferences(SQLModel, table=True):
    __tablename__ = "user_preferences"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", unique=True, index=True)
    autonomy_level: str = Field(default="low")  # "low", "medium", "high"
    enabled_categories: str = Field(default='["reminders", "scheduling"]')  # JSON string
    work_start_hour: int = Field(default=9)
    work_end_hour: int = Field(default=17)
