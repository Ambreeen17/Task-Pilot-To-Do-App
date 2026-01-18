-- Migration: Add full_name column to users table
-- Date: 2026-01-18
-- Feature: User profile enhancement for signup
-- Database: PostgreSQL (Render)

BEGIN;

-- Add full_name column to users table
-- Using empty string as default for existing users
ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR(255) NOT NULL DEFAULT '';

-- Update existing users to have a placeholder name based on email (PostgreSQL)
UPDATE users SET full_name = SPLIT_PART(email, '@', 1) WHERE full_name = '';

COMMIT;
