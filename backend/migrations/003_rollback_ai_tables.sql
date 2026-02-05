-- Rollback: Remove Phase 3 AI tables
-- Date: 2026-01-10
-- Feature: 003-ai-assisted-todo

BEGIN;

DROP TABLE IF EXISTS user_contexts;
DROP TABLE IF EXISTS ai_insights;
DROP TABLE IF EXISTS task_summaries;
DROP TABLE IF EXISTS parsed_task_intents;
DROP TABLE IF EXISTS ai_messages;
DROP TABLE IF EXISTS ai_conversations;

COMMIT;
