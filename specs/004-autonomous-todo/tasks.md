# Tasks: Phase 4 — Autonomous & Proactive Todo System

**Input**: Design documents from `/specs/004-autonomous-todo/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Tests are included as explicit verification steps for each autonomous behavior.

**Organization**: Tasks are structured by milestones from the plan, with clear agent ownership for each task.

## Autonomy Levels Definition (Reference)
- **Low**: Suggestion only (UI notification)
- **Medium**: Draft/Schedule actions (requires confirmation)
- **High**: Execute actions (notify after)

---

## Phase 1: Shared Infrastructure (Milestone 1)

**Purpose**: Database schema, API endpoints, and logging foundation.

- [ ] T001 [Observability Agent] Create `user_preferences` model in `backend/src/models/preferences.py` and migration
- [ ] T002 [Observability Agent] Create `ai_activity_log` model in `backend/src/models/activity.py` and migration
- [ ] T003 [Consent Agent] Implement `GET /monitor/settings` and `PUT /monitor/settings` in `backend/src/routers/monitor.py`
- [ ] T004 [Observability Agent] Implement `GET /monitor/logs` in `backend/src/routers/monitor.py`
- [ ] T005 [Safety Agent] Implement `LogService` in `backend/src/services/logger.py` to write structured audit logs

**Checkpoint**: Database tables created, settings API active, logging service ready.

---

## Phase 2: Reasoning & Detection Logic (Milestone 2)

**Purpose**: Backend logic to detect patterns and generate suggestions.

- [ ] T006 [Trigger Agent] Implement `DeadlineDetector` in `backend/src/services/triggers/deadline.py`
- [ ] T007 [Trigger Agent] Implement `PatternDetector` (heuristic + basic learning) in `backend/src/services/triggers/pattern.py`
- [ ] T008 [Reasoning Agent] Implement `SuggestionEngine` in `backend/src/services/suggestion.py` (combines triggers)
- [ ] T009 [Reasoning Agent] Create `POST /ai/analyze` endpoint in `backend/src/routers/ai.py` that invokes SuggestionEngine
- [ ] T010 [Safety Agent] Implement `ActionValidator` in `backend/src/services/safety.py` to check `user_preferences` before suggesting

**Checkpoint**: Backend can ingest current state and output a list of valid `Suggestion` objects.

---

## Phase 3: Client-Side Orchestration (Milestone 3)

**Purpose**: Frontend "brain" that drives the autonomy loop.

- [ ] T011 [Orchestrator Agent] Create `AutonomyContext` in `frontend/src/context/AutonomyContext.tsx`
- [ ] T012 [Orchestrator Agent] Implement `useAutonomy` hook with periodic polling logic (useEffect)
- [ ] T013 [Consent Agent] Create `AutonomySettings` UI component in `frontend/src/components/settings/AutonomySettings.tsx`
- [ ] T014 [Orchestrator Agent] Connect `useAutonomy` to `POST /ai/analyze` and local state management

**Checkpoint**: Frontend regularly polls backend when active; Settings UI allows toggling autonomy levels.

---

## Phase 4: UI Integration (Milestone 4)

**Purpose**: Visible surface for AI actions.

- [ ] T015 [UI Agent] Create `SuggestionPanel` component in `frontend/src/components/ai/SuggestionPanel.tsx`
- [ ] T016 [UI Agent] Create `NotificationManager` integration in `frontend/src/components/ui/Toast.tsx` for proactive alerts
- [ ] T017 [UI Agent] Implement `Accept/Reject` handlers in `frontend/src/services/aiActions.ts`
- [ ] T018 [Observability Agent] Create `ActivityLogView` component in `frontend/src/components/settings/ActivityLogView.tsx`

**Checkpoint**: Users see suggestions, can accept/reject them, and view history.

---

## Phase 5: End-to-End Validation

**Purpose**: Verify the autonomous loop works as intended without regression.

- [ ] T019 [QA Agent] Verify "Low Autonomy" generates suggestions but takes no action
- [ ] T020 [QA Agent] Verify "Deadline Risk" triggers proactive notification
- [ ] T021 [QA Agent] Verify `ai_activity_log` records reasoning for all generated suggestions
- [ ] T022 [QA Agent] Verify Phase 3 manual AI chat still functions correctly
- [ ] T023 [Observability Agent] Implement `EngagementMetrics` tracking in `backend/src/services/analytics.py` to measure suggestion acceptance rate

**Checkpoint**: Feature complete and validated.
