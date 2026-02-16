-- Migration: Add language column to ai_conversations table
-- Date: 2026-02-16
-- Feature: Multi-language chatbot support (English/Urdu)
-- Database: PostgreSQL (Render)

BEGIN;

-- Add language column to ai_conversations table
-- Default to 'en' for existing conversations
ALTER TABLE ai_conversations ADD COLUMN IF NOT EXISTS language VARCHAR(10) NOT NULL DEFAULT 'en';

COMMIT;
