# Data Model: Phase 3 — AI-Assisted Todo

**Feature**: 003-ai-assisted-todo | **Date**: 2026-01-10 | **Status**: Design Phase

## Overview

This document defines the database schema and entity relationships for Phase 3 AI capabilities. All entities extend the existing Phase 2 schema without modifying core task management tables.

**Design Principles**:
- User-scoped isolation (all AI data belongs to a user)
- Soft deletes for conversations (audit trail)
- Optimistic concurrency for context updates
- Time-series optimization for summaries and insights

## Entity Diagram

```text
┌─────────────────┐
│      User       │ (Phase 2 - existing)
│  (id, email)    │
└────────┬────────┘
         │
         │ 1:N
         │
    ┌────┴─────────────────────────────────────────────────────┐
    │                                                            │
┌───▼──────────────┐  1:N   ┌──────────────────┐               │
│ AIConversation   ├────────► AIMessage         │               │
│                  │         │                  │               │
│ - id             │         │ - id             │               │
│ - user_id (FK)   │         │ - conversation_id│               │
│ - start_time     │         │ - role           │               │
│ - last_activity  │         │ - content        │               │
│ - status         │         │ - timestamp      │               │
│ - context_window │         │ - parsed_intent  │               │
└──────────────────┘         └──────┬───────────┘               │
                                    │                           │
                                    │ 1:1                       │
                                    │                           │
                             ┌──────▼──────────────┐            │
                             │ ParsedTaskIntent    │            │
                             │                     │            │
                             │ - id                │            │
                             │ - message_id (FK)   │            │
                             │ - original_text     │            │
                             │ - extracted_title   │            │
                             │ - extracted_priority│            │
                             │ - extracted_date    │            │
                             │ - confidence_scores │            │
                             │ - confirmed         │            │
                             └─────────────────────┘            │
                                                                │
    ┌───────────────────────────────────────────────────────────┘
    │
    │ 1:N                              1:N
    │                                  │
┌───▼──────────────┐          ┌───────▼──────────┐
│ TaskSummary      │          │ AIInsight        │
│                  │          │                  │
│ - id             │          │ - id             │
│ - user_id (FK)   │          │ - user_id (FK)   │
│ - period_type    │          │ - insight_type   │
│ - start_date     │          │ - title          │
│ - end_date       │          │ - description    │
│ - metrics (JSON) │          │ - supporting_data│
│ - summary_text   │          │ - priority       │
│ - generated_at   │          │ - created_at     │
└──────────────────┘          │ - dismissed_at   │
                              └──────────────────┘

┌─────────────────┐
│  UserContext    │ (In-memory with periodic DB sync)
│                 │
│ - user_id (PK)  │
│ - conversation  │
│ - messages (10) │
│ - task_refs     │
│ - last_topic    │
│ - last_updated  │
└─────────────────┘
```

## Entities

### 1. AIConversation

Multi-turn conversation session between user and AI assistant.

**Table**: `ai_conversations`

```sql
CREATE TABLE ai_conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    start_time TIMESTAMP NOT NULL DEFAULT NOW(),
    last_activity_time TIMESTAMP NOT NULL DEFAULT NOW(),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    context_window INTEGER NOT NULL DEFAULT 10,
    topic VARCHAR(200),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP,

    CONSTRAINT valid_status CHECK (status IN ('active', 'closed', 'timeout')),
    CONSTRAINT valid_context_window CHECK (context_window > 0 AND context_window <= 20)
);

CREATE INDEX idx_ai_conversations_user_status ON ai_conversations(user_id, status);
CREATE INDEX idx_ai_conversations_last_activity ON ai_conversations(last_activity_time) WHERE deleted_at IS NULL;
```

**Attributes**:
- `id`: Unique conversation identifier
- `user_id`: Owner of conversation (FK to users.id)
- `start_time`: When conversation began
- `last_activity_time`: Last message timestamp (for timeout detection)
- `status`: Conversation state (active/closed/timeout)
- `context_window`: Number of messages to maintain (default 10)
- `topic`: AI-detected conversation topic (nullable)
- `created_at`: Record creation timestamp
- `updated_at`: Last modification timestamp
- `deleted_at`: Soft delete timestamp (nullable)

