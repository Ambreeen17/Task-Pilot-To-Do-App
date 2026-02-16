# ADR-003: User Control and Transparency Framework

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-01-14
- **Feature:** 005-adaptive-intelligence
- **Context:** Phase 5 introduces behavioral learning that could feel intrusive or opaque to users if not properly controlled and explained. Building on privacy-preserving architecture (ADR-001) and pattern analysis (ADR-002), the system must empower users to understand, control, and manage what the system learns. This decision addresses: How do we give users meaningful control over learning? How do we make learned patterns transparent and understandable? How do we build trust through visibility?

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Determines user adoption, trust, regulatory compliance
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Opt-in vs opt-out, full vs limited visibility
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects UX, APIs, data models, legal compliance
-->

## Decision

Implement a **comprehensive user control and transparency framework** with opt-in consent, full pattern visibility, and granular data management:

**User Control Mechanisms:**
- **Opt-In Learning:** Disabled by default, requires explicit user consent with privacy disclosure
- **Granular Categories:** Users select what to learn (timing patterns, priority patterns, grouping patterns)
- **Pause/Resume:** Learning can be temporarily disabled without deleting historical patterns
- **One-Click Data Reset:** Complete deletion of all behavioral events and learned patterns (GDPR Article 17)
- **Pattern Visibility Levels:** Users choose "Low" (minimal), "Medium" (summary), or "High" (full details)

**Transparency Features:**
- **Interactive Pattern Exploration:** Visual dashboards showing learned patterns with explanations
  - Peak Productivity Hours: Bar chart (hours 0-23) with frequency scores
  - Task Type Timing: Heatmap showing task_type_hash × hour_of_day patterns
  - Priority Adjustment Flows: Sankey diagram showing priority change transitions
  - Grouping Patterns: Network graph showing co-occurring task types
- **Data Points Counter:** Real-time display of behavioral events collected
- **Learning Status Indicator:** Clear UI showing whether learning is active/paused/disabled
- **Suggestion Reasoning:** Every adaptive suggestion includes "Why?" explanation linking to patterns
- **Confidence Display:** Visual indicators (🟢 high, 🟡 medium, 🟠 low) for pattern reliability

**UI/UX Components:**
```typescript
LearningInsightsPage
├── LearningControlPanel
│   ├── OptInToggle (with privacy disclosure modal)
│   ├── CategorySelector (timing, priority, grouping)
│   ├── DataPointsCounter ("2,341 events collected")
│   └── ResetButton (with confirmation: "This cannot be undone")
├── PatternVisualization
│   ├── PeakHoursChart (bar chart with tooltips)
│   ├── TaskTimingHeatmap (interactive, hover for details)
│   └── PriorityFlowDiagram (Sankey with percentages)
└── AdaptiveSuggestionsPanel
    └── SuggestionCard[]
        ├── Message ("Try completing this task at 2 PM")
        ├── ReasoningDisplay ("You typically finish similar tasks at this hour")
        ├── ConfidenceIndicator (🟢 85% confidence)
        └── ActionButtons (Accept/Reject/Dismiss)
```

**Progressive Disclosure Strategy:**
- **First-Time User:** Privacy disclosure modal explains what's learned (and what's not)
- **Initial Learning (0-20 events):** "Building your profile... X events collected"
- **Early Patterns (20-50 events):** "We're starting to see patterns. View insights?"
- **Mature Profile (50+ events):** Full pattern exploration available
- **Gradual Suggestions:** Max 3 suggestions/day initially, increase based on acceptance rate

**API Endpoints for Control:**
```python
# Learning control
POST /api/learning/enable          # Opt-in with consent timestamp
POST /api/learning/disable         # Pause without deleting data
DELETE /api/learning/reset         # Permanent data deletion

# Transparency
GET /api/learning/status           # Enabled, data_points, last_update
GET /api/learning/patterns         # Human-readable pattern summaries
GET /api/learning/insights         # Actionable insights from patterns
GET /api/learning/export           # GDPR data export (JSON format)

# Suggestion interaction
GET /api/adaptive/suggestions      # Pending suggestions with reasoning
POST /api/adaptive/suggestions/:id/respond  # Accept/Reject/Dismiss
```

## Consequences

### Positive

