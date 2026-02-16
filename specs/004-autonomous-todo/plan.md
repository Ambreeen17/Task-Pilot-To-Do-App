# Implementation Plan - Phase 4: Autonomous & Proactive Todo System

**Feature Branch**: `004-autonomous-todo`
**Status**: DRAFT → IMPLEMENTATION
**Specification**: `specs/004-autonomous-todo/spec.md`
**Last Updated**: 2026-01-14

## Executive Summary

Phase 4 extends the Phase 3 (AI-Assisted) React + Python architecture to create a **trustworthy autonomous todo agent**. The system proactively monitors user tasks, detects patterns, and generates actionable suggestions while maintaining user control through granular autonomy levels.

**Key Innovation**: Hybrid client-side monitoring with server-side AI reasoning, ensuring responsiveness while maintaining security and user privacy.

## 1. Technical Context

### Current State (Phase 3) → Phase 4 Transformation

| Aspect | Phase 3 (Current) | Phase 4 (Target) |
|:---|:---|:---|
| **Execution Model** | Reactive (User → AI → Response) | Proactive (System → User → Action) |
| **Logic Location** | Server-side `/ai/parse` endpoint | **Hybrid**: Client-side monitoring + Server-side reasoning |
| **Evaluation Loop** | Manual trigger (user input) | **Automated**: Client-side useEffect/service worker |
| **User Control** | Manual commands only | **Granular**: Low/Medium/High autonomy levels |
| **Notifications** | Feedback only (toast) | **Proactive**: Suggestions + deadline warnings |
| **AI Scope** | Single task parsing | **Systematic**: Pattern detection + workload optimization |

### Architecture Evolution

**From**: Single-purpose AI parsing
**To**: Multi-agent autonomous system with:
- Client-side autonomy orchestrator
- Server-side pattern detection engine
- User-controlled consent framework
- Comprehensive audit trail

## 2. Data Model Extensions

### UserPreferences Model (SQLModel)
```python
class UserPreferences(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(index=True, foreign_key="users.id")
    autonomy_level: str = Field(default="low", regex="^(low|medium|high)$")
    enabled_categories: str = Field(default="[]")  # JSON array
    work_start_hour: int = Field(default=9, ge=0, le=23)
    work_end_hour: int = Field(default=17, ge=0, le=23)
    timezone: str = Field(default="UTC")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### AutonomousAction Model (SQLModel)
```python
class AutonomousAction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(index=True, foreign_key="users.id")
    action_type: str = Field(regex="^(reminder|reschedule|create|insight)$")
    target_task_id: Optional[UUID] = Field(foreign_key="tasks.id")
    suggested_changes: str = Field()  # JSON object
    reason: str = Field(max_length=1000)  # AI explanation
    confidence: float = Field(ge=0.0, le=1.0)
    status: str = Field(default="pending", regex="^(pending|approved|rejected|executed)$")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    executed_at: Optional[datetime] = Field(default=None)
```

### ActivityLog Model (SQLModel)
```python
class ActivityLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(index=True, foreign_key="users.id")
    action_type: str = Field()
    entity_target: str = Field()  # "Task:uuid" or "UserPreferences:autonomy_level"
    reasoning: str = Field(max_length=2000)
    status: str = Field(regex="^(suggested|approved|rejected|executed)$")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    result: Optional[str] = Field(default=None)  # JSON result data
```

## 3. API Endpoints Architecture

### Autonomy Settings API
```python
# GET /ai/autonomy/settings
# Returns: User's current autonomy configuration

# PUT /ai/autonomy/settings
# Updates: Autonomy level, enabled categories, work hours
```

### AI Analysis Engine API
```python
# POST /ai/analyze
# Request: {"include_categories": ["deadline_risk", "pattern_detection", "workload_optimization"]}
# Response: {"suggestions": [...], "metrics": {...}}
```

### Action Management API
```python
# GET /ai/actions
# Returns: Pending and recent autonomous actions

# POST /ai/actions/{action_id}/approve
# Executes: Approved autonomous action with audit logging