**Validation Rules** (from spec FR-016, FR-017):
- Context window between 1-20 messages
- Status must be one of: active, closed, timeout
- User must exist in Phase 2 users table
- last_activity_time updated on every message
- Auto-timeout after 10 minutes (handled by ContextManager)

**State Transitions**:
```text
       create()
          │
          ▼
    ┌─────────┐  add_message()  ┌─────────┐
    │ active  │◄────────────────┤ active  │
    └────┬────┘                 └────┬────┘
         │                           │
         │ timeout (10 min)          │ explicit_close()
         │                           │
         ▼                           ▼
    ┌─────────┐                ┌─────────┐
    │ timeout │                │ closed  │
    └─────────┘                └─────────┘
```

**Relationships**:
- `user_id` → `users.id` (N:1)
- Has many `ai_messages` (1:N)
- Referenced by `user_context` (1:1 active)

---

### 2. AIMessage

Individual message in a conversation (user or assistant role).

**Table**: `ai_messages`

```sql
CREATE TABLE ai_messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES ai_conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    token_count INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_role CHECK (role IN ('user', 'assistant')),
    CONSTRAINT valid_content_length CHECK (LENGTH(content) <= 10000)
);

CREATE INDEX idx_ai_messages_conversation ON ai_messages(conversation_id, timestamp);
CREATE INDEX idx_ai_messages_role ON ai_messages(conversation_id, role);
```

**Attributes**:
- `id`: Unique message identifier
- `conversation_id`: Parent conversation (FK to ai_conversations.id)
- `role`: Message sender (user or assistant)
- `content`: Message text (max 10,000 chars per FR-024)
- `timestamp`: When message was created
- `token_count`: Estimated tokens for cost tracking (nullable)
- `created_at`: Record creation timestamp

**Validation Rules** (from spec FR-024):
- Content max 10,000 characters (truncate with warning)
- Role must be 'user' or 'assistant'
- Conversation must exist and be active
- User messages trigger AI responses

**Relationships**:
- `conversation_id` → `ai_conversations.id` (N:1)
- May have one `parsed_task_intent` (1:1) if role='user'

---

### 3. ParsedTaskIntent

Structured data extracted from natural language input.

**Table**: `parsed_task_intents`

```sql
CREATE TABLE parsed_task_intents (
    id SERIAL PRIMARY KEY,
    message_id INTEGER NOT NULL REFERENCES ai_messages(id) ON DELETE CASCADE,
    original_text TEXT NOT NULL,
    extracted_title VARCHAR(200),
    extracted_priority VARCHAR(10),
    extracted_due_date DATE,
    extracted_due_time TIME,
    confidence_scores JSONB NOT NULL,
    confirmed BOOLEAN NOT NULL DEFAULT FALSE,
    task_id INTEGER REFERENCES tasks(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    confirmed_at TIMESTAMP,

    CONSTRAINT valid_priority CHECK (extracted_priority IN ('Low', 'Medium', 'High', NULL)),
    CONSTRAINT valid_confidence_scores CHECK (
        (confidence_scores->>'title')::FLOAT >= 0.0 AND (confidence_scores->>'title')::FLOAT <= 1.0 AND
        (confidence_scores->>'priority')::FLOAT >= 0.0 AND (confidence_scores->>'priority')::FLOAT <= 1.0 AND
        (confidence_scores->>'due_date')::FLOAT >= 0.0 AND (confidence_scores->>'due_date')::FLOAT <= 1.0
    )
);

CREATE INDEX idx_parsed_intents_message ON parsed_task_intents(message_id);
CREATE INDEX idx_parsed_intents_confirmed ON parsed_task_intents(confirmed, created_at);
CREATE INDEX idx_parsed_intents_task ON parsed_task_intents(task_id) WHERE task_id IS NOT NULL;
```

