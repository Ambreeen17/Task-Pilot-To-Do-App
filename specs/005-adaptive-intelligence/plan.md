# Implementation Plan - Phase 5: Self-Learning & Adaptive Intelligence

**Feature Branch**: `005-adaptive-intelligence`
**Status**: PLANNING → IMPLEMENTATION
**Specification**: `specs/005-adaptive-intelligence/spec.md`
**Last Updated**: 2026-01-14

## Executive Summary

Phase 5 introduces **privacy-preserving behavioral learning** to the Phase 4 autonomous todo system. The system learns from user behavior patterns (timing, frequency, grouping) to provide personalized task prioritization and workflow suggestions, while maintaining strict privacy boundaries—no task content is ever learned or stored.

**Key Innovation**: Client-side behavioral event capture with server-side pattern analysis using privacy-preserving aggregation, ensuring all learning is transparent, reversible, and user-controlled.

## 1. Technical Context

### Current State (Phase 4) → Phase 5 Transformation

| Aspect | Phase 4 (Current) | Phase 5 (Target) |
|:---|:---|:---|
| **Suggestion Model** | Rule-based (deadline proximity, patterns) | **Learning-based** (user behavior patterns) |
| **Personalization** | Fixed autonomy levels | **Adaptive**: learns individual preferences |
| **Data Collection** | Activity logs (audit only) | **Behavioral metadata** (timing, frequency, grouping) |
| **Privacy Model** | No data aggregation | **Privacy-first**: metadata only, no content |
| **User Control** | Autonomy on/off | **Granular**: opt-in learning + data reset |
| **Suggestion Quality** | Generic recommendations | **Personalized**: based on historical patterns |

### Architecture Evolution

**From**: Rule-based autonomous suggestions
**To**: Adaptive learning system with:
- Privacy-preserving behavioral data collection
- Pattern analysis and preference learning
- Personalized task prioritization
- Interactive pattern exploration UI
- User-controlled learning with full transparency

## 2. Data Model Extensions

### BehavioralEvent Model (SQLModel)
```python
class BehavioralEvent(SQLModel, table=True):
    """
    Captures user behavior metadata WITHOUT task content.
    Privacy: Only timing, frequency, and grouping patterns.
    """
    __tablename__ = "behavioral_events"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    event_type: str = Field()  # "task_completed", "priority_changed", "task_grouped"

    # Timing data (privacy-safe)
    hour_of_day: int = Field(ge=0, le=23)  # When action occurred
    day_of_week: int = Field(ge=0, le=6)  # 0=Monday, 6=Sunday

    # Frequency data (privacy-safe)
    task_type_hash: str = Field()  # One-way hash of task type/category (NOT content)

    # Grouping data (privacy-safe)
    session_id: Optional[str] = Field(default=None)  # Groups actions in same session

    # Metadata
    timestamp: datetime = Field(default_factory=utcnow, index=True)

    # CRITICAL: No task content, description, title, or user metadata stored
```

### UserBehaviorProfile Model (SQLModel)
```python
class UserBehaviorProfile(SQLModel, table=True):
    """
    Aggregated behavioral patterns learned from BehavioralEvent data.
    Stores statistical summaries, not raw events.
    """
    __tablename__ = "user_behavior_profiles"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", unique=True, index=True)

    # Time-of-day preferences (JSON: {hour: frequency_score})
    peak_hours: str = Field(default="{}")  # When user is most productive

    # Task type patterns (JSON: {type_hash: {hour: frequency}})
    type_timing_patterns: str = Field(default="{}")

    # Priority change patterns (JSON: {from_priority: {to_priority: frequency}})
    priority_adjustment_patterns: str = Field(default="{}")

    # Session grouping patterns (JSON: {type_hash: [related_type_hashes]})
    grouping_patterns: str = Field(default="{}")

    # Learning metadata
    data_points_collected: int = Field(default=0)
    last_learning_date: Optional[datetime] = Field(default=None)
    model_version: str = Field(default="1.0")

    # User control
    learning_enabled: bool = Field(default=False)  # Opt-in
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
```