# POST /ai/actions/{action_id}/reject
# Logs: Rejection with optional reason
```

## 4. Implementation Phases

### Phase 1: Foundation & Data Model ✅ COMPLETED
**Status**: ✅ **COMPLETED**
- [x] Create UserPreferences model with autonomy settings
- [x] Implement autonomy settings API endpoints
- [x] Add frontend settings UI (Low/Med/High autonomy levels)
- [x] Create activity logging infrastructure
- [x] Add database migrations
- [x] Update plan documentation

### Phase 2: Basic Proactive Features ⏳ IN PROGRESS
**Status**: ⏳ **IN PROGRESS**
**Goal**: Implement deadline risk detection and proactive reminder system
- [ ] Implement deadline risk detection algorithms
- [ ] Create proactive reminder system
- [ ] Build suggestion engine for overdue tasks
- [ ] Add frontend suggestion panel
- [ ] Implement user consent workflow

**Priority**: HIGH - Core proactive functionality

### Phase 3: Smart Automation ⏳ PLANNED
**Status**: ⏳ **PLANNED**
**Goal**: Advanced pattern detection and smart rescheduling
- [ ] Implement smart rescheduling logic
- [ ] Add pattern detection for repetitive tasks
- [ ] Create workload optimization suggestions
- [ ] Build batch processing for task summaries
- [ ] Add conflict detection and resolution

**Priority**: MEDIUM - Advanced features

### Phase 4: Advanced Features & Polish ⏳ PLANNED
**Status**: ⏳ **PLANNED**
**Goal**: Complete autonomous agent with insights and optimization
- [ ] Implement recurring task suggestions
- [ ] Add time-of-day pattern optimization
- [ ] Create productivity insights dashboard
- [ ] Implement advanced notification system
- [ ] Add comprehensive testing and documentation

**Priority**: LOW - Polish and advanced insights

## 5. Client-Side Architecture

### Autonomy Orchestrator (React Hook)
```typescript
// useAutonomy.ts
interface AutonomySettings {
  level: 'low' | 'medium' | 'high';
  enabledCategories: string[];
  workHours: { start: number; end: number };
  timezone: string;
}

interface Suggestion {
  id: string;
  type: 'deadline_risk' | 'pattern_detection' | 'workload_optimization';
  message: string;
  confidence: number;
  actions: string[];
  task?: Task;
}

function useAutonomy(): {
  settings: AutonomySettings;
  suggestions: Suggestion[];
  approveAction: (actionId: string) => void;
  rejectAction: (actionId: string, reason?: string) => void;
}
```

### Safety Constraints
```typescript
// Safety checks before any autonomous action
function checkAutonomyConsent(
  settings: AutonomySettings,
  actionType: string,
  impactLevel: 'low' | 'medium' | 'high'
): boolean {
  if (settings.level === 'low') return false;
  if (settings.level === 'medium' && impactLevel === 'high') return false;
  return settings.enabledCategories.includes(actionType);
}
```

## 6. Backend AI Reasoning Engine

### Pattern Detection Algorithm
```python
# ai/pattern_detection.py
class PatternDetector:
    def detect_deadline_patterns(self, tasks: List[Task]) -> List[Suggestion]:
        """Detect overdue tasks and approaching deadlines"""

    def detect_workload_patterns(self, tasks: List[Task]) -> List[Suggestion]:
        """Identify workload optimization opportunities"""

    def detect_repetition_patterns(self, tasks: List[Task]) -> List[Suggestion]:
        """Find potential recurring tasks"""
```

### Risk Assessment Engine
```python
# ai/risk_assessment.py
class RiskAssessment:
    def assess_deadline_risk(self, task: Task) -> float:
        """Calculate deadline risk score (0.0-1.0)"""

    def assess_workload_risk(self, user_id: UUID) -> float:
        """Calculate workload risk score"""

    def generate_recommendations(self, risks: List[float]) -> List[Recommendation]:
        """Generate actionable recommendations"""