**Attributes**:
- `id`: Unique intent identifier
- `message_id`: Source message (FK to ai_messages.id)
- `original_text`: Raw user input that was parsed
- `extracted_title`: Parsed task title (max 200 chars)
- `extracted_priority`: Parsed priority level (Low/Medium/High or NULL)
- `extracted_due_date`: Parsed due date (nullable)
- `extracted_due_time`: Parsed due time (nullable)
- `confidence_scores`: JSON object with scores for each field
- `confirmed`: Whether user approved the interpretation
- `task_id`: Created task (FK to tasks.id, nullable until confirmed)
- `created_at`: When parsing occurred
- `confirmed_at`: When user confirmed (nullable)

**Validation Rules** (from spec FR-001, FR-002, FR-003):
- Title required if extracted (FR-001)
- Priority must be Low/Medium/High or NULL (FR-001)
- Confidence scores between 0.0-1.0 for each field (FR-002)
- All fields editable until confirmed (FR-003)
- Confidence threshold for auto-confirm: ≥0.9 (research.md decision)

**Confidence Score Schema**:
```json
{
  "title": 0.95,      // 0.0-1.0
  "priority": 0.75,   // 0.0-1.0
  "due_date": 0.90    // 0.0-1.0
}
```

**Interpretation Confidence Levels** (from research.md):
- ≥0.9: High confidence (auto-accept)
- 0.7-0.89: Medium confidence (show in UI, allow edit)
- <0.7: Low confidence (flag as uncertain, prompt review)

**Relationships**:
- `message_id` → `ai_messages.id` (1:1)
- `task_id` → `tasks.id` (1:1 after confirmation)

---

### 4. TaskSummary

AI-generated summary of tasks over a time period.

**Table**: `task_summaries`

```sql
CREATE TABLE task_summaries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    period_type VARCHAR(20) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    metrics JSONB NOT NULL,
    summary_text TEXT NOT NULL,
    generated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_period_type CHECK (period_type IN ('daily', 'weekly', 'monthly', 'custom')),
    CONSTRAINT valid_date_range CHECK (end_date >= start_date),
    CONSTRAINT unique_user_period UNIQUE (user_id, period_type, start_date, end_date)
);

CREATE INDEX idx_task_summaries_user_period ON task_summaries(user_id, period_type, start_date DESC);
```

**Attributes**:
- `id`: Unique summary identifier
- `user_id`: Summary owner (FK to users.id)
- `period_type`: Timeframe (daily/weekly/monthly/custom)
- `start_date`: Period start (inclusive)
- `end_date`: Period end (inclusive)
- `metrics`: JSON object with calculated metrics
- `summary_text`: AI-generated natural language summary
- `generated_at`: When summary was created

**Validation Rules** (from spec FR-009, FR-010):
- Period type must be daily/weekly/monthly/custom (FR-009)
- end_date >= start_date
- One summary per user per period (unique constraint)
- Minimum 7 days of data required for insights (FR-011)

**Metrics Schema** (from spec FR-009):
```json
{
  "total_tasks": 42,
  "completed": 30,
  "pending": 8,
  "overdue": 4,
  "completion_rate": 0.71,
  "priority_distribution": {
    "Low": 15,
    "Medium": 20,
    "High": 7
  },
  "tasks_by_day": {
    "2026-01-03": 6,
    "2026-01-04": 4,
    "...": "..."
  },
  "average_completion_time_hours": 48.5
}
```

**Relationships**:
- `user_id` → `users.id` (N:1)
- No direct FK to tasks (calculated from task history at generation time)

---

### 5. AIInsight

Pattern-based recommendation or productivity insight.

**Table**: `ai_insights`

```sql
CREATE TABLE ai_insights (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    insight_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    supporting_data JSONB NOT NULL,
    priority VARCHAR(10) NOT NULL DEFAULT 'Medium',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    dismissed_at TIMESTAMP,
    dismissed_reason TEXT,

    CONSTRAINT valid_insight_type CHECK (insight_type IN (
        'overdue_pattern', 'productivity_trend', 'priority_imbalance',
        'completion_streak', 'workload_warning', 'time_management',
        'recurring_task', 'other'
    )),
    CONSTRAINT valid_priority CHECK (priority IN ('Low', 'Medium', 'High'))
);

CREATE INDEX idx_ai_insights_user_created ON ai_insights(user_id, created_at DESC);
CREATE INDEX idx_ai_insights_type ON ai_insights(user_id, insight_type) WHERE dismissed_at IS NULL;
CREATE INDEX idx_ai_insights_active ON ai_insights(user_id) WHERE dismissed_at IS NULL;
```

