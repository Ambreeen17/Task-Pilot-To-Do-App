-- Rollback: Remove language column from ai_conversations table
-- Date: 2026-02-16
-- Feature: Multi-language chatbot support (English/Urdu)
-- Database: PostgreSQL (Render)

BEGIN;

-- Drop language column from ai_conversations table
ALTER TABLE ai_conversations DROP COLUMN IF EXISTS language;

COMMIT;
