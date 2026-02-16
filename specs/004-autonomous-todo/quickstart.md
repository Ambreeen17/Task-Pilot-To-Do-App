# Quickstart - Phase 4

## Prerequisites
- Phase 3 environment running (Backend + Frontend)
- OpenAI/Claude API Key active

## Setup

1. **Update Database**:
   ```bash
   alembic upgrade head
   # Or reset DB if in dev: rm test.db && python init_db.py
   ```

2. **Environment Variables**:
   Add to `.env` (backend):
   ```
   # No new keys required if reusing Phase 3 LLM key
   # Optional:
   LOG_LEVEL_AUTONOMY=DEBUG
   ```

3. **Frontend**:
   No new env vars required.

## Verifying Installation

1. Start backend: `uvicorn src.main:app --reload`
2. Start frontend: `npm run dev`
3. Navigate to Settings page (new Autonomy tab should appear)
4. Check browser console for `[AutonomyOrchestrator] Evaluation loop started`