**Attributes**:
- `id`: Unique insight identifier
- `user_id`: Insight recipient (FK to users.id)
- `insight_type`: Category of insight
- `title`: Short insight headline (max 200 chars)
- `description`: Detailed explanation and recommendation
- `supporting_data`: JSON with evidence/metrics
- `priority`: Insight urgency (Low/Medium/High)
- `created_at`: When insight was generated
- `dismissed_at`: When user dismissed (nullable)
- `dismissed_reason`: Optional user feedback on dismissal

**Validation Rules** (from spec FR-012, FR-013, FR-014):
- Minimum 10 tasks required for insights (FR-011)
- Minimum 7 days of history required (FR-011)
- Insight type must be from predefined list
- Priority required (default Medium)
- Users can dismiss insights (FR-025 opt-out)

**Insight Types**:
- `overdue_pattern`: User consistently has overdue tasks
- `productivity_trend`: Completion rate improving/declining
- `priority_imbalance`: Too many High priority tasks
- `completion_streak`: User completing tasks consistently
- `workload_warning`: Too many tasks due soon
- `time_management`: Tasks taking longer than expected
- `recurring_task`: Detected repeating task pattern
- `other`: Miscellaneous insights

**Supporting Data Schema Examples**:

Overdue Pattern:
```json
{
  "overdue_count": 5,
  "average_overdue_days": 3.2,
  "affected_priorities": ["High", "Medium"],
  "suggested_action": "Consider setting earlier due dates or breaking tasks into smaller chunks"
}
```

Productivity Trend:
```json
{
  "period": "last_14_days",
  "completion_rate_current": 0.85,
  "completion_rate_previous": 0.70,
  "trend": "improving",
  "change_percentage": 21.4
}
```

**Relationships**:
- `user_id` → `users.id` (N:1)
- No direct FK to tasks (insights derived from task patterns)

---

### 6. UserContext (Hybrid Storage)

Current conversation state for active users. Stored in-memory with periodic database sync.

**Table**: `user_contexts` (database backup)

```sql
CREATE TABLE user_contexts (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    active_conversation_id INTEGER REFERENCES ai_conversations(id),
    referenced_task_ids INTEGER[] DEFAULT ARRAY[]::INTEGER[],
    last_topic VARCHAR(200),
    last_updated TIMESTAMP NOT NULL DEFAULT NOW(),
    context_data JSONB,

    CONSTRAINT valid_task_refs CHECK (ARRAY_LENGTH(referenced_task_ids, 1) IS NULL OR ARRAY_LENGTH(referenced_task_ids, 1) <= 50)
);

CREATE INDEX idx_user_contexts_conversation ON user_contexts(active_conversation_id);
CREATE INDEX idx_user_contexts_updated ON user_contexts(last_updated);
```

**In-Memory Representation** (Python dataclass):
```python
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class UserContext:
    user_id: int
    active_conversation_id: Optional[int] = None
    messages: List[dict] = field(default_factory=list)  # Last 10 messages
    referenced_task_ids: List[int] = field(default_factory=list)  # Max 50
    last_topic: Optional[str] = None
    last_updated: datetime = field(default_factory=datetime.now)

    def add_message(self, role: str, content: str):
        """Add message and maintain 10-message window"""
        self.messages.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        self.messages = self.messages[-10:]  # Keep last 10
        self.last_updated = datetime.now()

    def add_task_reference(self, task_id: int):
        """Track referenced tasks"""
        if task_id not in self.referenced_task_ids:
            self.referenced_task_ids.append(task_id)
            if len(self.referenced_task_ids) > 50:
                self.referenced_task_ids = self.referenced_task_ids[-50:]
```

**Attributes**:
- `user_id`: Context owner (PK, FK to users.id)
- `active_conversation_id`: Current conversation (FK to ai_conversations.id, nullable)
- `referenced_task_ids`: Array of task IDs mentioned in conversation (max 50)
- `last_topic`: AI-detected topic from last interaction
- `last_updated`: Last modification timestamp
- `context_data`: JSON blob for additional context

