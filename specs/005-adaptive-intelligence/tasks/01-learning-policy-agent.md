# Agent 1: Learning Policy Agent

**Responsibility**: Define what signals are learnable, forbidden signals, and decay/forgetting rules

**Priority**: P0 (Foundation - Required before any learning begins)

---

## Task 1.1: Define Learnable Signal Specification

**Description**: Create comprehensive specification of signals that can be safely learned without privacy violations

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

**Dependencies**: None (foundation task)

**Estimated Effort**: 4 hours

---

## Task 1.2: Define Forbidden Signal Policy

**Description**: Create explicit policy and enforcement for signals that must NEVER be learned

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

**Dependencies**: Task 1.1

**Estimated Effort**: 6 hours

---

## Task 1.3: Implement Signal Decay Rules

**Description**: Define and implement temporal decay for learned patterns to prevent stale patterns from dominating

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
- `backend/src/learning/pattern_analyzer.py` (extend)
- `backend/tests/test_decay.py` (new)

**Dependencies**: Task 1.1

**Estimated Effort**: 5 hours

---

## Task 1.4: Implement Forgetting Rules

**Description**: Define rules for when patterns should be automatically forgotten or reset

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

**Dependencies**: Task 1.3

**Estimated Effort**: 6 hours

---

## Task 1.5: Create Learning Policy Documentation

**Description**: Comprehensive documentation of learning policy for users and developers

**Acceptance Criteria**:
- [ ] Create user-facing privacy policy document
- [ ] Create developer learning policy reference
- [ ] Document signal approval process for future additions
- [ ] Add policy version number and changelog

**Files**:
- `docs/learning-policy.md` (new)
- `docs/developer-learning-guide.md` (new)
- `PRIVACY.md` (new, user-facing)

**Dependencies**: Tasks 1.1, 1.2, 1.3, 1.4

**Estimated Effort**: 4 hours

---

**Total Agent Effort**: 25 hours
