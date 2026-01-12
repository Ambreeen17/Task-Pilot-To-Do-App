# Implementation Plan - Phase 4: Autonomous & Proactive Todo System

**Feature Branch**: `004-autonomous-todo`
**Status**: DRAFT
**Specification**: `specs/004-autonomous-todo/spec.md`

## 1. Technical Context

Phase 4 extends the Phase 3 (AI-Assisted) React + Python architecture to include autonomous client-side monitoring and proactive notifications.

| Aspect | Current State (Phase 3) | Phase 4 Requirement |
|:---|:---|:---|
| **Execution Model** | Reactive (User acts → AI responds) | Proactive (System acts → User notified) |
| **Logic Location** | Server-side `/ai/parse` endpoint | **Hybrid**: Client-side monitoring + Server-side AI logic |
| **Evaluation Loop** | N/A | **Client-Side Trigger** (useEffect / Service Worker) |
| **User Control** | Manual commands | **Granular Autonomy Levels** (Low/Med/High) |
| **Notifications** | Toast (Feedback only) | **Proactive Toasts & Suggestion Panels** |

### Data Model Changes

**New Tables/Entities (`data-model.md`):**
1.  **user_preferences**: Stores `autonomy_level` (Low/Med/High), `work_hours`, `enabled_categories`.
2.  **ai_activity_log**: Audit trail for all autonomous actions (`action_type`, `reason`, `status`, `timestamp`).
3.  **pattern_detection**: Cache for detected user habits/patterns.

### Architecture Components

1.  **Autonomy Orchestrator (Client-Side)**:
    -   React Context/Hook (`useAutonomy`) that runs periodic checks.
    -   Triggers evaluation only when user is active (on focus/mount).
    -   Communicates with backend AI endpoints.

2.  **Consent & Policy Engine**:
    -   Enforces `autonomy_level` constraints before any action.
    -   Blocks action execution if consent is missing.

3.  **Proactive UI Layer**:
    -   `SuggestionPanel`: Displays AI proposals (rescheduling, new tasks).
    -   `NotificationManager`: Handles "Heads up" toasts.

## 2. Agent-Based Decomposition

| Agent | Responsibility | Phase 4 Specifics |
|:---|:---|:---|
| **Autonomy Orchestrator** | Coordination | Manages the `useEffect` loop, calls API, manages state. |
| **Consent & Policy** | Safety | Checks `user_preferences`. Blocks unauthorized actions. |
| **Reasoning Agent** | Logic (Backend) | Extends `ai_service` to analyze patterns and generate suggestions. |
| **Trigger Agent** | Detection | Identifies "Deadline Risks" or "Pattern Matches" from task list. |
| **UI Interaction** | Presentation | Renders `SuggestionPanel` and Proactive Toasts. |
| **Observability** | Audit | Writes to `ai_activity_log` for explainability. |

## 3. Milestones & Execution Plan

### Milestone 1: Foundation & Data Model
**Goal**: Establish database schema and backend endpoints for autonomy settings and logs.
- [ ] Create `user_preferences` table (SQLModel).
- [ ] Create `ai_activity_log` table.
- [ ] Create API endpoints: `GET/PUT /monitor/settings`, `GET /monitor/logs`.
- [ ] **Rollback**: Drop tables, remove endpoints.

### Milestone 2: Backend Reasoning Logic
**Goal**: Enable AI to analyze tasks and generate structured suggestions (without executing them).
- [ ] Create `POST /ai/analyze` endpoint.
- [ ] Implement `PatternDetection` logic (using LLM or heuristic).
- [ ] Implement `DeadlineRisk` detection logic.
- [ ] **Rollback**: Revert backend code changes.

### Milestone 3: Client-Side Orchestrator
**Goal**: Implement the client-side "brain" that wakes up and checks for things to do.
- [ ] Create `AutonomyContext` and `useAutonomy` hook.
- [ ] Implement the "Evaluation Loop" (triggers API analysis on interval/focus).
- [ ] Connect `AutonomySettings` UI to backend.
- [ ] **Rollback**: Disable hook, revert frontend changes.

### Milestone 4: UI integration & Proactive Notifications
**Goal**: Expose the AI's thoughts to the user via UI.
- [ ] Implement `SuggestionPanel` component (AnimatePresence, Dismissible).
- [ ] Integrate with `Toast` system for deadline warnings.
- [ ] Connect Accept/Reject actions to backend execution.
- [ ] **Rollback**: Remove UI components.

## 4. Safety-First Execution Order

1.  **Guardrails First**: Implement the `Consent & Policy` checks before any autonomous logic.
2.  **Logs Second**: Ensure `ai_activity_log` works so every test action is recorded.
3.  **Suggestions Third**: Implementation suggestion-only mode (Low Autonomy).
4.  **Action Execution Last**: Only enable "Medium/High" autonomy execution paths after suggestions are verified.

## 5. Risk Mitigation

| Risk | Mitigation |
|:---|:---|
| **Annoying Spam** | Rate limit proactive notifications (e.g., 1 per session/hour). |
| **Destructive Acts** | Hard-block DELETE actions in autonomous mode. |
| **Hallucination** | Validate all Task IDs against DB before suggesting changes. |
| **Performance** | Run evaluation loop only on client idle/focus, debounce API calls. |

## 6. Constitution Check

- **Non-Destructive**: Phase 1-3 features remain untouched. Phase 4 is additive.
- **User Control**: Explicit "Autonomy Level" settings required (FR-001).
- **Explainability**: "Reasoning" field required for all actions (FR-006).
- **Safety**: Phase 3 Prompt Injection layer reused (SPR-001).

**Validation**: Proceed to Implementation.
