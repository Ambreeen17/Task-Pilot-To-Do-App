# Feature Specification: Phase 4 — Autonomous & Proactive Todo System

**Feature Branch**: `004-autonomous-todo`
**Created**: 2026-01-11
**Status**: Draft
**Input**: User description for Phase 4 autonomous features

## Clarifications
### Session 2026-01-11
- Q: How granular should Autonomy Levels be? → A: **Explicit Levels** (Option A). Hardcoded Low (Suggestions only), Medium (Non-destructive autoscheduling), High (Full autonomy).
- Q: Where does the background evaluation loop run? → A: **Client-Side Trigger** (Option A). Logic runs in browser when user is active to minimize server cost and complexity.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Proactive Task Reminders (Priority: P1)

The system autonomously monitors upcoming deadlines and risk patterns, proactively notifying the user about critical tasks without explicit queries.

**Why this priority**: Core value proposition of Phase 4—shifting from reactive tool to proactive assistant. High user value in preventing missed deadlines.

**Independent Test**: Can be effectively tested by creating tasks with near-future deadlines and verifying the system triggers notifications without user interaction.

**Acceptance Scenarios**:
1. **Given** a high-priority task due in 2 hours, **When** no activity is detected on it, **Then** the system sends a proactive notification: "Heads up: 'Client Presentation' is due in 2 hours."
2. **Given** multiple tasks due today, **When** the user logs in, **Then** the AI suggests a prioritized focus list: "Good morning! You have 3 critical tasks today. Suggest starting with 'Bug Fix #123'."
3. **Given** a proactive notification, **When** the user ignores it, **Then** the system does not spam but may escalate only if critical (based on settings).

### User Story 2 - User Consent & Autonomy Control (Priority: P1)

Users must have granular control over the AI's autonomy levels, ensuring trust and preventing unwanted actions.

**Why this priority**: Essential for safety, trust, and adoption. Users must feel in control of an autonomous agent.

**Independent Test**: Verify that disabling autonomy stops all proactive actions, and setting logic (Low/High) changes behavior frequency/boldness.

**Acceptance Scenarios**:
1. **Given** the Autonomy Settings panel, **When** user selects "Low Autonomy", **Then** AI only makes suggestions but takes no actions.
2. **Given** "Medium Autonomy", **When** AI identifies a pattern (e.g., weekly report), **Then** it asks for permission: "I noticed you create this weekly. Shall I schedule it automatically?"
3. **Given** a proposed autonomous action, **When** user rejects it, **Then** the AI learns and does not repeat that specific action type immediately.

### User Story 3 - Smart Rescheduling Suggestions (Priority: P2)

The AI detects schedule conflicts or missed tasks and suggests optimized recovery plans.

**Why this priority**: Adds significant intelligence and recovery capability, reducing user stress from "task debt".

**Independent Test**: Create a scenario with overlapping tasks or overdue items and verify AI generates a sensible rescheduling plan.

**Acceptance Scenarios**:
1. **Given** 3 overdue tasks from yesterday, **When** a new day starts, **Then** AI suggests: "You missed 3 tasks. Move them to today or Friday?"
2. **Given** a new high-priority task inserted into a full day, **When** schedule is tight, **Then** AI suggests: "You seem overbooked. Should we move 'Low Priority Research' to tomorrow?"

### User Story 4 - Habit & Pattern Detection (Priority: P3)

The system learns from user behavior to automate repetitive tasks or suggest optimizations.

**Why this priority**: Long-term value multiplier. Makes the system "smarter" over time but not critical for Day 1 autonomy.

**Independent Test**: Simulate a repetitive action (e.g., adding "Team Sync" every Monday) and checking if AI suggests automating it after N occurrences.

**Acceptance Scenarios**:
1. **Given** user creates "Gym" task every Monday 3 weeks in a row, **When** 4th Monday approaches, **Then** AI suggests: "Create recurring 'Gym' task for Mondays?"
2. **Given** user consistently completes "Reading" tasks in the evening, **When** a "Reading" task is scheduled for morning, **Then** AI warns: "You usually do reading at night. Move this to 8 PM?"

### Edge Cases
- **Permission Conflict**: User enables autonomy but system lacks required permissions (e.g., no valid LLM token). System should gracefully fallback to manual mode with a warning.
- **Conflicting Rules**: One rule says "Remind 1 hr before" and another "Do not disturb". Safety rules (Do Not Disturb) must override proactive actions.
- **Hallucination Risk**: AI suggests rescheduling a task that doesn't exist. Prevention: Strict validation against DB before making any suggestion.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide an **Autonomy Settings** interface with 3 explicit levels:
    - **Low**: Suggestions only (no auto-actions).
    - **Medium**: Non-destructive actions (e.g., autoschedule empty slots) allow with verification.
    - **High**: Full autonomy (including create/reschedule) with post-action notification.
- **FR-002**: System MUST run a **Client-Side** background evaluation loop (e.g., via `useEffect` or Service Worker) to analyze tasks while the app is active.
- **FR-003**: System MUST identify **Deadline Risks** (tasks due soon, overdue tasks).
- **FR-004**: System MUST generate **Proactive Notifications** for identified risks or opportunities.
- **FR-005**: All autonomous actions MUST require **User Consent** based on the configured autonomy level (e.g., explicit approval for High impact).
- **FR-006**: System MUST explain the **Reasoning** for every suggestion ("Why did you suggest this?").
- **FR-007**: System MUST detect **Patterns** in task creation/completion (recurring text, times).
- **FR-008**: System MUST support **Accept/Reject** workflows for AI suggestions.
- **FR-009**: System MUST enforce **Safety Constraints** (no deletion without confirmation, no cross-user data).
- **FR-010**: System MUST maintain an **Activity Log** of all AI-initiated suggestions and actions.

### Key Entities

- **AutonomousAction**: Represents a potential action (Type: Reminder|Reschedule|Create, TargetTaskId, Reason, Confidence, Status: Pending|Approved|Rejected).
- **AutonomyProfile**: User-specific settings (Level: Low/Med/High, EnabledCategories, WorkHours).
- **PatternSuggestion**: Detected habit (PatternType, suggestedAction, frequency).

## Security & Privacy Requirements

- **SPR-001**: **No Prompt Injection**: Re-use Phase 3 validation layer for all AI inputs/outputs.
- **SPR-002**: **User Isolation**: The background evaluator must strictly query only the current user's tasks.
- **SPR-003**: **Action Verification**: Every write action (Create/Update/Delete) generated by AI must trigger a secondary validation check before execution/suggestion.
- **SPR-004**: **Explicit Opt-In**: Autonomous features default to OFF until user enables them.

## Success Criteria

1. **Engagement**: Users accept >40% of AI suggestions (indicating relevance).
2. **Reliability**: Zero destructive actions executed without explicit user confirmation.
3. **Performance**: Background evaluation impact on API latency remains <10% overhead.
4. **Safety**: 100% of autonomous actions are logged with "Reasoning" and "Timestamp".

## Assumptions
- Phase 3 "AI Parse" API is reusable for interpreting pattern data.
- User is logged in; notifications are handled via in-app UI (Toast/Panel) for this phase (Push notifications OOS for purely web scope unless PWA specified).
- "Background Loop" implies a trigger mechanism (e.g., on page load/refresh or periodic polling while app is open), not necessarily a server-side cron job if implementation is client-driven for Phase 4 (to be decided in Plan, but assuming Client-Side Polling or Next.js API cron for simplicity). *Current assumption: Client-side polling or "On Interaction" check to keep architecture simple.*
