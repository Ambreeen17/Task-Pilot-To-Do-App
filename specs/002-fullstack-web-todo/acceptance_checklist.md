# Acceptance Checklist — Phase 2 Full Stack Web Todo

**Feature**: `002-fullstack-web-todo`
**Date**: 2026-01-07

## Scope & Success Criteria

- [x] Backend API exists and is test-covered (FastAPI + SQLModel)
- [x] Frontend app exists (Next.js App Router)
- [x] Frontend ↔ backend integration exists (JWT + task CRUD)
- [x] Automated tests pass (backend unit/integration + frontend E2E smoke)

## Functional Acceptance

### Auth
- [x] Register new user with email + password (min 8 chars)
- [x] Duplicate registration returns 409
- [x] Login returns a JWT bearer token
- [x] Unauthenticated access to `/tasks` endpoints returns 401

### Tasks
- [x] Create task with title + optional description
- [x] List tasks returns only the current user's tasks
- [x] Get task is owner-scoped
- [x] Update task (PUT)
- [x] Toggle completion (PATCH /tasks/{id}/toggle)
- [x] Delete task (204)
- [x] Search by title/description query param `search`
- [x] Filter by `status` and `priority`

### UI
- [x] Landing page links to login/signup
- [x] Login page form validation + error toast
- [x] Signup page form validation + error toast
- [x] Tasks page: search + status/priority filters
- [x] Tasks page: create task + list + toggle + delete
- [x] Tasks page: signed-out state prompts user to login

## Non-Functional Acceptance

- [ ] Uses PostgreSQL in local dev (currently defaulting to SQLite unless `DATABASE_URL` set)
- [ ] Password hashing uses bcrypt (current implementation uses `pbkdf2_sha256` due to bcrypt backend issues)
- [x] All timestamps are timezone-aware UTC (backend uses `datetime.now(timezone.utc)`)

## Automated Test Evidence

### Backend
- [x] `python -m pytest backend/tests -q` → `12 passed, 1 skipped`

### Frontend
- [x] `npm run lint --prefix frontend` → pass
- [x] `npm run build --prefix frontend` → pass
- [x] `npm run test:e2e --prefix frontend` → `2 passed`

## Manual Smoke Test

- [ ] Start backend: `uvicorn backend.src.main:app --reload --port 8000`
- [ ] Start frontend: `npm run dev --prefix frontend`
- [ ] Create user, login, create a task, toggle it, delete it

## Known Risks / Follow-ups

- Current password hashing scheme differs from spec (`bcrypt` vs `pbkdf2_sha256`).
- Backend uses SQLite fallback; production PostgreSQL connection not exercised.
- `datetime.utcnow()` deprecations: should migrate to timezone-aware UTC timestamps.
