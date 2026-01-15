# Agent 4: Adaptation Agent

**Responsibility**: Adaptive prioritization, suggestion tuning, workflow personalization

**Priority**: P1 (Core Feature - Primary user-facing value)

---

## Task 4.1: Implement Confidence Scoring System

**Description**: Calculate confidence scores for learned patterns to filter low-quality suggestions

**Acceptance Criteria**:
- [ ] Implement confidence formula:
  ```python
  confidence = (frequency_weight * 0.4) + (recency_weight * 0.3) + (consistency_weight * 0.3)
  ```
- [ ] Frequency weight: occurrences / max_occurrences (normalized 0-1)
- [ ] Recency weight: exponential decay over days_since_last
- [ ] Consistency weight: 1 - (std_deviation / mean)
- [ ] Set minimum confidence threshold: 0.60 for suggestions
- [ ] Add confidence_score field to AdaptiveSuggestion model

**Files**:
- `backend/src/learning/confidence.py` (new)
- `backend/src/models/adaptive_suggestion.py` (new)
- `backend/tests/test_confidence.py` (new)

**Dependencies**: Task 3.7 (Patterns available)

**Estimated Effort**: 6 hours

---

## Task 4.2: Implement Priority Adjustment Suggestions

**Description**: Suggest priority changes based on user's historical priority adjustment patterns

**Acceptance Criteria**:
- [ ] Create `suggest_priority_adjustments()` function
- [ ] Analyze current task priorities vs learned patterns
- [ ] Generate suggestions for misaligned priorities
- [ ] Filter by confidence >= 0.60
- [ ] Format: "Based on your habits, consider changing [Task] from Medium to High priority"
- [ ] Include reasoning: "You typically prioritize similar tasks as High"
- [ ] Store as AdaptiveSuggestion records

**Files**:
- `backend/src/learning/suggestion_generator.py` (new)
- `backend/src/learning/suggestions/priority.py` (new)
- `backend/tests/test_priority_suggestions.py` (new)

**Dependencies**: Task 4.1, Task 3.5 (Priority patterns)

**Estimated Effort**: 8 hours

---

## Task 4.3: Implement Optimal Timing Suggestions

**Description**: Suggest best times to work on tasks based on type and timing patterns

**Acceptance Criteria**:
- [ ] Create `suggest_optimal_timing()` function
- [ ] Hash task type (privacy-safe)
- [ ] Lookup type_timing_patterns for this type
- [ ] Identify top 2-3 peak hours for this task type
- [ ] Generate suggestion: "Try completing this task at 2-4 PM (your peak time for similar tasks)"
- [ ] Include confidence score in suggestion
- [ ] Only suggest if confidence >= 0.65

**Files**:
- `backend/src/learning/suggestions/timing.py` (new)
- `backend/tests/test_timing_suggestions.py` (new)

**Dependencies**: Task 4.1, Task 3.4 (Type timing patterns)

**Estimated Effort**: 7 hours

---

## Task 4.4: Implement Task Grouping Suggestions

**Description**: Suggest related tasks to batch together based on grouping patterns

**Acceptance Criteria**:
- [ ] Create `suggest_task_grouping()` function
- [ ] When user creates/views a task, check grouping_patterns
- [ ] Find related task types frequently done together
- [ ] Find existing incomplete tasks of related types
- [ ] Suggest: "Consider also working on [Related Tasks] (you typically do these together)"
- [ ] Limit to top 3 related tasks
- [ ] Confidence >= 0.60 required

**Files**:
- `backend/src/learning/suggestions/grouping.py` (new)
- `backend/tests/test_grouping_suggestions.py` (new)

**Dependencies**: Task 4.1, Task 3.6 (Grouping patterns)

**Estimated Effort**: 7 hours

---

## Task 4.5: Implement Suggestion API Endpoints

**Description**: REST API for retrieving and responding to adaptive suggestions

**Acceptance Criteria**:
- [ ] Implement GET /api/adaptive/suggestions
  - Returns pending suggestions for user
  - Sorted by confidence (highest first)
  - Limited to top 5 suggestions
  - Includes reasoning and confidence score
- [ ] Implement POST /api/adaptive/suggestions/:id/respond
  - Actions: "accept", "reject", "dismiss"
  - Optional feedback text
  - Update suggestion status
  - Log user response for feedback learning
- [ ] Add rate limiting: max 100 requests/hour/user

**Files**:
- `backend/src/routers/adaptive.py` (new)
- `backend/src/services/suggestion_service.py` (new)
- `backend/tests/test_suggestion_api.py` (new)

**Dependencies**: Tasks 4.2, 4.3, 4.4

**Estimated Effort**: 6 hours

---

## Task 4.6: Implement Suggestion Deduplication

**Description**: Prevent duplicate or redundant suggestions from overwhelming users

**Acceptance Criteria**:
- [ ] Track recently shown suggestions (last 7 days)
- [ ] Deduplicate by suggestion_type + target_task_id
- [ ] Suppress suggestions with >80% similarity to recent suggestions
- [ ] Implement cooldown period: same suggestion not shown for 48 hours after dismiss
- [ ] Max 3 suggestions/day for new users (gradual introduction)
- [ ] Increase to 5 suggestions/day after 70%+ acceptance rate

**Files**:
- `backend/src/learning/deduplication.py` (new)
- `backend/src/services/suggestion_service.py` (extend)
- `backend/tests/test_deduplication.py` (new)

**Dependencies**: Task 4.5

**Estimated Effort**: 5 hours

---

## Task 4.7: Implement Feedback Learning Loop

**Description**: Adjust confidence scores based on user accept/reject/dismiss responses

**Acceptance Criteria**:
- [ ] Track suggestion responses in database
- [ ] Implement feedback adjustments:
  - Accept: +0.1 confidence boost for pattern type
  - Reject: -0.15 confidence penalty for pattern type
  - Dismiss: no change (neutral)
- [ ] Cap confidence adjustments: min 0.4, max 1.0
- [ ] Update pattern weights weekly based on acceptance rate
- [ ] If acceptance rate < 50%, reduce suggestion frequency
- [ ] If acceptance rate > 80%, increase suggestion frequency

**Files**:
- `backend/src/learning/feedback_processor.py` (new)
- `backend/src/jobs/feedback_learning.py` (new)
- `backend/tests/test_feedback_learning.py` (new)

**Dependencies**: Task 4.5

**Estimated Effort**: 8 hours

---

**Total Agent Effort**: 47 hours
