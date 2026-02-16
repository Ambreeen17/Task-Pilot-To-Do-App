# Phase 5: Adaptive Intelligence - Implementation Tasks

**Feature**: 005-adaptive-intelligence
**Branch**: `005-adaptive-intelligence`
**Status**: Ready for Implementation
**Total Effort**: 321 hours (~8 weeks)

---

## Implementation Rules

**CRITICAL REQUIREMENTS**:
- ✅ Learning OFF by default (LEARNING_ENABLED=false)
- ✅ No silent behavior change
- ✅ Every adaptation must be explainable
- ✅ User can reset system to Phase-3 behavior
- ✅ Full user control at all times

**Feature Flags**:
```python
LEARNING_ENABLED = False  # Default: Learning disabled
```

**Testing Requirements**:
- Learning on/off tests
- Reset tests
- Regression tests for Phase 1-4

---

## Implementation Order (BLOCKING)

Tasks MUST be completed in this order:

1. **Learning Safety & Boundaries** (Agent 1) - BLOCKING
2. **Consent & Controls** (Agent 2) - BLOCKING
3. **Learning Signal Capture** (Agent 3, Tasks 3.1-3.2)
4. **Behavior Modeling** (Agent 3, Tasks 3.3-3.7)
5. **Adaptive Logic** (Agent 4)
6. **Explanation Engine** (Agent 5)
7. **Insights & Reports** (Agent 6)
8. **Reset & Rollback** (Agent 7)

---

## Phase 1: Learning Safety & Boundaries (BLOCKING)

**Agent**: 1 (Learning Policy Agent)
**Effort**: 25 hours
**Priority**: P0 - Must complete before ANY other work

### Task 1.1: Define Learnable Signal Specification

**Status**: [ ]
**Effort**: 4 hours
**Dependencies**: None

**Acceptance Criteria**:
- [ ] Document approved learnable signals:
  - ✅ `hour_of_day` (0-23)
  - ✅ `day_of_week` (0-6, Monday=0)
  - ✅ `task_type_hash` (one-way SHA-256 hash)
  - ✅ `session_id` (grouping identifier)
  - ✅ `priority_change_event` (from→to transitions)
  - ✅ `task_completion_event` (timing only)
- [ ] Create validation schema for learnable signals
- [ ] Add signal type enumeration in backend
- [ ] Write unit tests for signal validation

**Files**:
- `backend/src/learning/signal_policy.py` (new)
- `backend/src/learning/schemas.py` (new)
- `backend/tests/test_signal_policy.py` (new)

---

### Task 1.2: Define Forbidden Signal Policy

**Status**: [ ]
**Effort**: 6 hours
**Dependencies**: Task 1.1

**Acceptance Criteria**:
- [ ] Document forbidden signals with rationale:
  - ❌ `task.title` - Contains sensitive content
  - ❌ `task.description` - Contains sensitive content
  - ❌ `task.category` - User-defined, may contain PII
  - ❌ `task.tags` - User-defined, may contain PII
  - ❌ `task.notes` - Contains sensitive content
  - ❌ `user.name` - PII
  - ❌ `user.email` - PII
- [ ] Implement validation layer that rejects forbidden signals
- [ ] Add automated tests that verify forbidden signal rejection
- [ ] Create privacy validation gate in CI/CD pipeline

**Files**:
- `backend/src/learning/signal_policy.py` (extend)
- `backend/tests/test_privacy_validation.py` (new)
- `.github/workflows/privacy-check.yml` (new)

---

### Task 1.3: Implement Signal Decay Rules

**Status**: [ ]
**Effort**: 5 hours
**Dependencies**: Task 1.1

**Acceptance Criteria**:
- [ ] Define decay formula: `weight = base_weight * e^(-λ * days_old)`
  - Recent events (0-30 days): weight = 1.0
  - Medium age (31-60 days): weight = 0.7
  - Old events (61-90 days): weight = 0.4
  - Very old (>90 days): weight = 0.2
- [ ] Implement decay calculation in pattern analysis
- [ ] Add decay_factor field to UserBehaviorProfile model
- [ ] Test decay with synthetic time-series data

**Files**:
- `backend/src/learning/decay.py` (new)
- `backend/src/learning/pattern_analyzer.py` (new)
- `backend/tests/test_decay.py` (new)

---

### Task 1.4: Implement Forgetting Rules