**Validation Rules** (from spec FR-016, FR-017):
- Messages limited to 10 most recent (context window, FR-016)
- Referenced tasks limited to 50 most recent
- Sync to database every 5 minutes or on timeout
- Clear on explicit conversation close (FR-017)

**Storage Strategy** (from research.md):
- Active contexts kept in-memory (ContextManager)
- Timeout after 10 minutes of inactivity
- Persist to database on timeout or explicit close
- Load from database on conversation resume

**Relationships**:
- `user_id` → `users.id` (1:1)
- `active_conversation_id` → `ai_conversations.id` (N:1)
- `referenced_task_ids` → `tasks.id[]` (N:N indirect)

---

## Phase 2 Dependencies

### Existing Tables (No Modifications)

Phase 3 AI entities reference but do not modify Phase 2 tables:

**users** (existing):
```sql
-- Phase 2 schema (unchanged)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    timezone VARCHAR(50) DEFAULT 'UTC',  -- Used for AI date parsing
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

**tasks** (existing):
```sql
-- Phase 2 schema (unchanged)
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    priority VARCHAR(10) CHECK (priority IN ('Low', 'Medium', 'High')),
    status VARCHAR(20) DEFAULT 'pending',
    due_date DATE,
    due_time TIME,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP
);
```

**AI Integration Points**:
- `parsed_task_intents.task_id` → `tasks.id` (created after confirmation)
- AI summaries and insights query tasks table (read-only)
- User timezone from `users.timezone` used for date parsing

---

## Database Schema Migration

### Migration Script: `003_add_ai_tables.sql`

```sql
-- Migration: Add Phase 3 AI tables
-- Date: 2026-01-10
-- Feature: 003-ai-assisted-todo

BEGIN;

-- 1. AI Conversations
CREATE TABLE ai_conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    start_time TIMESTAMP NOT NULL DEFAULT NOW(),
    last_activity_time TIMESTAMP NOT NULL DEFAULT NOW(),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    context_window INTEGER NOT NULL DEFAULT 10,
    topic VARCHAR(200),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP,

    CONSTRAINT valid_status CHECK (status IN ('active', 'closed', 'timeout')),
    CONSTRAINT valid_context_window CHECK (context_window > 0 AND context_window <= 20)
);

CREATE INDEX idx_ai_conversations_user_status ON ai_conversations(user_id, status);
CREATE INDEX idx_ai_conversations_last_activity ON ai_conversations(last_activity_time) WHERE deleted_at IS NULL;

-- 2. AI Messages
CREATE TABLE ai_messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES ai_conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    token_count INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_role CHECK (role IN ('user', 'assistant')),
    CONSTRAINT valid_content_length CHECK (LENGTH(content) <= 10000)
);

CREATE INDEX idx_ai_messages_conversation ON ai_messages(conversation_id, timestamp);
CREATE INDEX idx_ai_messages_role ON ai_messages(conversation_id, role);

-- 3. Parsed Task Intents
CREATE TABLE parsed_task_intents (
    id SERIAL PRIMARY KEY,
    message_id INTEGER NOT NULL REFERENCES ai_messages(id) ON DELETE CASCADE,
    original_text TEXT NOT NULL,
    extracted_title VARCHAR(200),
    extracted_priority VARCHAR(10),
    extracted_due_date DATE,
    extracted_due_time TIME,
    confidence_scores JSONB NOT NULL,
    confirmed BOOLEAN NOT NULL DEFAULT FALSE,
    task_id INTEGER REFERENCES tasks(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    confirmed_at TIMESTAMP,

    CONSTRAINT valid_priority CHECK (extracted_priority IN ('Low', 'Medium', 'High', NULL)),
    CONSTRAINT valid_confidence_scores CHECK (
        (confidence_scores->>'title')::FLOAT >= 0.0 AND (confidence_scores->>'title')::FLOAT <= 1.0 AND
        (confidence_scores->>'priority')::FLOAT >= 0.0 AND (confidence_scores->>'priority')::FLOAT <= 1.0 AND
        (confidence_scores->>'due_date')::FLOAT >= 0.0 AND (confidence_scores->>'due_date')::FLOAT <= 1.0
    )
);

CREATE INDEX idx_parsed_intents_message ON parsed_task_intents(message_id);
CREATE INDEX idx_parsed_intents_confirmed ON parsed_task_intents(confirmed, created_at);
CREATE INDEX idx_parsed_intents_task ON parsed_task_intents(task_id) WHERE task_id IS NOT NULL;

-- 4. Task Summaries
CREATE TABLE task_summaries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    period_type VARCHAR(20) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    metrics JSONB NOT NULL,
    summary_text TEXT NOT NULL,
    generated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_period_type CHECK (period_type IN ('daily', 'weekly', 'monthly', 'custom')),
    CONSTRAINT valid_date_range CHECK (end_date >= start_date),
    CONSTRAINT unique_user_period UNIQUE (user_id, period_type, start_date, end_date)
);

