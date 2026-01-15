# Agent 3: Behavior Modeling Agent

**Responsibility**: Task timing patterns, priority preferences, completion behavior

**Priority**: P1 (Core Learning - Foundation for personalization)

---

## Task 3.1: Implement Behavioral Event Capture

**Description**: Client-side event capture for privacy-safe behavioral metadata

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

**Dependencies**: Task 2.1 (Consent), Task 1.1 (Signal Policy)

**Estimated Effort**: 8 hours

---

## Task 3.2: Implement Behavioral Event Storage

**Description**: Server-side API endpoint and database storage for behavioral events

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

**Dependencies**: Task 3.1

**Estimated Effort**: 6 hours

---

## Task 3.3: Implement Time-of-Day Pattern Analysis

**Description**: Detect when users are most productive based on task completion timing

**Acceptance Criteria**:
- [ ] Create `analyze_peak_hours()` function
- [ ] Aggregate task completions by hour_of_day
- [ ] Apply exponential decay weighting (recent events weighted higher)
- [ ] Normalize to 0-1 productivity scores per hour
- [ ] Identify top 3-5 peak hours
- [ ] Store in UserBehaviorProfile.peak_hours (JSON)
- [ ] Require minimum 20 events before detecting patterns

**Files**:
- `backend/src/learning/pattern_analyzer.py` (new)
- `backend/src/learning/algorithms/timing.py` (new)
- `backend/tests/test_timing_patterns.py` (new)

**Dependencies**: Task 3.2, Task 1.3 (Decay Rules)

**Estimated Effort**: 8 hours

---

## Task 3.4: Implement Task Type Timing Pattern Analysis

**Description**: Learn when users prefer to work on specific types of tasks

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

**Dependencies**: Task 3.3

**Estimated Effort**: 7 hours

---

## Task 3.5: Implement Priority Adjustment Pattern Analysis

**Description**: Learn how users typically adjust task priorities

**Acceptance Criteria**:
- [ ] Create `analyze_priority_patterns()` function
- [ ] Track priority_changed events
- [ ] Build transition probability matrix:
  - `{Low: {Medium: 0.6, High: 0.3, Low: 0.1}}`
  - `{Medium: {High: 0.5, Low: 0.2, Medium: 0.3}}`
  - `{High: {High: 0.7, Medium: 0.2, Low: 0.1}}`
- [ ] Filter for consistent patterns (>3 occurrences)
- [ ] Store in UserBehaviorProfile.priority_adjustment_patterns
- [ ] Require minimum 15 priority change events

**Files**:
- `backend/src/learning/algorithms/priority.py` (new)
- `backend/tests/test_priority_patterns.py` (new)

**Dependencies**: Task 3.2

**Estimated Effort**: 7 hours

---

## Task 3.6: Implement Task Grouping Pattern Analysis

**Description**: Detect which task types users frequently complete together

**Acceptance Criteria**:
- [ ] Create `analyze_grouping_patterns()` function
- [ ] Track task_grouped events (same session_id)
- [ ] Calculate co-occurrence frequency for task_type_hash pairs
- [ ] Identify strong associations (co-occur >50% of time)
- [ ] Store in UserBehaviorProfile.grouping_patterns
- [ ] Format: `{task_type_hash: [related_type_hashes]}`
- [ ] Require minimum 10 grouping events

**Files**:
- `backend/src/learning/algorithms/grouping.py` (new)
- `backend/tests/test_grouping_patterns.py` (new)

**Dependencies**: Task 3.2

**Estimated Effort**: 6 hours

---

## Task 3.7: Implement Batch Learning Job

**Description**: Daily scheduled job to analyze behavioral events and update patterns

**Acceptance Criteria**:
- [ ] Create scheduled job (runs daily at 2 AM)
- [ ] For each user with learning_enabled=true:
  - Fetch behavioral events from last 90 days
  - Run analyze_peak_hours()
  - Run analyze_type_timing()
  - Run analyze_priority_patterns()
  - Run analyze_grouping_patterns()
  - Update UserBehaviorProfile with new patterns
  - Increment data_points_collected counter
  - Set last_learning_date timestamp
- [ ] Job completion time: <30s per user
- [ ] Log job metrics (users processed, patterns updated, errors)

**Files**:
- `backend/src/jobs/batch_learning.py` (new)
- `backend/src/services/learning_service.py` (extend)
- `backend/tests/test_batch_learning.py` (new)

**Dependencies**: Tasks 3.3, 3.4, 3.5, 3.6

**Estimated Effort**: 8 hours

---

**Total Agent Effort**: 50 hours