**Status**: [ ]
**Effort**: 6 hours
**Dependencies**: Task 1.3

**Acceptance Criteria**:
- [ ] Implement automatic forgetting triggers:
  - Pattern drift detected (>25% statistical divergence)
  - Suggestion rejection rate >50% for pattern type
  - No supporting events in last 90 days
  - User explicitly requests pattern refresh
- [ ] Add pattern_staleness_score calculation
- [ ] Implement auto-cleanup job for forgotten patterns
- [ ] Log all forgetting events to audit trail

**Files**:
- `backend/src/learning/forgetting.py` (new)
- `backend/src/learning/pattern_analyzer.py` (extend)
- `backend/src/jobs/pattern_cleanup.py` (new)
- `backend/tests/test_forgetting.py` (new)

---

### Task 1.5: Create Learning Policy Documentation

**Status**: [ ]
**Effort**: 4 hours
**Dependencies**: Tasks 1.1, 1.2, 1.3, 1.4

**Acceptance Criteria**:
- [ ] Create user-facing privacy policy document
- [ ] Create developer learning policy reference
- [ ] Document signal approval process for future additions
- [ ] Add policy version number and changelog

**Files**:
- `docs/learning-policy.md` (new)
- `docs/developer-learning-guide.md` (new)
- `PRIVACY.md` (new, user-facing)

---

## Phase 2: Consent & Controls (BLOCKING)

**Agent**: 2 (Consent & Control Agent)
**Effort**: 39 hours
**Priority**: P0 - GDPR/CCPA Compliance Required

### Task 2.1: Implement Opt-In Consent Flow

**Status**: [ ]
**Effort**: 8 hours
**Dependencies**: Task 1.1

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

---

### Task 2.2: Implement Opt-Out Flow

**Status**: [ ]
**Effort**: 4 hours
**Dependencies**: Task 2.1

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

---

### Task 2.3: Implement Pause/Resume Learning

**Status**: [ ]
**Effort**: 5 hours
**Dependencies**: Task 2.2

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

---

### Task 2.4: Implement Learning Category Selection

**Status**: [ ]
**Effort**: 6 hours
**Dependencies**: Task 2.1

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

---

### Task 2.5: Implement Complete Learning Reset

**Status**: [ ]
**Effort**: 7 hours
**Dependencies**: Task 2.1

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

---

### Task 2.6: Implement Learning Status Indicator

**Status**: [ ]
**Effort**: 4 hours
**Dependencies**: Tasks 2.1, 2.2, 2.3

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

---

### Task 2.7: Implement Data Export (GDPR Article 15)

**Status**: [ ]
**Effort**: 5 hours
**Dependencies**: Task 2.1

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

---

## Phase 3: Learning Signal Capture

**Agent**: 3 (Behavior Modeling Agent - Part 1)
**Effort**: 14 hours
**Priority**: P1

### Task 3.1: Implement Behavioral Event Capture

**Status**: [ ]
**Effort**: 8 hours
**Dependencies**: Tasks 1.1, 2.1

**Acceptance Criteria**:
- [ ] Create `useBehavioralTracking` React hook
- [ ] Implement event capture for:
  - Task completion: `{event_type: "task_completed", hour_of_day, day_of_week, task_type_hash}`
  - Priority change: `{event_type: "priority_changed", hour_of_day, from_priority, to_priority, task_type_hash}`
  - Task grouping: `{event_type: "task_grouped", session_id, task_type_hashes[]}`
- [ ] Add privacy validation: NEVER send task content
- [ ] Implement client-side hashing for task_type_hash
- [ ] Add event batching (send max every 30s)
- [ ] Only capture if learning_enabled=true

**Files**:
- `frontend/src/hooks/useBehavioralTracking.ts` (new)
- `frontend/src/services/learningApi.ts` (new)
- `frontend/src/utils/privacyHash.ts` (new)

---

### Task 3.2: Implement Behavioral Event Storage

**Status**: [ ]
**Effort**: 6 hours
**Dependencies**: Task 3.1

**Acceptance Criteria**:
- [ ] Create BehavioralEvent SQLModel
- [ ] Implement POST /api/learning/events endpoint
- [ ] Validate incoming events against signal policy
- [ ] Reject events with forbidden signals
- [ ] Store events with user_id, timestamp
- [ ] Add database indexes on user_id, timestamp, event_type
- [ ] Rate limit: max 100 events/user/hour

