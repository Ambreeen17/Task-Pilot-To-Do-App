# Agent 2: Consent & Control Agent

**Responsibility**: Learning opt-in/out flows, pause/resume learning, reset learning state

**Priority**: P0 (Foundation - Required for GDPR/CCPA compliance)

---

## Task 2.1: Implement Opt-In Consent Flow

**Description**: Create user consent flow for learning with clear privacy disclosure

**Acceptance Criteria**:
- [ ] Design privacy disclosure modal with:
  - What is learned (timing, frequency, grouping)
  - What is NOT learned (content, categories, PII)
  - How data is used (personalization only)
  - Data retention (kept until reset)
  - Right to delete (one-click reset)
- [ ] Implement consent timestamp tracking
- [ ] Add POST /api/learning/enable endpoint
- [ ] Store consent in UserPreferences.learning_enabled
- [ ] Log consent event to audit trail

**Files**:
- `frontend/src/components/LearningConsentModal.tsx` (new)
- `frontend/src/hooks/useLearning.ts` (new)
- `backend/src/routers/learning.py` (new)
- `backend/src/models/preferences.py` (extend)

**Dependencies**: Task 1.1 (Learning Policy)

**Estimated Effort**: 8 hours

---

## Task 2.2: Implement Opt-Out Flow

**Description**: Allow users to opt-out of learning while preserving historical data

**Acceptance Criteria**:
- [ ] Add toggle UI in settings page
- [ ] Implement POST /api/learning/disable endpoint
- [ ] Set learning_enabled=false (keeps data)
- [ ] Stop collecting new behavioral events
- [ ] Display "Learning Paused" status in UI
- [ ] Log opt-out event to audit trail

**Files**:
- `frontend/src/components/LearningSettings.tsx` (new)
- `backend/src/routers/learning.py` (extend)
- `backend/src/services/learning_service.py` (new)

**Dependencies**: Task 2.1

**Estimated Effort**: 4 hours

---

## Task 2.3: Implement Pause/Resume Learning

**Description**: Allow temporary pausing without changing opt-in status

**Acceptance Criteria**:
- [ ] Add "Pause Learning" button with tooltip
- [ ] Implement temporary pause state (different from opt-out)
- [ ] Add pause_until timestamp field
- [ ] Auto-resume after specified duration or manual resume
- [ ] Show "Paused until [date]" indicator
- [ ] Log pause/resume events

**Files**:
- `frontend/src/components/LearningControlPanel.tsx` (new)
- `backend/src/models/preferences.py` (extend - add pause_until)
- `backend/src/routers/learning.py` (extend - POST /api/learning/pause, /api/learning/resume)

**Dependencies**: Task 2.2

**Estimated Effort**: 5 hours

---

## Task 2.4: Implement Learning Category Selection

**Description**: Granular control over what types of patterns to learn

**Acceptance Criteria**:
- [ ] Add category checkboxes in settings:
  - ☐ Timing patterns (when I work)
  - ☐ Priority patterns (how I prioritize)
  - ☐ Grouping patterns (how I batch tasks)
- [ ] Store selections in UserPreferences.learning_categories (JSON array)
- [ ] Filter behavioral events by enabled categories
- [ ] Update PUT /api/learning/settings endpoint
- [ ] Show category-specific pattern counts

**Files**:
- `frontend/src/components/LearningCategorySelector.tsx` (new)
- `backend/src/routers/learning.py` (extend)
- `backend/src/services/event_collector.py` (new)

**Dependencies**: Task 2.1

**Estimated Effort**: 6 hours

---

## Task 2.5: Implement Complete Learning Reset

**Description**: One-click deletion of all learning data (GDPR Article 17 compliance)

**Acceptance Criteria**:
- [ ] Add "Reset Learning Data" button with danger styling
- [ ] Show confirmation modal: "This cannot be undone. Delete X events and Y patterns?"
- [ ] Implement DELETE /api/learning/reset endpoint
- [ ] Delete all BehavioralEvent records for user
- [ ] Delete UserBehaviorProfile record
- [ ] Delete all AdaptiveSuggestion records
- [ ] Log deletion event (but not deleted data)
- [ ] Show success message: "Learning data deleted"
- [ ] Reset UI to initial state

**Files**:
- `frontend/src/components/ResetLearningButton.tsx` (new)
- `backend/src/routers/learning.py` (extend)
- `backend/src/services/learning_service.py` (extend)
- `backend/tests/test_learning_reset.py` (new)

**Dependencies**: Task 2.1

**Estimated Effort**: 7 hours

---

## Task 2.6: Implement Learning Status Indicator

**Description**: Always-visible indicator showing current learning state

**Acceptance Criteria**:
- [ ] Add status badge/pill in app header or sidebar:
  - 🟢 "Learning Active" (enabled, not paused)
  - 🟡 "Learning Paused" (paused temporarily)
  - ⚫ "Learning Disabled" (opted out)
  - 🔴 "Not Enrolled" (never opted in)
- [ ] Clicking badge opens LearningSettings modal
- [ ] Show data points collected count
- [ ] Add tooltip with last update timestamp

**Files**:
- `frontend/src/components/LearningStatusIndicator.tsx` (new)
- `frontend/src/layouts/AppLayout.tsx` (extend)

**Dependencies**: Tasks 2.1, 2.2, 2.3

**Estimated Effort**: 4 hours

---

## Task 2.7: Implement Data Export (GDPR Article 15)

**Description**: Allow users to export all their learning data

**Acceptance Criteria**:
- [ ] Add "Export My Data" button in settings
- [ ] Implement GET /api/learning/export endpoint
- [ ] Generate JSON file containing:
  - All BehavioralEvent records
  - UserBehaviorProfile patterns
  - AdaptiveSuggestion history
  - Consent timestamps
- [ ] Format as human-readable JSON with comments
- [ ] Trigger browser download
- [ ] Log export event to audit trail

**Files**:
- `frontend/src/components/ExportDataButton.tsx` (new)
- `backend/src/routers/learning.py` (extend)
- `backend/src/services/data_export.py` (new)

**Dependencies**: Task 2.1

**Estimated Effort**: 5 hours

---

**Total Agent Effort**: 39 hours