### AdaptiveSuggestion Model (SQLModel)
```python
class AdaptiveSuggestion(SQLModel, table=True):
    """
    Personalized suggestions generated from learned behavioral patterns.
    Extends Phase 4 AutonomousAction with learning-based reasoning.
    """
    __tablename__ = "adaptive_suggestions"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    suggestion_type: str = Field()  # "priority_adjust", "timing_optimize", "grouping_suggest"

    # Target task (optional - may be general workflow suggestion)
    target_task_id: Optional[uuid.UUID] = Field(default=None, foreign_key="tasks.id")

    # Suggestion details
    message: str = Field(max_length=500)  # User-facing explanation
    reasoning: str = Field(max_length=2000)  # Based on learned pattern X
    confidence: float = Field(ge=0.0, le=1.0)  # Model confidence

    # Behavioral evidence
    pattern_evidence: str = Field()  # JSON: {pattern_type, frequency, recency}

    # User interaction
    status: str = Field(default="pending")  # "pending", "accepted", "rejected", "dismissed"
    created_at: datetime = Field(default_factory=utcnow)
    responded_at: Optional[datetime] = Field(default=None)
```

### Update UserPreferences Model
```python
# Add to existing UserPreferences model:
    learning_enabled: bool = Field(default=False)  # Opt-in for Phase 5
    learning_categories: str = Field(default='["timing", "priority"]')  # What to learn
    pattern_visibility: str = Field(default="high")  # "low", "medium", "high"
```

## 3. API Endpoints Architecture

### Learning Control API
```python
# GET /api/learning/status
# Returns: Learning enabled status, data points collected, last update

# POST /api/learning/enable
# Activates: Behavioral learning for user (opt-in)

# POST /api/learning/disable
# Deactivates: Stops learning (existing data preserved)

# DELETE /api/learning/reset
# Removes: All behavioral data and learned patterns (GDPR compliance)
```

### Behavioral Events API
```python
# POST /api/learning/events
# Request: {"event_type": "task_completed", "hour": 14, "day_of_week": 2, "task_type_hash": "abc123"}
# Response: {"recorded": true}
# Note: Called by frontend after user actions (if learning enabled)
```

### Pattern Analysis API
```python
# GET /api/learning/patterns
# Returns: User's learned behavioral patterns in human-readable format

# GET /api/learning/insights
# Returns: Personalized insights based on learned patterns
# Response: {
#   "peak_productivity_hours": [9, 10, 14, 15],
#   "task_timing_preferences": {...},
#   "priority_tendencies": {...}
# }
```

### Adaptive Suggestions API
```python
# GET /api/adaptive/suggestions
# Returns: Personalized suggestions based on learned patterns

# POST /api/adaptive/suggestions/{id}/respond
# Request: {"action": "accept" | "reject" | "dismiss", "feedback": "optional"}
# Updates: Suggestion status and learns from user feedback
```

## 4. Implementation Phases

### Phase 1: Foundation & Privacy-Safe Data Collection ⏳ PLANNED
**Goal**: Establish privacy-preserving behavioral event capture system

**Backend Tasks**:
- [ ] Create `BehavioralEvent` model with privacy constraints
- [ ] Create `UserBehaviorProfile` model for aggregated patterns
- [ ] Implement `/api/learning/events` endpoint
- [ ] Add privacy validation: no content leakage checks
- [ ] Create database migrations
- [ ] Update `UserPreferences` with learning controls

**Frontend Tasks**:
- [ ] Create behavioral event tracking service
- [ ] Implement client-side event capture hooks
- [ ] Add learning opt-in UI component
- [ ] Create privacy disclosure modal
- [ ] Add learning status indicator

**Testing**:
- [ ] Test event capture without content leakage
- [ ] Verify privacy boundaries (no task titles/descriptions stored)
- [ ] Test opt-in/opt-out flows
- [ ] Validate data isolation per user

**Acceptance Criteria**:
- ✅ System captures timing, frequency, grouping data only
- ✅ No task content stored in behavioral events
- ✅ User can opt-in/opt-out at any time
- ✅ Privacy disclosure shown before enabling

**Priority**: P1 - Foundation for all learning features

---

### Phase 2: Pattern Analysis & Learning Engine ⏳ PLANNED
**Goal**: Build pattern analysis algorithms to learn from behavioral data