**Files**:
- `backend/src/models/behavioral_event.py` (new)
- `backend/src/routers/learning.py` (extend)
- `backend/src/services/event_collector.py` (extend)
- `backend/migrations/versions/xxx_create_behavioral_events.py` (new)

---

## Phase 4: Behavior Modeling (Bounded)

**Agent**: 3 (Behavior Modeling Agent - Part 2)
**Effort**: 36 hours
**Priority**: P1

### Task 3.3: Implement Time-of-Day Pattern Analysis

**Status**: [ ]
**Effort**: 8 hours
**Dependencies**: Tasks 3.2, 1.3

**Acceptance Criteria**:
- [ ] Create `analyze_peak_hours()` function
- [ ] Aggregate task completions by hour_of_day
- [ ] Apply exponential decay weighting (recent events weighted higher)
- [ ] Normalize to 0-1 productivity scores per hour
- [ ] Identify top 3-5 peak hours
- [ ] Store in UserBehaviorProfile.peak_hours (JSON)
- [ ] Require minimum 20 events before detecting patterns

**Files**:
- `backend/src/learning/pattern_analyzer.py` (extend)
- `backend/src/learning/algorithms/timing.py` (new)
- `backend/tests/test_timing_patterns.py` (new)

---

### Task 3.4: Implement Task Type Timing Pattern Analysis

**Status**: [ ]
**Effort**: 7 hours
**Dependencies**: Task 3.3

**Acceptance Criteria**:
- [ ] Create `analyze_type_timing()` function
- [ ] Group events by task_type_hash × hour_of_day
- [ ] Calculate frequency distributions
- [ ] Identify statistically significant patterns (z-score > 1.5)
- [ ] Store in UserBehaviorProfile.type_timing_patterns (JSON)
- [ ] Format: `{task_type_hash: {hour: frequency_score}}`
- [ ] Require minimum 5 occurrences per task type

**Files**:
- `backend/src/learning/algorithms/timing.py` (extend)
- `backend/tests/test_type_timing.py` (new)

---

### Task 3.5: Implement Priority Adjustment Pattern Analysis

**Status**: [ ]
**Effort**: 7 hours
**Dependencies**: Task 3.2

**Acceptance Criteria**:
- [ ] Create `analyze_priority_patterns()` function
- [ ] Track priority_changed events
- [ ] Build transition probability matrix
- [ ] Filter for consistent patterns (>3 occurrences)
- [ ] Store in UserBehaviorProfile.priority_adjustment_patterns
- [ ] Require minimum 15 priority change events

**Files**:
- `backend/src/learning/algorithms/priority.py` (new)
- `backend/tests/test_priority_patterns.py` (new)

---

### Task 3.6: Implement Task Grouping Pattern Analysis

**Status**: [ ]
**Effort**: 6 hours
**Dependencies**: Task 3.2

**Acceptance Criteria**:
- [ ] Create `analyze_grouping_patterns()` function
- [ ] Track task_grouped events (same session_id)
- [ ] Calculate co-occurrence frequency for task_type_hash pairs
- [ ] Identify strong associations (co-occur >50% of time)
- [ ] Store in UserBehaviorProfile.grouping_patterns
- [ ] Require minimum 10 grouping events

**Files**:
- `backend/src/learning/algorithms/grouping.py` (new)
- `backend/tests/test_grouping_patterns.py` (new)

---

### Task 3.7: Implement Batch Learning Job

**Status**: [ ]
**Effort**: 8 hours
**Dependencies**: Tasks 3.3, 3.4, 3.5, 3.6

**Acceptance Criteria**:
- [ ] Create scheduled job (runs daily at 2 AM)
- [ ] For each user with learning_enabled=true:
  - Fetch behavioral events from last 90 days
  - Run analyze_peak_hours()
  - Run analyze_type_timing()
  - Run analyze_priority_patterns()
  - Run analyze_grouping_patterns()
  - Update UserBehaviorProfile with new patterns
- [ ] Job completion time: <30s per user
- [ ] Log job metrics

**Files**:
- `backend/src/jobs/batch_learning.py` (new)
- `backend/src/services/learning_service.py` (extend)
- `backend/tests/test_batch_learning.py` (new)

---

## Phase 5: Adaptive Logic

**Agent**: 4 (Adaptation Agent)
**Effort**: 47 hours
**Priority**: P1

### Task 4.1: Implement Confidence Scoring System

