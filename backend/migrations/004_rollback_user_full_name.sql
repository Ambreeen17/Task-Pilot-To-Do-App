-- Rollback: Remove full_name column from users table
-- Date: 2026-01-18

BEGIN;

ALTER TABLE users DROP COLUMN IF EXISTS full_name;

COMMIT;