CREATE INDEX idx_task_summaries_user_period ON task_summaries(user_id, period_type, start_date DESC);

-- 5. AI Insights
CREATE TABLE ai_insights (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    insight_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    supporting_data JSONB NOT NULL,
    priority VARCHAR(10) NOT NULL DEFAULT 'Medium',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    dismissed_at TIMESTAMP,
    dismissed_reason TEXT,

    CONSTRAINT valid_insight_type CHECK (insight_type IN (
        'overdue_pattern', 'productivity_trend', 'priority_imbalance',
        'completion_streak', 'workload_warning', 'time_management',
        'recurring_task', 'other'
    )),
    CONSTRAINT valid_priority CHECK (priority IN ('Low', 'Medium', 'High'))
);

CREATE INDEX idx_ai_insights_user_created ON ai_insights(user_id, created_at DESC);
CREATE INDEX idx_ai_insights_type ON ai_insights(user_id, insight_type) WHERE dismissed_at IS NULL;
CREATE INDEX idx_ai_insights_active ON ai_insights(user_id) WHERE dismissed_at IS NULL;

-- 6. User Contexts (backup storage)
CREATE TABLE user_contexts (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    active_conversation_id INTEGER REFERENCES ai_conversations(id),
    referenced_task_ids INTEGER[] DEFAULT ARRAY[]::INTEGER[],
    last_topic VARCHAR(200),
    last_updated TIMESTAMP NOT NULL DEFAULT NOW(),
    context_data JSONB,

    CONSTRAINT valid_task_refs CHECK (ARRAY_LENGTH(referenced_task_ids, 1) IS NULL OR ARRAY_LENGTH(referenced_task_ids, 1) <= 50)
);

CREATE INDEX idx_user_contexts_conversation ON user_contexts(active_conversation_id);
CREATE INDEX idx_user_contexts_updated ON user_contexts(last_updated);

COMMIT;
```

### Rollback Script: `003_rollback_ai_tables.sql`

```sql
-- Rollback: Remove Phase 3 AI tables
BEGIN;

DROP TABLE IF EXISTS user_contexts;
DROP TABLE IF EXISTS ai_insights;
DROP TABLE IF EXISTS task_summaries;
DROP TABLE IF EXISTS parsed_task_intents;
DROP TABLE IF EXISTS ai_messages;
DROP TABLE IF EXISTS ai_conversations;

COMMIT;
```

---

## SQLModel Entity Definitions

### AIConversation

```python
# backend/src/models/ai_conversation.py
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List, Literal
from datetime import datetime

class AIConversation(SQLModel, table=True):
    __tablename__ = "ai_conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    start_time: datetime = Field(default_factory=datetime.now)
    last_activity_time: datetime = Field(default_factory=datetime.now)
    status: Literal["active", "closed", "timeout"] = Field(default="active")
    context_window: int = Field(default=10, ge=1, le=20)
    topic: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    deleted_at: Optional[datetime] = None

    # Relationships
    messages: List["AIMessage"] = Relationship(back_populates="conversation")
    user: "User" = Relationship(back_populates="ai_conversations")
```

### AIMessage

```python
# backend/src/models/ai_message.py
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, Literal
from datetime import datetime