**Status**: [ ]
**Effort**: 6 hours
**Dependencies**: Task 3.7

**Acceptance Criteria**:
- [ ] Implement confidence formula:
  ```python
  confidence = (frequency_weight * 0.4) + (recency_weight * 0.3) + (consistency_weight * 0.3)
  ```
- [ ] Set minimum confidence threshold: 0.60 for suggestions
- [ ] Add confidence_score field to AdaptiveSuggestion model

**Files**:
- `backend/src/learning/confidence.py` (new)
- `backend/src/models/adaptive_suggestion.py` (new)
- `backend/tests/test_confidence.py` (new)

---

### Task 4.2: Implement Priority Adjustment Suggestions

**Status**: [ ]
**Effort**: 8 hours
**Dependencies**: Tasks 4.1, 3.5

**Acceptance Criteria**:
- [ ] Create `suggest_priority_adjustments()` function
- [ ] Analyze current task priorities vs learned patterns
- [ ] Generate suggestions for misaligned priorities
- [ ] Filter by confidence >= 0.60
- [ ] Include reasoning and confidence score

**Files**:
- `backend/src/learning/suggestion_generator.py` (new)
- `backend/src/learning/suggestions/priority.py` (new)
- `backend/tests/test_priority_suggestions.py` (new)

---

### Task 4.3: Implement Optimal Timing Suggestions

**Status**: [ ]
**Effort**: 7 hours
**Dependencies**: Tasks 4.1, 3.4

**Acceptance Criteria**:
- [ ] Create `suggest_optimal_timing()` function
- [ ] Lookup type_timing_patterns for task type
- [ ] Identify top 2-3 peak hours
- [ ] Only suggest if confidence >= 0.65

**Files**:
- `backend/src/learning/suggestions/timing.py` (new)
- `backend/tests/test_timing_suggestions.py` (new)

---

### Task 4.4: Implement Task Grouping Suggestions

**Status**: [ ]
**Effort**: 7 hours
**Dependencies**: Tasks 4.1, 3.6

**Acceptance Criteria**:
- [ ] Create `suggest_task_grouping()` function
- [ ] Find related task types frequently done together
- [ ] Limit to top 3 related tasks
- [ ] Confidence >= 0.60 required

**Files**:
- `backend/src/learning/suggestions/grouping.py` (new)
- `backend/tests/test_grouping_suggestions.py` (new)

---

### Task 4.5: Implement Suggestion API Endpoints

**Status**: [ ]
**Effort**: 6 hours
**Dependencies**: Tasks 4.2, 4.3, 4.4

**Acceptance Criteria**:
- [ ] Implement GET /api/adaptive/suggestions
- [ ] Implement POST /api/adaptive/suggestions/:id/respond
- [ ] Add rate limiting: max 100 requests/hour/user

**Files**:
- `backend/src/routers/adaptive.py` (new)
- `backend/src/services/suggestion_service.py` (new)
- `backend/tests/test_suggestion_api.py` (new)

---

### Task 4.6: Implement Suggestion Deduplication

**Status**: [ ]
**Effort**: 5 hours
**Dependencies**: Task 4.5

**Acceptance Criteria**:
- [ ] Track recently shown suggestions (last 7 days)
- [ ] Deduplicate by suggestion_type + target_task_id
- [ ] Max 3 suggestions/day for new users

**Files**:
- `backend/src/learning/deduplication.py` (new)
- `backend/src/services/suggestion_service.py` (extend)
- `backend/tests/test_deduplication.py` (new)

---

### Task 4.7: Implement Feedback Learning Loop

**Status**: [ ]
**Effort**: 8 hours
**Dependencies**: Task 4.5

**Acceptance Criteria**:
- [ ] Track suggestion responses
- [ ] Implement feedback adjustments:
  - Accept: +0.1 confidence boost
  - Reject: -0.15 confidence penalty
  - Dismiss: no change
- [ ] Update pattern weights weekly

**Files**:
- `backend/src/learning/feedback_processor.py` (new)
- `backend/src/jobs/feedback_learning.py` (new)
- `backend/tests/test_feedback_learning.py` (new)

---

## Phase 6: Explanation Engine

**Agent**: 5 (Explanation Agent)
**Effort**: 43 hours
**Priority**: P2

### Task 5.1: Implement Pattern Change Detection

**Status**: [ ]
**Effort**: 7 hours
**Dependencies**: Task 3.7