**Backend Tasks**:
- [ ] Create `LearningService` class
- [ ] Implement time-of-day pattern detection algorithm
- [ ] Implement task type timing pattern analysis
- [ ] Implement priority adjustment pattern detection
- [ ] Implement task grouping pattern analysis
- [ ] Create batch learning job (daily aggregation)
- [ ] Add pattern confidence scoring

**Pattern Detection Algorithms**:
```python
# Time-of-day analysis
def analyze_peak_hours(events: List[BehavioralEvent]) -> Dict[int, float]:
    """
    Identify hours when user is most productive.
    Returns: {hour: productivity_score}
    """
    # Aggregate completed tasks by hour
    # Weight recent events higher (exponential decay)
    # Normalize to 0-1 confidence scores

# Task type timing analysis
def analyze_type_timing(events: List[BehavioralEvent]) -> Dict[str, Dict[int, float]]:
    """
    Learn when user prefers to work on specific task types.
    Returns: {task_type_hash: {hour: frequency_score}}
    """
    # Group events by task_type_hash and hour
    # Calculate frequency distributions
    # Identify statistically significant patterns

# Priority adjustment patterns
def analyze_priority_patterns(events: List[BehavioralEvent]) -> Dict[str, Dict[str, float]]:
    """
    Learn how user typically adjusts task priorities.
    Returns: {from_priority: {to_priority: probability}}
    """
    # Track priority change sequences
    # Build transition probability matrix
    # Filter for consistent patterns (>3 occurrences)
```

**Testing**:
- [ ] Test pattern detection with synthetic behavioral data
- [ ] Verify pattern confidence scoring accuracy
- [ ] Test edge case: insufficient data
- [ ] Test edge case: conflicting patterns
- [ ] Validate batch learning job performance

**Acceptance Criteria**:
- ✅ System identifies time-of-day patterns with 70%+ confidence
- ✅ Task type timing patterns detected after 2 weeks of data
- ✅ Priority patterns identified with 60%+ accuracy
- ✅ System handles insufficient/conflicting data gracefully

**Priority**: P1 - Core learning capability

---

### Phase 3: Adaptive Suggestion Generation ⏳ PLANNED
**Goal**: Generate personalized suggestions based on learned patterns

**Backend Tasks**:
- [ ] Create `AdaptiveSuggestionService` class
- [ ] Implement priority adjustment suggestion logic
- [ ] Implement optimal timing suggestion logic
- [ ] Implement task grouping suggestion logic
- [ ] Add suggestion confidence filtering (min 60% confidence)
- [ ] Implement suggestion deduplication
- [ ] Create `/api/adaptive/suggestions` endpoint

**Suggestion Logic**:
```python
# Priority adjustment suggestions
def suggest_priority_adjustments(
    tasks: List[Task],
    profile: UserBehaviorProfile
) -> List[AdaptiveSuggestion]:
    """
    Suggest priority changes based on user's historical patterns.
    """
    # Analyze current task priorities
    # Compare against learned priority patterns
    # Generate suggestions for misaligned priorities
    # Filter by confidence threshold (60%)

# Optimal timing suggestions
def suggest_optimal_timing(
    task: Task,
    profile: UserBehaviorProfile
) -> Optional[AdaptiveSuggestion]:
    """
    Suggest best time to work on task based on type and user patterns.
    """
    # Hash task type (privacy-safe)
    # Lookup timing patterns for type
    # Identify peak hours for this task type
    # Generate time slot recommendation

# Grouping suggestions
def suggest_task_grouping(
    new_task: Task,
    existing_tasks: List[Task],
    profile: UserBehaviorProfile
) -> List[AdaptiveSuggestion]:
    """
    Suggest related tasks to batch together based on grouping patterns.
    """
    # Hash new task type
    # Lookup grouping patterns
    # Find related task types in existing tasks
    # Suggest batch processing
```

**Frontend Tasks**:
- [ ] Create `AdaptiveSuggestionsPanel` component
- [ ] Add suggestion card UI with reasoning display
- [ ] Implement suggestion accept/reject/dismiss actions
- [ ] Add confidence indicator visualization
- [ ] Create gradual introduction UX (max 3 suggestions/day initially)

**Testing**:
- [ ] Test suggestion generation with various profiles
- [ ] Verify confidence filtering works correctly
- [ ] Test suggestion deduplication
- [ ] Test user interaction flows (accept/reject/dismiss)
- [ ] Validate gradual introduction limits