class AIMessage(SQLModel, table=True):
    __tablename__ = "ai_messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="ai_conversations.id", index=True)
    role: Literal["user", "assistant"] = Field()
    content: str = Field(max_length=10000)
    timestamp: datetime = Field(default_factory=datetime.now)
    token_count: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    conversation: "AIConversation" = Relationship(back_populates="messages")
    parsed_intent: Optional["ParsedTaskIntent"] = Relationship(back_populates="message")
```

### ParsedTaskIntent

```python
# backend/src/models/parsed_task_intent.py
from sqlmodel import Field, SQLModel, Relationship, Column
from sqlalchemy import JSON
from typing import Optional, Dict
from datetime import datetime, date, time

class ParsedTaskIntent(SQLModel, table=True):
    __tablename__ = "parsed_task_intents"

    id: Optional[int] = Field(default=None, primary_key=True)
    message_id: int = Field(foreign_key="ai_messages.id", index=True)
    original_text: str = Field()
    extracted_title: Optional[str] = Field(default=None, max_length=200)
    extracted_priority: Optional[str] = Field(default=None)
    extracted_due_date: Optional[date] = None
    extracted_due_time: Optional[time] = None
    confidence_scores: Dict[str, float] = Field(sa_column=Column(JSON))
    confirmed: bool = Field(default=False)
    task_id: Optional[int] = Field(default=None, foreign_key="tasks.id")
    created_at: datetime = Field(default_factory=datetime.now)
    confirmed_at: Optional[datetime] = None

    # Relationships
    message: "AIMessage" = Relationship(back_populates="parsed_intent")
    task: Optional["Task"] = Relationship()
```

### TaskSummary

```python
# backend/src/models/task_summary.py
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import JSON
from typing import Optional, Dict, Literal
from datetime import datetime, date

class TaskSummary(SQLModel, table=True):
    __tablename__ = "task_summaries"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    period_type: Literal["daily", "weekly", "monthly", "custom"] = Field()
    start_date: date = Field()
    end_date: date = Field()
    metrics: Dict = Field(sa_column=Column(JSON))
    summary_text: str = Field()
    generated_at: datetime = Field(default_factory=datetime.now)
```

### AIInsight

```python
# backend/src/models/ai_insight.py
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import JSON
from typing import Optional, Dict, Literal
from datetime import datetime

class AIInsight(SQLModel, table=True):
    __tablename__ = "ai_insights"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    insight_type: Literal[
        "overdue_pattern", "productivity_trend", "priority_imbalance",
        "completion_streak", "workload_warning", "time_management",
        "recurring_task", "other"
    ] = Field()
    title: str = Field(max_length=200)
    description: str = Field()
    supporting_data: Dict = Field(sa_column=Column(JSON))
    priority: Literal["Low", "Medium", "High"] = Field(default="Medium")
    created_at: datetime = Field(default_factory=datetime.now)
    dismissed_at: Optional[datetime] = None
    dismissed_reason: Optional[str] = None
```

---

## Data Access Patterns

### Common Queries

**Get Active Conversation for User**:
```python
def get_active_conversation(user_id: int) -> Optional[AIConversation]:
    """Get user's active conversation or None"""
    return session.exec(
        select(AIConversation)
        .where(AIConversation.user_id == user_id)
        .where(AIConversation.status == "active")
        .where(AIConversation.deleted_at.is_(None))
    ).first()
```

**Get Recent Messages in Conversation**:
```python
def get_recent_messages(conversation_id: int, limit: int = 10) -> List[AIMessage]:
    """Get last N messages in conversation"""
    return session.exec(
        select(AIMessage)
        .where(AIMessage.conversation_id == conversation_id)
        .order_by(AIMessage.timestamp.desc())
        .limit(limit)
    ).all()[::-1]  # Reverse to chronological order
```

**Get Unconfirmed Parsed Intents**:
```python
def get_pending_intents(user_id: int) -> List[ParsedTaskIntent]:
    """Get intents awaiting user confirmation"""
    return session.exec(
        select(ParsedTaskIntent)
        .join(AIMessage)
        .join(AIConversation)
        .where(AIConversation.user_id == user_id)
        .where(ParsedTaskIntent.confirmed == False)
        .order_by(ParsedTaskIntent.created_at.desc())
    ).all()
