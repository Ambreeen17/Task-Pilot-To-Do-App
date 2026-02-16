# Agent 6: Insight Agent

**Responsibility**: Productivity trends, habit summaries, improvement suggestions

**Priority**: P2 (Value-Add - Helps users improve workflows)

---

## Task 6.1: Implement Peak Productivity Hours Visualization

**Description**: Interactive chart showing user's most productive hours

**Acceptance Criteria**:
- [ ] Create bar chart component (hours 0-23 on x-axis)
- [ ] Fetch peak_hours data from GET /api/learning/patterns
- [ ] Display productivity scores as bar heights
- [ ] Highlight top 3 peak hours with distinct color
- [ ] Add hover tooltip: "3 PM - 85% productivity (based on 24 completions)"
- [ ] Show data freshness: "Updated 2 days ago"
- [ ] Responsive design: works on mobile and desktop

**Files**:
- `frontend/src/components/PeakHoursChart.tsx` (new)
- `frontend/src/pages/LearningInsightsPage.tsx` (new)
- `frontend/src/services/learningApi.ts` (extend)

**Dependencies**: Task 3.7 (Peak hours pattern)

**Estimated Effort**: 6 hours

---

## Task 6.2: Implement Task Type Timing Heatmap

**Description**: Visual heatmap showing when different task types are typically completed

**Acceptance Criteria**:
- [ ] Create heatmap component (task types × hours grid)
- [ ] Fetch type_timing_patterns from API
- [ ] Color intensity: darker = higher frequency
- [ ] Hover tooltip: "Email tasks at 9 AM - 12 completions"
- [ ] Legend: explain color scale
- [ ] Handle sparse data: show "Insufficient data" for <5 events
- [ ] Allow filtering by date range (last 7/30/90 days)

**Files**:
- `frontend/src/components/TaskTimingHeatmap.tsx` (new)
- `backend/src/routers/learning.py` (extend - add date range filter)

**Dependencies**: Task 3.7 (Type timing pattern)

**Estimated Effort**: 8 hours

---

## Task 6.3: Implement Priority Flow Diagram

**Description**: Sankey diagram showing priority change flows

**Acceptance Criteria**:
- [ ] Create Sankey diagram component
- [ ] Fetch priority_adjustment_patterns from API
- [ ] Visualize transitions: Low → Medium → High
- [ ] Show percentages on flows: "60% of Medium tasks become High"
- [ ] Color flows by direction (upgrade = green, downgrade = red)
- [ ] Add summary text: "You tend to upgrade priorities more than downgrade"
- [ ] Click flow to see example tasks (anonymized hashes)

**Files**:
- `frontend/src/components/PriorityFlowDiagram.tsx` (new)
- `frontend/src/lib/sankeyChart.ts` (new)

**Dependencies**: Task 3.7 (Priority pattern)

**Estimated Effort**: 9 hours

---

## Task 6.4: Implement Productivity Trends Analysis

**Description**: Week-over-week and month-over-month productivity metrics

**Acceptance Criteria**:
- [ ] Calculate weekly task completion rates
- [ ] Compare current week vs previous weeks (4-week trend)
- [ ] Metrics to track:
  - Tasks completed per day
  - Average time-to-completion
  - Priority distribution (% Low/Medium/High)
  - Peak hour consistency
- [ ] Visualize as line charts with trend lines
- [ ] Add insights: "Your productivity is up 15% this week! 🎉"
- [ ] API endpoint: GET /api/learning/insights/trends

**Files**:
- `backend/src/learning/insights/productivity.py` (new)
- `frontend/src/components/ProductivityTrends.tsx` (new)
- `backend/tests/test_productivity_insights.py` (new)

**Dependencies**: Task 3.2 (Event storage)

**Estimated Effort**: 10 hours

---

## Task 6.5: Implement Habit Summaries

**Description**: Natural language summaries of user's work habits

**Acceptance Criteria**:
- [ ] Generate habit summary text from patterns:
  - "You're most productive at 2-4 PM 🌟"
  - "You typically prioritize tasks on Monday mornings"
  - "You prefer to batch similar tasks together"
  - "Your work schedule is consistent week-to-week"
- [ ] Personalize based on strongest patterns (confidence > 0.75)
- [ ] Limit to top 5 most significant habits
- [ ] Add "Learn More" links to detailed pattern visualizations
- [ ] API endpoint: GET /api/learning/insights/habits

**Files**:
- `backend/src/learning/insights/habits.py` (new)
- `frontend/src/components/HabitSummary.tsx` (new)
- `backend/tests/test_habit_summaries.py` (new)

**Dependencies**: Task 3.7 (All patterns)

**Estimated Effort**: 7 hours

---

## Task 6.6: Implement Workflow Improvement Suggestions

**Description**: Actionable recommendations to improve productivity

**Acceptance Criteria**:
- [ ] Analyze patterns for improvement opportunities:
  - "Try scheduling difficult tasks during your 2-4 PM peak hours"
  - "You're most effective on Tuesdays - consider front-loading priorities"
  - "Group similar tasks together to match your natural workflow"
  - "Your afternoon productivity drops - consider shorter work blocks"
- [ ] Generate 3-5 personalized recommendations
- [ ] Rank by potential impact (estimated time savings)
- [ ] Include "Try This" action button to apply suggestion
- [ ] Track which suggestions are followed

**Files**:
- `backend/src/learning/insights/recommendations.py` (new)
- `frontend/src/components/ImprovementSuggestions.tsx` (new)
- `backend/tests/test_recommendations.py` (new)

**Dependencies**: Task 6.4, Task 6.5

**Estimated Effort**: 9 hours

---

## Task 6.7: Implement Data Points Counter and Progress Indicator

**Description**: Show users how much data has been collected and learning progress

**Acceptance Criteria**:
- [ ] Display total behavioral events collected
- [ ] Show breakdown by event type:
  - Task completions: 156
  - Priority changes: 42
  - Task groupings: 28
- [ ] Add progress bar: "Building your profile (28/50 events needed)"
- [ ] Milestones:
  - 0-20 events: "Just getting started"
  - 20-50 events: "Early patterns emerging"
  - 50+ events: "Profile ready! 🎉"
- [ ] Show days since learning enabled
- [ ] API endpoint: GET /api/learning/status

**Files**:
- `frontend/src/components/LearningProgress.tsx` (new)
- `backend/src/routers/learning.py` (extend)

**Dependencies**: Task 3.2 (Event storage)

**Estimated Effort**: 5 hours

---

**Total Agent Effort**: 54 hours