**Acceptance Criteria**:
- ✅ Suggestions generated with 70%+ acceptance rate
- ✅ Confidence scores accurately reflect pattern strength
- ✅ Suggestions introduced gradually (max 3/day for new users)
- ✅ User can accept/reject/dismiss suggestions

**Priority**: P1 - Core user-facing feature

---

### Phase 4: Interactive Pattern Exploration ⏳ PLANNED
**Goal**: Provide transparency through interactive pattern visualization

**Frontend Tasks**:
- [ ] Create `LearningInsightsPage` component
- [ ] Build peak hours visualization (bar chart)
- [ ] Build task type timing heatmap
- [ ] Build priority adjustment flow diagram
- [ ] Add pattern strength indicators
- [ ] Create data points collected counter
- [ ] Add "Reset Learning Data" button with confirmation

**Backend Tasks**:
- [ ] Create `/api/learning/patterns` endpoint (formatted for UI)
- [ ] Add pattern explanation text generation
- [ ] Implement data export functionality (GDPR compliance)

**Visualizations**:
1. **Peak Productivity Hours**: Bar chart showing hours 0-23 with productivity scores
2. **Task Type Timing**: Heatmap showing when different task types are typically completed
3. **Priority Adjustment Patterns**: Sankey diagram showing priority change flows
4. **Grouping Patterns**: Network graph showing task types frequently done together

**Testing**:
- [ ] Test visualizations with various data profiles
- [ ] Test with minimal data (edge case)
- [ ] Test with conflicting patterns
- [ ] Verify explanations are clear and accurate
- [ ] Test data reset functionality

**Acceptance Criteria**:
- ✅ Users can view all learned patterns visually
- ✅ Pattern strength clearly communicated
- ✅ Explanations help users understand their habits
- ✅ 90% of users understand patterns within 5 minutes

**Priority**: P2 - Transparency and trust-building

---

### Phase 5: Feedback Loop & Model Improvement ⏳ PLANNED
**Goal**: Learn from user responses to improve suggestion quality

**Backend Tasks**:
- [ ] Implement feedback learning system
- [ ] Track suggestion acceptance/rejection patterns
- [ ] Adjust confidence scoring based on feedback
- [ ] Create model retraining job (weekly)
- [ ] Add A/B testing framework for suggestion algorithms
- [ ] Implement suggestion quality metrics

**Feedback Learning Logic**:
```python
def learn_from_feedback(
    suggestion: AdaptiveSuggestion,
    user_response: str,  # "accept", "reject", "dismiss"
    profile: UserBehaviorProfile
) -> None:
    """
    Adjust learning model based on user feedback.
    """
    if user_response == "accept":
        # Increase confidence for this pattern type
        # Boost similar suggestion generation
    elif user_response == "reject":
        # Decrease confidence for this pattern
        # Reduce similar suggestion frequency
    elif user_response == "dismiss":
        # Neutral - pattern may not apply in this context
        # Track dismissal reasons for pattern refinement
```

**Metrics & Monitoring**:
- Suggestion acceptance rate (target: 70%)
- Average confidence score (target: 0.75)
- Pattern learning time (target: <2 weeks)
- User satisfaction score (target: 4.0/5.0)

**Testing**:
- [ ] Test feedback incorporation accuracy
- [ ] Verify model improvements over time
- [ ] Test A/B framework with different algorithms
- [ ] Validate metrics collection

**Acceptance Criteria**:
- ✅ System learns from user feedback
- ✅ Suggestion quality improves over time
- ✅ Acceptance rate reaches 70%+ after 2 weeks
- ✅ Metrics tracked and accessible

**Priority**: P2 - Continuous improvement

---

## 5. Privacy & Security Architecture

### Privacy Guarantees

**What IS Learned (Privacy-Safe)**:
- ✅ Task completion timing (hour of day, day of week)
- ✅ Priority change frequency and patterns
- ✅ Task grouping behaviors (session-based)
- ✅ Aggregated statistical patterns

**What IS NOT Learned (Privacy-Protected)**:
- ❌ Task titles, descriptions, or content
- ❌ User-defined categories or tags
- ❌ Task metadata (notes, attachments)
- ❌ Any personally identifiable information

### Data Protection Measures