```

**Get Active Insights for User**:
```python
def get_active_insights(user_id: int) -> List[AIInsight]:
    """Get non-dismissed insights"""
    return session.exec(
        select(AIInsight)
        .where(AIInsight.user_id == user_id)
        .where(AIInsight.dismissed_at.is_(None))
        .order_by(AIInsight.created_at.desc())
    ).all()
```

---

## Performance Considerations

### Indexing Strategy

**Hot Paths** (most frequent queries):
1. Get active conversation for user → `idx_ai_conversations_user_status`
2. Get messages in conversation → `idx_ai_messages_conversation`
3. Get recent summaries → `idx_task_summaries_user_period`
4. Get active insights → `idx_ai_insights_active`

**Composite Indexes**:
- `(user_id, status)` on ai_conversations (conversation lookup)
- `(conversation_id, timestamp)` on ai_messages (message retrieval)
- `(user_id, period_type, start_date DESC)` on task_summaries (summary history)

**Partial Indexes**:
- `deleted_at IS NULL` on ai_conversations (exclude soft-deleted)
- `dismissed_at IS NULL` on ai_insights (active insights only)
- `task_id IS NOT NULL` on parsed_task_intents (confirmed intents)

### Data Retention

**Conversation Cleanup** (optional background job):
```sql
-- Archive conversations older than 90 days
UPDATE ai_conversations
SET deleted_at = NOW()
WHERE status IN ('closed', 'timeout')
  AND last_activity_time < NOW() - INTERVAL '90 days'
  AND deleted_at IS NULL;
```

**Insight Cleanup** (after 30 days dismissed):
```sql
-- Hard delete dismissed insights after 30 days
DELETE FROM ai_insights
WHERE dismissed_at < NOW() - INTERVAL '30 days';
```

---

## Testing Requirements

### Unit Tests (Model Validation)

```python
# backend/tests/test_models_ai.py
def test_ai_conversation_status_validation():
    """Test status must be active/closed/timeout"""
    with pytest.raises(ValidationError):
        AIConversation(user_id=1, status="invalid")

def test_parsed_intent_confidence_scores():
    """Test confidence scores between 0.0-1.0"""
    with pytest.raises(ValidationError):
        ParsedTaskIntent(
            message_id=1,
            original_text="test",
            confidence_scores={"title": 1.5, "priority": 0.5, "due_date": 0.8}
        )

def test_context_window_bounds():
    """Test context window between 1-20"""
    with pytest.raises(ValidationError):
        AIConversation(user_id=1, context_window=0)
    with pytest.raises(ValidationError):
        AIConversation(user_id=1, context_window=21)
```

### Integration Tests (Data Access)

```python
# backend/tests/test_data_access_ai.py
def test_get_active_conversation(session, test_user):
    """Test retrieving active conversation"""
    conv = AIConversation(user_id=test_user.id, status="active")
    session.add(conv)
    session.commit()

    result = get_active_conversation(test_user.id)
    assert result is not None
    assert result.status == "active"

def test_message_ordering(session, test_conversation):
    """Test messages returned in chronological order"""
    msg1 = AIMessage(conversation_id=test_conversation.id, role="user", content="First")
    msg2 = AIMessage(conversation_id=test_conversation.id, role="assistant", content="Second")
    session.add_all([msg1, msg2])
    session.commit()

    messages = get_recent_messages(test_conversation.id, limit=10)
    assert messages[0].content == "First"
    assert messages[1].content == "Second"
```

---

## Summary

**Entities Created**: 6 new tables (ai_conversations, ai_messages, parsed_task_intents, task_summaries, ai_insights, user_contexts)

**Phase 2 Integration**: Zero modifications to existing tables; AI entities reference users and tasks via foreign keys

**Storage Strategy**: Hybrid (active contexts in-memory, conversations/summaries/insights in PostgreSQL)

**Performance**: Optimized indexes for hot paths, partial indexes for filtered queries

**Validation**: All functional requirements from spec.md enforced via constraints and model validation

**Ready for**: API contract definition (next phase)