1. **User Trust:** Transparent learning builds confidence, increasing adoption rate
2. **Compliance:** Opt-in + data export + deletion satisfy GDPR/CCPA requirements
3. **Empowerment:** Users feel in control, reducing "creepy AI" perception
4. **Education:** Pattern visualization helps users understand their own work habits
5. **Debugging:** Full visibility enables users to identify and report inaccurate patterns
6. **Adoption:** Progressive disclosure avoids overwhelming new users
7. **Differentiation:** Transparency is competitive advantage vs black-box AI tools

### Negative

1. **Implementation Cost:** Pattern visualization requires significant frontend development
2. **Complexity:** Multiple control surfaces (opt-in, categories, pause, reset) increase UX complexity
3. **Support Burden:** Users may misunderstand patterns, generating support requests
4. **Over-Correction Risk:** Users may disable valuable learning due to single bad suggestion
5. **Performance:** Real-time pattern queries add API load for transparency features
6. **Design Challenge:** Making statistical patterns human-understandable requires careful UX
7. **Maintenance:** Visualization components require ongoing updates as patterns evolve

## Alternatives Considered

### Alternative A: Opt-Out with Minimal Visibility
**Approach:** Learning enabled by default, users opt-out if desired
**Components:**
- Learning starts automatically after signup
- Settings page allows disabling with single toggle
- No pattern visualization, only on/off control
- Suggestions show "Learn more" link but limited detail

**Why Rejected:**
- ❌ Privacy Risk: Opt-out violates GDPR requirement for "freely given, specific consent"
- ❌ Trust Erosion: Users feel surveilled, creates "creepy AI" perception
- ❌ Compliance: CCPA requires explicit opt-in for data collection
- ❌ Low Transparency: Users can't verify what system learned
- ❌ Support Issues: Users can't debug or report inaccurate patterns

### Alternative B: Full Transparency with No User Control
**Approach:** Always-on learning with complete pattern visibility
**Components:**
- Learning cannot be disabled (core feature)
- Full pattern exploration dashboard available
- Users can view but not delete learned patterns
- Suggestions can be ignored but learning continues

**Why Rejected:**
- ❌ Legal Risk: Violates GDPR "right to erasure" (Article 17)
- ❌ User Frustration: No way to correct persistent bad patterns
- ❌ Trust Damage: Forced learning feels coercive
- ❌ Adoption Blocker: Privacy-conscious users won't use feature
- ❌ Inflexibility: Cannot accommodate diverse user preferences

### Alternative C: Simplified Control with Aggregated Patterns Only
**Approach:** Single on/off toggle with high-level pattern summaries
**Components:**
- Opt-in toggle (only control surface)
- Simple dashboard: "You work best at 2-4 PM" (no charts)
- No granular category selection
- No raw event data visibility

**Why Rejected:**
- ❌ Limited Trust: Users want to verify claims ("Why does it think 2 PM is best?")
- ❌ Less Actionable: Summary insights don't enable behavior change
- ❌ Debugging Impossible: Cannot identify why patterns are wrong
- ❌ Missed Opportunity: Pattern visualization provides unique value
- ❌ Support Burden: Users request more detail, forcing reactive feature adds

### Decision Rationale

**Comprehensive Control + Full Transparency (chosen approach)** provides the best balance:
- ✅ Legal compliance: Opt-in + data export + deletion satisfy GDPR/CCPA
- ✅ User empowerment: Granular control builds trust and adoption
- ✅ Educational value: Pattern visualization helps users improve workflows
- ✅ Debugging support: Transparency enables issue identification
- ✅ Competitive advantage: Differentiation from black-box AI tools
- ⚖️ Trade implementation complexity for user trust - essential for Phase 5 adoption

## References

- Feature Spec: `specs/005-adaptive-intelligence/spec.md` (FR-006, FR-007, FR-010, FR-012, FR-013)
- Implementation Plan: `specs/005-adaptive-intelligence/plan.md` (sections 4.1, 4.4, 8)
- Related ADRs: ADR-001 (Privacy Architecture), ADR-002 (Pattern Analysis)
- Success Criteria: SC-005 (90% understand controls within 5 minutes)
- User Stories: US3 (Privacy-Preserving Learning), US2 (Personalized Workflow Suggestions)
- Compliance: GDPR Articles 15 (Access), 17 (Erasure), CCPA Section 1798.100