**Encryption**:
- All behavioral data encrypted at rest (AES-256)
- All API communications over HTTPS/TLS 1.3
- Database-level encryption for `behavioral_events` table

**Isolation**:
- Per-user data partitioning (no cross-user learning)
- User ID as partition key for all queries
- Row-level security policies in PostgreSQL

**Compliance**:
- GDPR Article 17 (Right to Erasure): DELETE /api/learning/reset
- GDPR Article 15 (Right to Access): GET /api/learning/patterns
- CCPA compliance: Opt-in required, data export available

**Audit Trail**:
- All learning operations logged in `ai_activity_log`
- Pattern changes tracked with timestamps
- User consent changes recorded

### Privacy Validation Tests
```python
def test_no_content_leakage():
    """Verify no task content stored in behavioral events."""
    event = create_behavioral_event(task)
    assert "title" not in event.to_dict()
    assert "description" not in event.to_dict()
    assert event.task_type_hash != task.title  # Must be one-way hash

def test_user_isolation():
    """Verify users cannot access other users' patterns."""
    response = client.get("/api/learning/patterns", auth=user_a_token)
    assert all(p.user_id == user_a.id for p in response.patterns)

def test_data_deletion():
    """Verify complete data removal on reset."""
    client.delete("/api/learning/reset", auth=user_token)
    events = get_behavioral_events(user_id)
    profile = get_behavior_profile(user_id)
    assert len(events) == 0
    assert profile is None or profile.data_points_collected == 0
```

## 6. Performance Requirements

### Latency Targets
- Event capture: <100ms (p95)
- Pattern analysis: <2s for on-demand query (p95)
- Suggestion generation: <1s (p95)
- Batch learning job: <30s for daily aggregation

### Scalability
- Support 10,000+ behavioral events per user
- Pattern analysis efficient with 6 months of data
- Suggestion generation scales with task count (<1000 tasks)

### Resource Constraints
- Batch learning job: <512MB memory
- Pattern storage: <10KB per user profile
- Database indexes on: user_id, timestamp, event_type

## 7. Edge Case Handling

### Insufficient Data
```python
def handle_insufficient_data(profile: UserBehaviorProfile) -> str:
    """Return appropriate message when data is insufficient."""
    if profile.data_points_collected < 20:
        return "Keep using the app! We need more data to learn your patterns."
    elif profile.data_points_collected < 50:
        return "Building your profile... We're starting to see patterns."
    else:
        return "Your behavioral profile is ready!"
```

### Conflicting Patterns
```python
def resolve_conflicting_patterns(patterns: List[Pattern]) -> Pattern:
    """Use recency and frequency weighting to resolve conflicts."""
    # Weight recent patterns higher (last 30 days = 2x weight)
    # Require minimum frequency threshold (>3 occurrences)
    # Fall back to default behavior if still ambiguous
```

### Pattern Drift
```python
def detect_pattern_drift(
    old_profile: UserBehaviorProfile,
    new_events: List[BehavioralEvent]
) -> bool:
    """Detect significant changes in user behavior over time."""
    # Calculate statistical divergence between old and new patterns
    # Trigger profile refresh if divergence > threshold
    # Notify user: "We've noticed your habits have changed. Update your patterns?"
```

## 8. Frontend Architecture

### Component Hierarchy
```
LearningInsightsPage
├── LearningControlPanel
│   ├── OptInToggle
│   ├── DataPointsCounter
│   └── ResetButton
├── PatternVisualization
│   ├── PeakHoursChart
│   ├── TaskTimingHeatmap
│   └── PriorityFlowDiagram
└── AdaptiveSuggestionsPanel
    └── SuggestionCard[]
        ├── ReasoningDisplay
        ├── ConfidenceIndicator
        └── ActionButtons (Accept/Reject/Dismiss)
```

### State Management
```typescript
// useLearning.ts
interface LearningState {
  enabled: boolean;
  dataPoints: number;
  patterns: BehaviorPatterns;
  suggestions: AdaptiveSuggestion[];
  loading: boolean;
  error: string | null;
}

function useLearning(): {
  state: LearningState;
  enableLearning: () => Promise<void>;
  disableLearning: () => Promise<void>;
  resetData: () => Promise<void>;
  respondToSuggestion: (id: string, action: string) => Promise<void>;
}
```

