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