**Acceptance Criteria**:
- [ ] Compare old vs new UserBehaviorProfile
- [ ] Calculate statistical divergence
- [ ] Flag significant changes
- [ ] Store change events

**Files**:
- `backend/src/learning/change_detector.py` (new)
- `backend/src/models/pattern_change_log.py` (new)
- `backend/tests/test_change_detection.py` (new)

---

### Task 5.2: Implement "What Changed?" Explanation

**Status**: [ ]
**Effort**: 8 hours
**Dependencies**: Task 5.1

**Acceptance Criteria**:
- [ ] Create explanation templates
- [ ] Include data points and timeframe
- [ ] Add visualization
- [ ] API endpoint: GET /api/learning/changes

**Files**:
- `backend/src/learning/explanation_generator.py` (new)
- `frontend/src/components/PatternChangeSummary.tsx` (new)
- `backend/tests/test_explanation_generator.py` (new)

---

### Task 5.3: Implement "Why It Changed?" Analysis

**Status**: [ ]
**Effort**: 9 hours
**Dependencies**: Task 5.2

**Acceptance Criteria**:
- [ ] Analyze recent events that drove change
- [ ] Identify trigger events
- [ ] Generate causality explanation
- [ ] Include confidence level

**Files**:
- `backend/src/learning/causality_analyzer.py` (new)
- `frontend/src/components/ChangeReasoningPanel.tsx` (new)
- `backend/tests/test_causality.py` (new)

---

### Task 5.4: Implement "How to Revert?" Control

**Status**: [ ]
**Effort**: 8 hours
**Dependencies**: Task 5.1

**Acceptance Criteria**:
- [ ] Add "Revert This Change" button
- [ ] Implement pattern rollback
- [ ] Store pattern history (last 3 versions)
- [ ] API endpoints for revert and refresh

**Files**:
- `backend/src/learning/pattern_version.py` (new)
- `backend/src/routers/learning.py` (extend)
- `frontend/src/components/RevertPatternButton.tsx` (new)
- `backend/tests/test_pattern_revert.py` (new)

---

### Task 5.5: Implement Suggestion Reasoning Display

**Status**: [ ]
**Effort**: 6 hours
**Dependencies**: Task 4.5

**Acceptance Criteria**:
- [ ] Add "Why?" expandable section
- [ ] Include pattern reference, evidence, confidence
- [ ] Link to pattern visualization

**Files**:
- `frontend/src/components/SuggestionReasoningPanel.tsx` (new)
- `frontend/src/components/AdaptiveSuggestionCard.tsx` (extend)

---

### Task 5.6: Implement Pattern Drift Notifications

**Status**: [ ]
**Effort**: 5 hours
**Dependencies**: Tasks 5.1, 5.2

**Acceptance Criteria**:
- [ ] Detect pattern drift after batch learning
- [ ] Create notification
- [ ] Link to pattern change summary
- [ ] Only notify if confidence > 0.75

**Files**:
- `frontend/src/components/PatternDriftNotification.tsx` (new)
- `backend/src/jobs/batch_learning.py` (extend)
- `frontend/src/hooks/useNotifications.ts` (extend)

---

## Phase 7: Insights & Reports

**Agent**: 6 (Insight Agent)
**Effort**: 54 hours
**Priority**: P2

### Task 6.1: Implement Peak Productivity Hours Visualization

**Status**: [ ]
**Effort**: 6 hours
**Dependencies**: Task 3.7

**Acceptance Criteria**:
- [ ] Create bar chart component (hours 0-23)
- [ ] Fetch peak_hours data
- [ ] Highlight top 3 peak hours
- [ ] Add hover tooltip

**Files**:
- `frontend/src/components/PeakHoursChart.tsx` (new)
- `frontend/src/pages/LearningInsightsPage.tsx` (new)
- `frontend/src/services/learningApi.ts` (extend)

---

### Task 6.2: Implement Task Type Timing Heatmap

**Status**: [ ]
**Effort**: 8 hours
**Dependencies**: Task 3.7

**Acceptance Criteria**:
- [ ] Create heatmap component
- [ ] Fetch type_timing_patterns
- [ ] Color intensity based on frequency
- [ ] Handle sparse data

**Files**:
- `frontend/src/components/TaskTimingHeatmap.tsx` (new)
- `backend/src/routers/learning.py` (extend)

---