### Event Capture Hook
```typescript
// useBeha vioralTracking.ts
function useBehavioralTracking() {
  const { learningEnabled } = useLearning();

  const trackTaskCompletion = useCallback((task: Task) => {
    if (!learningEnabled) return;

    const event: BehavioralEvent = {
      event_type: "task_completed",
      hour_of_day: new Date().getHours(),
      day_of_week: new Date().getDay(),
      task_type_hash: hashTaskType(task),  // Privacy-safe hash
      timestamp: new Date().toISOString(),
    };

    api.post("/api/learning/events", event);
  }, [learningEnabled]);

  return { trackTaskCompletion, trackPriorityChange, trackTaskGrouping };
}
```

## 9. Testing Strategy

### Unit Tests
- Pattern detection algorithms (timing, priority, grouping)
- Confidence scoring calculations
- Privacy validation (no content leakage)
- Suggestion generation logic
- Feedback learning algorithms

### Integration Tests
- End-to-end learning flow (event → pattern → suggestion → feedback)
- Privacy compliance (GDPR/CCPA)
- User isolation (cross-user data access prevention)
- Data reset functionality
- API endpoint interactions

### Performance Tests
- Batch learning job performance with 10K+ events
- Pattern query performance with 6 months of data
- Suggestion generation latency
- Concurrent user load testing

### User Acceptance Tests
- Opt-in flow usability
- Pattern visualization comprehension
- Suggestion acceptance/rejection flows
- Data reset confirmation
- Privacy disclosure understanding

## 10. Monitoring & Observability

### Metrics to Track
- Learning adoption rate (% users opted in)
- Average data points per user
- Pattern detection success rate
- Suggestion acceptance rate (target: 70%)
- Average confidence score (target: 0.75)
- Time to first pattern detected (target: <2 weeks)
- API latency (p50, p95, p99)
- Error rates by endpoint

### Alerts
- Privacy violation detected (task content in behavioral event)
- Learning job failure
- Suggestion acceptance rate drops below 50%
- API latency exceeds 2s (p95)
- Data deletion failures

### Logging
```python
# Log all learning operations
logger.info("Learning enabled", extra={
    "user_id": user.id,
    "timestamp": now(),
    "action": "opt_in"
})

# Log pattern updates
logger.info("Patterns updated", extra={
    "user_id": user.id,
    "data_points": profile.data_points_collected,
    "patterns_detected": len(patterns),
    "confidence_avg": avg_confidence
})

# Log suggestion interactions
logger.info("Suggestion responded", extra={
    "user_id": user.id,
    "suggestion_id": suggestion.id,
    "action": "accept",
    "confidence": suggestion.confidence
})
```

## 11. Migration Plan

### Database Migrations
```sql
-- Migration 001: Create behavioral_events table
CREATE TABLE behavioral_events (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    event_type VARCHAR(50) NOT NULL,
    hour_of_day INTEGER NOT NULL CHECK (hour_of_day >= 0 AND hour_of_day <= 23),
    day_of_week INTEGER NOT NULL CHECK (day_of_week >= 0 AND day_of_week <= 6),
    task_type_hash VARCHAR(64) NOT NULL,
    session_id VARCHAR(64),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_behavioral_events_user_id ON behavioral_events(user_id);
CREATE INDEX idx_behavioral_events_timestamp ON behavioral_events(timestamp);

-- Migration 002: Create user_behavior_profiles table
CREATE TABLE user_behavior_profiles (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL UNIQUE REFERENCES users(id),
    peak_hours TEXT NOT NULL DEFAULT '{}',
    type_timing_patterns TEXT NOT NULL DEFAULT '{}',
    priority_adjustment_patterns TEXT NOT NULL DEFAULT '{}',
    grouping_patterns TEXT NOT NULL DEFAULT '{}',
    data_points_collected INTEGER NOT NULL DEFAULT 0,
    last_learning_date TIMESTAMP WITH TIME ZONE,
    model_version VARCHAR(10) NOT NULL DEFAULT '1.0',
    learning_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Migration 003: Create adaptive_suggestions table
CREATE TABLE adaptive_suggestions (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    suggestion_type VARCHAR(50) NOT NULL,
    target_task_id UUID REFERENCES tasks(id),
    message VARCHAR(500) NOT NULL,
    reasoning VARCHAR(2000) NOT NULL,
    confidence DECIMAL(3,2) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    pattern_evidence TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    responded_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_adaptive_suggestions_user_id ON adaptive_suggestions(user_id);
CREATE INDEX idx_adaptive_suggestions_status ON adaptive_suggestions(status);

-- Migration 004: Update user_preferences table
ALTER TABLE user_preferences
ADD COLUMN learning_enabled BOOLEAN NOT NULL DEFAULT FALSE,
ADD COLUMN learning_categories TEXT NOT NULL DEFAULT '["timing", "priority"]',
ADD COLUMN pattern_visibility VARCHAR(20) NOT NULL DEFAULT 'high';
```