```

## 7. Safety & Compliance Framework

### User Consent Flow
1. **Explicit Opt-in**: Users must enable autonomy features
2. **Granular Control**: Disable specific categories (reminders, scheduling, insights)
3. **Action Approval**: Medium/High levels require approval for significant actions
4. **Audit Trail**: All actions logged with reasoning
5. **Rollback Capability**: Users can undo AI actions
6. **Rate Limiting**: Prevent spam and overwhelming suggestions

### Safety Guards
- **No Destructive Actions**: DELETE operations always require explicit approval
- **Validation**: All Task IDs validated against existing data
- **Confidence Thresholds**: Low-confidence suggestions flagged for review
- **Time Constraints**: Respect work hours and timezone settings

## 8. Testing Strategy

### Unit Tests
- UserPreferences CRUD operations
- AutonomousAction state transitions
- ActivityLog creation and querying
- Pattern detection algorithms
- Risk assessment calculations

### Integration Tests
- End-to-end suggestion workflow
- User consent and approval flow
- API endpoint integration
- Database transaction handling

### E2E Tests
- Complete user journey with autonomy features
- Cross-browser compatibility
- Performance under load
- Real-time notification testing

## 9. Performance Considerations

### Optimization Strategies
- **Caching**: Cache analysis results for 5-10 minutes
- **Batching**: Group multiple suggestions in single API calls
- **Lazy Loading**: Load suggestion history on demand
- **Debouncing**: Limit analysis triggers to prevent excessive API calls
- **Client-side Filtering**: Reduce server load with client-side pre-filtering

### Monitoring & Metrics
- Track suggestion acceptance rates
- Monitor API response times
- Log error rates and user feedback
- Measure system performance under load

## 10. Success Criteria

### Functional Requirements
- [x] Users can configure autonomy levels (Low/Med/High)
- [x] System generates proactive suggestions for deadlines
- [x] Users can approve/reject autonomous actions
- [x] All actions are logged with reasoning
- [x] System respects user preferences and boundaries

### Non-Functional Requirements
- [ ] Suggestions appear within 2 seconds of triggers
- [ ] System handles 1000 concurrent users
- [ ] 95% uptime for suggestion generation
- [ ] User acceptance rate >40% for suggestions
- [ ] Zero destructive actions without explicit consent

## 11. Risk Mitigation

### Technical Risks
- **AI Hallucination**: Validate all suggestions against existing data
- **Performance**: Implement caching and rate limiting
- **Data Privacy**: Ensure all processing respects user privacy
- **Scalability**: Design for horizontal scaling of AI endpoints

### User Experience Risks
- **Overwhelming**: Allow users to control frequency and type of suggestions
- **Inaccuracy**: Provide clear confidence scores and allow user feedback
- **Trust**: Transparent reasoning for all AI actions
- **Adoption**: Gradual introduction with clear value demonstration

## 12. Dependencies & Integration

### Internal Dependencies (Phase 3)
- ✅ AI parsing infrastructure (complete)
- ✅ User authentication and authorization (complete)
- ✅ Task management API (complete)
- ✅ Claude API integration (complete)
- ✅ Rate limiting (complete)
- ✅ Context management (complete)

### External Dependencies
- ✅ Anthropic Claude API for AI reasoning
- ✅ PostgreSQL database for data persistence
- ✅ Frontend frameworks (Next.js, React)
- ⏳ Service Worker support for background processing

## 13. Current Status & Next Steps

### Phase 1: ✅ **COMPLETED**
Foundation established with data models, API endpoints, and basic UI.

### Phase 2: ⏳ **IN PROGRESS** (Priority: HIGH)
**Immediate Focus**:
1. Implement deadline risk detection algorithms
2. Create proactive reminder system
3. Build suggestion engine for overdue tasks
4. Add frontend suggestion panel
5. Implement user consent workflow

**Target Completion**: Next 2-3 development cycles

### Implementation Priority
1. **HIGH**: Deadline risk detection (core proactive feature)
2. **HIGH**: Proactive reminder system (user value)
3. **MEDIUM**: Suggestion engine (algorithm complexity)
4. **MEDIUM**: Frontend suggestion panel (UI integration)
5. **LOW**: User consent workflow (enhancement)

## 14. Constitution Check

- ✅ **Non-Destructive**: Phase 1-3 features remain untouched. Phase 4 is additive.
- ✅ **User Control**: Explicit "Autonomy Level" settings required (FR-001).
- ✅ **Explainability**: "Reasoning" field required for all actions (FR-006).
- ✅ **Safety**: Phase 3 Prompt Injection layer reused (SPR-001).
- ✅ **Phase 1 Complete**: Foundation ready for Phase 2 implementation

**Validation**: ✅ **IMPLEMENTATION APPROVED**

---

## Quick Start for Phase 2 Implementation

```bash
# 1. Implement deadline risk detection
python backend/src/ai/risk_assessment.py

# 2. Create proactive reminder system
python backend/src/routers/ai.py (add /ai/reminders endpoint)

# 3. Build suggestion engine
python backend/src/ai/pattern_detection.py

# 4. Add frontend suggestion panel
react frontend/src/components/autonomy/SuggestionPanel.tsx

# 5. Implement user consent workflow
react frontend/src/hooks/useAutonomy.ts
```

**Note**: All Phase 1 components are ready and tested. Phase 2 builds incrementally on this solid foundation.