### Task 6.3: Implement Priority Flow Diagram

**Status**: [ ]
**Effort**: 9 hours
**Dependencies**: Task 3.7

**Acceptance Criteria**:
- [ ] Create Sankey diagram component
- [ ] Fetch priority_adjustment_patterns
- [ ] Visualize transitions
- [ ] Show percentages

**Files**:
- `frontend/src/components/PriorityFlowDiagram.tsx` (new)
- `frontend/src/lib/sankeyChart.ts` (new)

---

### Task 6.4: Implement Productivity Trends Analysis

**Status**: [ ]
**Effort**: 10 hours
**Dependencies**: Task 3.2

**Acceptance Criteria**:
- [ ] Calculate weekly completion rates
- [ ] Compare 4-week trend
- [ ] Track metrics
- [ ] Visualize as line charts

**Files**:
- `backend/src/learning/insights/productivity.py` (new)
- `frontend/src/components/ProductivityTrends.tsx` (new)
- `backend/tests/test_productivity_insights.py` (new)

---

### Task 6.5: Implement Habit Summaries

**Status**: [ ]
**Effort**: 7 hours
**Dependencies**: Task 3.7

**Acceptance Criteria**:
- [ ] Generate habit summary text
- [ ] Personalize based on strongest patterns
- [ ] Limit to top 5 habits
- [ ] API endpoint: GET /api/learning/insights/habits

**Files**:
- `backend/src/learning/insights/habits.py` (new)
- `frontend/src/components/HabitSummary.tsx` (new)
- `backend/tests/test_habit_summaries.py` (new)

---

### Task 6.6: Implement Workflow Improvement Suggestions

**Status**: [ ]
**Effort**: 9 hours
**Dependencies**: Tasks 6.4, 6.5

**Acceptance Criteria**:
- [ ] Analyze patterns for improvements
- [ ] Generate 3-5 recommendations
- [ ] Rank by impact
- [ ] Track which suggestions followed

**Files**:
- `backend/src/learning/insights/recommendations.py` (new)
- `frontend/src/components/ImprovementSuggestions.tsx` (new)
- `backend/tests/test_recommendations.py` (new)

---

### Task 6.7: Implement Data Points Counter

**Status**: [ ]
**Effort**: 5 hours
**Dependencies**: Task 3.2

**Acceptance Criteria**:
- [ ] Display total events collected
- [ ] Show breakdown by event type
- [ ] Add progress bar
- [ ] Show milestones

**Files**:
- `frontend/src/components/LearningProgress.tsx` (new)
- `backend/src/routers/learning.py` (extend)

---

## Phase 8: Reset & Rollback

**Agent**: 7 (Audit & Reset Agent)
**Effort**: 63 hours
**Priority**: P1

### Task 7.1: Implement Learning Activity Audit Log

**Status**: [ ]
**Effort**: 7 hours
**Dependencies**: None

**Acceptance Criteria**:
- [ ] Extend AIActivityLog model
- [ ] Track all learning operations
- [ ] Log retention: 2 years
- [ ] API endpoint: GET /api/learning/audit-log

**Files**:
- `backend/src/models/activity.py` (extend)
- `backend/src/services/audit_logger.py` (new)
- `backend/tests/test_audit_logging.py` (new)

---

### Task 7.2: Implement Pattern Version Snapshots

**Status**: [ ]
**Effort**: 8 hours
**Dependencies**: Task 3.7

**Acceptance Criteria**:
- [ ] Create PatternSnapshot model
- [ ] Auto-create snapshot before updates
- [ ] Keep last 10 snapshots per type
- [ ] Auto-delete snapshots older than 90 days

**Files**:
- `backend/src/models/pattern_snapshot.py` (new)
- `backend/src/services/snapshot_service.py` (new)
- `backend/migrations/versions/xxx_create_pattern_snapshots.py` (new)
- `backend/tests/test_pattern_snapshots.py` (new)

---

### Task 7.3: Implement Complete Learning Reset

**Status**: [ ]
**Effort**: 9 hours
**Dependencies**: Task 7.1

**Acceptance Criteria**:
- [ ] Delete all BehavioralEvent records
- [ ] Delete UserBehaviorProfile
- [ ] Delete all AdaptiveSuggestion records
- [ ] Delete all PatternSnapshot records
- [ ] Reset UserPreferences
- [ ] Log deletion event