### Rollback Plan
```sql
-- Rollback in reverse order
ALTER TABLE user_preferences DROP COLUMN pattern_visibility;
ALTER TABLE user_preferences DROP COLUMN learning_categories;
ALTER TABLE user_preferences DROP COLUMN learning_enabled;

DROP TABLE adaptive_suggestions;
DROP TABLE user_behavior_profiles;
DROP TABLE behavioral_events;
```

## 12. Success Criteria

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
- ✅ 40% improvement in task completion efficiency (self-reported)
- ✅ 30% reduction in manual prioritization effort
- ✅ 70% suggestion acceptance rate after initial learning period

## 13. Risks & Mitigations

### Risk 1: Low Adoption (Users Don't Opt-In)
**Impact**: High - Feature unused if users don't enable learning
**Mitigation**:
- Clear value proposition in opt-in modal
- Show sample insights before enabling
- Gradual introduction (not overwhelming)
- Easy opt-out to build trust

### Risk 2: Poor Suggestion Quality
**Impact**: High - Low acceptance rate damages trust
**Mitigation**:
- Minimum confidence threshold (60%)
- Start with high-confidence suggestions only
- Learn from feedback to improve
- Allow dismissal without penalty

### Risk 3: Privacy Concerns
**Impact**: Critical - Trust violation damages product
**Mitigation**:
- Automated privacy tests in CI/CD
- Regular privacy audits
- Clear disclosure and transparency
- One-click data deletion
- External security review

### Risk 4: Pattern Drift (User Behavior Changes)
**Impact**: Medium - Suggestions become irrelevant
**Mitigation**:
- Recency weighting in pattern analysis
- Automatic drift detection
- Notify user when patterns change significantly
- Allow manual pattern reset

### Risk 5: Insufficient Data
**Impact**: Medium - No patterns detected for new/light users
**Mitigation**:
- Clear messaging about data requirements
- Graceful degradation (fallback to Phase 4 suggestions)
- Show progress indicator (data points collected)
- Set expectations (2 weeks to learn patterns)

## 14. Definition of Done

### Code Complete
- [ ] All models created with migrations
- [ ] All API endpoints implemented and tested
- [ ] Frontend components built and integrated
- [ ] Privacy validation tests pass (100%)
- [ ] Performance benchmarks met

### Documentation Complete
- [ ] API documentation updated
- [ ] Privacy policy updated
- [ ] User guide for learning features
- [ ] ADR created for key decisions
- [ ] Runbook for learning job monitoring

### Testing Complete
- [ ] Unit tests (90%+ coverage)
- [ ] Integration tests (all flows)
- [ ] Privacy compliance tests (automated)
- [ ] Performance tests (latency targets met)
- [ ] User acceptance testing (5+ users)

### Deployment Ready
- [ ] Database migrations tested
- [ ] Rollback plan validated
- [ ] Monitoring and alerts configured
- [ ] Feature flag created (gradual rollout)
- [ ] Privacy review approved

---

## Next Steps

1. **Immediate**: Review this plan with stakeholders
2. **Week 1**: Implement Phase 1 (Foundation & Data Collection)
3. **Week 2**: Implement Phase 2 (Pattern Analysis Engine)
4. **Week 3**: Implement Phase 3 (Adaptive Suggestions)
5. **Week 4**: Implement Phase 4 (Pattern Exploration UI)
6. **Week 5**: Implement Phase 5 (Feedback Loop) + Testing + Polish

**Estimated Timeline**: 5-6 weeks for complete implementation
**Team Size**: 1-2 developers (full-time)
**Dependencies**: Phase 4 must be complete (autonomous features)
