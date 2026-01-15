# ADR-002: Pattern Analysis and Confidence Scoring System

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-01-14
- **Feature:** 005-adaptive-intelligence
- **Context:** Phase 5 behavioral learning must convert raw behavioral events into actionable patterns and confident suggestions. The system needs to detect meaningful patterns (timing preferences, priority adjustments, task grouping) while avoiding false positives from noise or insufficient data. This decision addresses: How do we reliably extract patterns from behavioral metadata? How do we measure confidence in learned patterns? How do we improve suggestions based on user feedback?

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Determines learning accuracy and suggestion quality
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Statistical vs ML-based vs rule-based approaches
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects backend services, algorithms, user experience, metrics
-->

## Decision

Implement a **statistical pattern analysis system with confidence scoring and feedback-driven improvement**:

**Pattern Detection Algorithms:**
- **Time-of-Day Analysis:** Aggregate task completions by hour with exponential decay weighting (recent events weighted 2x)
- **Task Type Timing:** Build frequency distributions for task_type_hash × hour_of_day combinations
- **Priority Adjustment Patterns:** Create transition probability matrix tracking priority changes (Low→High, etc.)
- **Task Grouping Patterns:** Detect co-occurrence of task types within same session_id

**Confidence Scoring Strategy:**
```python
confidence_score = (frequency_weight * 0.4) + (recency_weight * 0.3) + (consistency_weight * 0.3)

# Frequency: Number of occurrences (normalized 0-1)
# Recency: Time decay factor (last 30 days = 1.0, exponential decay)
# Consistency: Standard deviation of pattern (lower = higher confidence)

# Minimum thresholds:
# - Pattern detection: ≥3 occurrences required
# - Suggestion generation: ≥0.60 confidence required
# - High-confidence display: ≥0.75 confidence prioritized
```

**Feedback Learning Loop:**
- Track user responses: Accept (+0.1 confidence), Reject (-0.15 confidence), Dismiss (no change)
- Adjust pattern weights based on acceptance rates
- Retrain patterns weekly using updated confidence adjustments
- Cap confidence boost/penalty to prevent overfitting

**Edge Case Handling:**
- **Insufficient Data (<20 events):** Show "Building your profile..." message, no suggestions
- **Conflicting Patterns:** Use recency weighting (last 30 days), fall back to Phase 4 rules if ambiguous
- **Pattern Drift:** Detect statistical divergence (>25% change), notify user, offer profile refresh

**Architecture Components:**
- **LearningService:** Orchestrates pattern detection, scheduled daily batch job
- **AdaptiveSuggestionService:** Generates suggestions from patterns, filters by confidence threshold
- **FeedbackProcessor:** Adjusts confidence scores based on user responses
- **PatternStore:** Persists aggregated patterns in UserBehaviorProfile JSON fields

## Consequences

### Positive

1. **Accuracy:** Statistical approach with 70%+ confidence threshold produces reliable suggestions
2. **Explainability:** Frequency + recency + consistency factors are human-understandable
3. **Adaptability:** Feedback loop continuously improves suggestion quality over time
4. **Performance:** Statistical aggregation is fast (<2s for pattern analysis) and scalable
5. **Simplicity:** No ML model training/deployment complexity, pure algorithmic approach
6. **Debuggability:** Deterministic algorithms enable reproducible testing and troubleshooting
7. **Privacy-Aligned:** Statistical methods work well with metadata-only constraints (ADR-001)

### Negative

1. **Cold Start Period:** Requires 2+ weeks of data to detect reliable patterns
2. **Limited Sophistication:** Cannot detect complex multi-variable interactions (e.g., "email tasks on Monday mornings")
3. **Manual Tuning:** Confidence weights (0.4/0.3/0.3) require empirical tuning, not learned
4. **False Negatives:** Conservative thresholds (≥3 occurrences, ≥0.60 confidence) miss weak but real patterns
5. **Feedback Noise:** User rejection may be context-specific (busy day) not pattern-invalid
6. **Drift Lag:** Weekly retraining means delayed response to behavior changes
7. **No Transfer Learning:** Each user starts from zero, cannot leverage population patterns

## Alternatives Considered

### Alternative A: Machine Learning-Based Pattern Detection
**Approach:** Train supervised ML models (Random Forest, XGBoost) on labeled behavioral data
**Components:**
- Feature engineering: time-of-day, day-of-week, task_type_hash embeddings
- Model training: Weekly retraining on user feedback (accept/reject labels)
- Prediction: Generate suggestions with ML-predicted confidence scores

**Why Rejected:**
- ❌ Complexity: Requires ML infrastructure (training pipeline, model versioning, serving)
- ❌ Cold Start: Insufficient data for training (need 100s of labeled examples per user)
- ❌ Explainability: Black-box predictions harder to debug and explain to users
- ❌ Overhead: Model training consumes more compute resources than statistical aggregation
- ❌ Overkill: Current problem doesn't require ML sophistication for Phase 5 MVP

### Alternative B: Rule-Based Heuristics Only
**Approach:** Hand-coded if/then rules for pattern detection
**Components:**
- Fixed rules: "If 3+ task completions at hour X, set as peak hour"
- No confidence scoring: Binary yes/no pattern detection
- No learning: Rules don't adapt based on user feedback

**Why Rejected:**
- ❌ Brittleness: Rules don't generalize to diverse user behaviors
- ❌ Maintenance: Requires constant rule updates as edge cases emerge
- ❌ No Improvement: System never gets better with usage
- ❌ Poor UX: Binary yes/no lacks nuance for displaying suggestions
- ❌ Limited Personalization: Cannot weight patterns by user-specific feedback

### Alternative C: Real-Time Streaming Pattern Detection
**Approach:** Detect patterns incrementally as events arrive (no batch processing)
**Components:**
- Event stream processing: Update patterns immediately on each behavioral event
- Online learning: Adjust confidence scores in real-time
- No batch jobs: All aggregation happens synchronously

**Why Rejected:**
- ❌ Complexity: Requires streaming infrastructure (Kafka, Flink) for incremental updates
- ❌ Cost: Continuous processing more expensive than daily batch jobs
- ❌ Unnecessary: Pattern changes are gradual, daily updates sufficient for UX
- ❌ Debugging: Harder to reproduce pattern states for troubleshooting
- ❌ Over-engineering: Real-time not required for task planning domain

### Decision Rationale

**Statistical + Confidence + Feedback (chosen approach)** provides the best balance:
- ✅ Sufficient accuracy for Phase 5 MVP (70%+ acceptance target)
- ✅ Fast and scalable with simple infrastructure
- ✅ Explainable and debuggable for trust-building
- ✅ Adapts to user feedback without ML complexity
- ✅ Works well with metadata-only privacy constraints
- ⚖️ Trade ML sophistication for simplicity - acceptable for initial release

## References

- Feature Spec: `specs/005-adaptive-intelligence/spec.md` (FR-002, FR-004, FR-005, FR-009, FR-011)
- Implementation Plan: `specs/005-adaptive-intelligence/plan.md` (sections 4.2, 4.3, 4.5, 7)
- Related ADRs: ADR-001 (Privacy Architecture), ADR-003 (User Control)
- Success Criteria: SC-002 (70% acceptance rate), SC-001 (30% effort reduction)
- Performance Targets: <2s pattern analysis (p95), <1s suggestion generation (p95)