**Files**:
- `frontend/src/components/ResetLearningModal.tsx` (new)
- `backend/src/routers/learning.py` (extend)
- `backend/src/services/reset_service.py` (new)
- `backend/tests/test_complete_reset.py` (new)

---

### Task 7.4: Implement Audit Log Viewer UI

**Status**: [ ]
**Effort**: 8 hours
**Dependencies**: Task 7.1

**Acceptance Criteria**:
- [ ] Create audit log viewer page
- [ ] Display events chronologically
- [ ] Filter by type, date range, result
- [ ] Pagination: 20 events per page
- [ ] Export as JSON or CSV

**Files**:
- `frontend/src/pages/AuditLogPage.tsx` (new)
- `frontend/src/components/AuditLogViewer.tsx` (new)
- `frontend/src/components/AuditEventCard.tsx` (new)
- `backend/src/routers/learning.py` (extend)

---

### Task 7.5: Implement Data Export with Full History

**Status**: [ ]
**Effort**: 9 hours
**Dependencies**: Tasks 7.1, 7.2

**Acceptance Criteria**:
- [ ] Generate comprehensive JSON export
- [ ] Include all behavioral events
- [ ] Include patterns and snapshots
- [ ] Include audit log
- [ ] Support CSV format

**Files**:
- `backend/src/services/data_export.py` (extend)
- `backend/src/exporters/json_exporter.py` (new)
- `backend/src/exporters/csv_exporter.py` (new)
- `backend/tests/test_data_export.py` (new)

---

### Task 7.6: Implement Privacy Validation Test Suite

**Status**: [ ]
**Effort**: 10 hours
**Dependencies**: All previous tasks

**Acceptance Criteria**:
- [ ] Test: No task content in BehavioralEvent
- [ ] Test: No PII in learning data
- [ ] Test: User isolation
- [ ] Test: Complete data deletion
- [ ] Test: Audit trail completeness
- [ ] Run in CI/CD pipeline

**Files**:
- `backend/tests/privacy/test_no_content_leakage.py` (new)
- `backend/tests/privacy/test_user_isolation.py` (new)
- `backend/tests/privacy/test_complete_deletion.py` (new)
- `backend/tests/privacy/test_audit_completeness.py` (new)
- `.github/workflows/privacy-validation.yml` (new)

---

### Task 7.7: Implement Learning Health Dashboard (Admin)

**Status**: [ ]
**Effort**: 12 hours
**Dependencies**: Tasks 7.1, 7.6

**Acceptance Criteria**:
- [ ] Admin-only dashboard
- [ ] Show system health metrics
- [ ] Show privacy compliance score
- [ ] Historical trends
- [ ] Export metrics

**Files**:
- `backend/src/admin/learning_dashboard.py` (new)
- `backend/src/services/metrics_collector.py` (new)
- `frontend/src/pages/admin/LearningHealthPage.tsx` (new)

---

## Success Criteria

### Functional Success
- ✅ Users can opt-in to behavioral learning
- ✅ System captures timing, frequency, grouping patterns only
- ✅ No task content stored (verified by automated tests)
- ✅ Patterns detected after 2 weeks of usage
- ✅ Suggestions generated with 70%+ acceptance rate
- ✅ Users can view and understand their patterns
- ✅ Complete data reset functionality works

### Non-Functional Success
- ✅ Event capture latency <100ms (p95)
- ✅ Pattern query latency <2s (p95)
- ✅ Suggestion generation <1s (p95)
- ✅ 95% privacy compliance (automated tests pass)
- ✅ GDPR/CCPA compliant (data export + deletion)

### User Experience Success
- ✅ 90% of users understand privacy controls within 5 minutes
- ✅ 40% improvement in task completion efficiency
- ✅ 30% reduction in manual prioritization effort
- ✅ 70% suggestion acceptance rate after initial learning period

---

## References

- **Spec**: `specs/005-adaptive-intelligence/spec.md`
- **Plan**: `specs/005-adaptive-intelligence/plan.md`
- **ADRs**:
  - `history/adr/001-privacy-preserving-behavioral-learning-architecture.md`
  - `history/adr/002-pattern-analysis-and-confidence-scoring-system.md`
  - `history/adr/003-user-control-and-transparency-framework.md`
- **Agent Tasks**: `specs/005-adaptive-intelligence/tasks/` (detailed breakdown)

---

**Last Updated**: 2026-01-14
**Status**: Ready for Implementation ✅
