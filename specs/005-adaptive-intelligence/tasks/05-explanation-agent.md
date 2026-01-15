# Agent 5: Explanation Agent

**Responsibility**: "What changed?", "Why it changed?", "How to revert?"

**Priority**: P2 (Transparency - Critical for user trust)

---

## Task 5.1: Implement Pattern Change Detection

**Description**: Detect when learned patterns change significantly and notify users

**Acceptance Criteria**:
- [ ] Compare old vs new UserBehaviorProfile after batch learning
- [ ] Calculate statistical divergence for each pattern type:
  - Peak hours shift: Jaccard similarity < 0.7
  - Type timing changes: >25% distribution change
  - Priority patterns: >20% transition probability change
  - Grouping changes: >30% association change
- [ ] Flag significant changes for user notification
- [ ] Store change events in pattern_change_log table

**Files**:
- `backend/src/learning/change_detector.py` (new)
- `backend/src/models/pattern_change_log.py` (new)
- `backend/tests/test_change_detection.py` (new)

**Dependencies**: Task 3.7 (Batch learning)

**Estimated Effort**: 7 hours

---

## Task 5.2: Implement "What Changed?" Explanation

**Description**: Generate human-readable summaries of pattern changes

**Acceptance Criteria**:
- [ ] Create explanation templates for each change type:
  - Peak hours: "Your most productive hours shifted from 9-11 AM to 2-4 PM"
  - Type timing: "You're now completing [type] tasks earlier in the day"
  - Priority: "You've been promoting more Medium tasks to High priority"
  - Grouping: "You're frequently doing [typeA] and [typeB] together now"
- [ ] Include data points: "Based on 45 events over the last 2 weeks"
- [ ] Add visualization: side-by-side before/after charts
- [ ] API endpoint: GET /api/learning/changes

**Files**:
- `backend/src/learning/explanation_generator.py` (new)
- `frontend/src/components/PatternChangeSummary.tsx` (new)
- `backend/tests/test_explanation_generator.py` (new)

**Dependencies**: Task 5.1

**Estimated Effort**: 8 hours

---

## Task 5.3: Implement "Why It Changed?" Analysis

**Description**: Explain the reasons behind pattern changes based on recent behavior

**Acceptance Criteria**:
- [ ] Analyze recent behavioral events that drove the change
- [ ] Identify trigger events (e.g., 10 late-afternoon completions in last week)
- [ ] Generate causality explanation:
  - "This changed because you completed 12 tasks at 3-5 PM this week"
  - "Your work schedule appears to have shifted later"
  - "You're prioritizing urgent tasks more frequently"
- [ ] Include confidence: "High confidence (85%)" or "Medium confidence (65%)"
- [ ] Show supporting evidence: chart of recent events

**Files**:
- `backend/src/learning/causality_analyzer.py` (new)
- `frontend/src/components/ChangeReasoningPanel.tsx` (new)
- `backend/tests/test_causality.py` (new)

**Dependencies**: Task 5.2

**Estimated Effort**: 9 hours

---

## Task 5.4: Implement "How to Revert?" Control

**Description**: Allow users to revert specific pattern changes or refresh patterns entirely

**Acceptance Criteria**:
- [ ] Add "Revert This Change" button for each detected change
- [ ] Implement pattern rollback to previous state
- [ ] Store pattern history (last 3 versions)
- [ ] Add "Refresh All Patterns" button to relearn from scratch
- [ ] Confirmation modal: "This will reset [pattern type]. Continue?"
- [ ] API endpoints:
  - POST /api/learning/patterns/:type/revert
  - POST /api/learning/patterns/refresh
- [ ] Log revert events to audit trail

**Files**:
- `backend/src/learning/pattern_version.py` (new)
- `backend/src/routers/learning.py` (extend)
- `frontend/src/components/RevertPatternButton.tsx` (new)
- `backend/tests/test_pattern_revert.py` (new)

**Dependencies**: Task 5.1

**Estimated Effort**: 8 hours

---

## Task 5.5: Implement Suggestion Reasoning Display

**Description**: Show users why each suggestion was made with supporting evidence

**Acceptance Criteria**:
- [ ] Add "Why?" expandable section to each suggestion card
- [ ] Include reasoning components:
  - Pattern reference: "Based on your timing pattern"
  - Evidence: "You completed similar tasks at 2 PM in 8 of the last 10 times"
  - Confidence: "85% confidence"
  - Data age: "Pattern learned from last 30 days"
- [ ] Link to pattern visualization: "View your timing patterns →"
- [ ] Add "This doesn't match my habits" feedback button

**Files**:
- `frontend/src/components/SuggestionReasoningPanel.tsx` (new)
- `frontend/src/components/AdaptiveSuggestionCard.tsx` (extend)

**Dependencies**: Task 4.5 (Suggestions API)

**Estimated Effort**: 6 hours

---

## Task 5.6: Implement Pattern Drift Notifications

**Description**: Proactively notify users when their patterns change significantly

**Acceptance Criteria**:
- [ ] Detect pattern drift after batch learning job
- [ ] Create notification: "📊 Your work patterns have changed. Review changes?"
- [ ] Link to pattern change summary page
- [ ] Allow dismissing notification with "Got it, thanks"
- [ ] Track notification dismiss rate to tune sensitivity
- [ ] Only notify if confidence in change > 0.75

**Files**:
- `frontend/src/components/PatternDriftNotification.tsx` (new)
- `backend/src/jobs/batch_learning.py` (extend - trigger notifications)
- `frontend/src/hooks/useNotifications.ts` (extend)

**Dependencies**: Task 5.1, Task 5.2

**Estimated Effort**: 5 hours

---

**Total Agent Effort**: 43 hours
