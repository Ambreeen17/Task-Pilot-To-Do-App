# Tasks: Phase 3 — AI-Assisted Todo

**Input**: Design documents from `/specs/003-ai-assisted-todo/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are OPTIONAL for this feature - not explicitly requested in specification. Focus on implementation with manual testing per quickstart.md.

**Organization**: Tasks are grouped by user story (P1, P2, P3) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Web app structure: `backend/src/`, `frontend/src/`
- Backend AI module: `backend/src/ai/`
- Frontend AI components: `frontend/src/components/`, `frontend/src/app/chat/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Phase 3 project initialization and dependency setup

- [ ] T001 Install Anthropic Python SDK in backend/requirements.txt (anthropic==0.25.0)
- [ ] T002 [P] Install python-dateutil in backend/requirements.txt (python-dateutil==2.8.2)
- [ ] T003 [P] Install frontend date-fns dependency in frontend/package.json (date-fns@^3.0.0)
- [ ] T004 Update backend/.env.example with ANTHROPIC_API_KEY, AI rate limit configs, AI feature flags per quickstart.md
- [ ] T005 [P] Create backend/src/ai/ module structure with __init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core AI infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Run database migration to add 6 AI tables per data-model.md (ai_conversations, ai_messages, parsed_task_intents, task_summaries, ai_insights, user_contexts)
- [ ] T007 [P] Create backend/src/models/ai_conversation.py (AIConversation SQLModel entity with status validation)
- [ ] T008 [P] Create backend/src/models/ai_message.py (AIMessage SQLModel entity with role validation)
- [ ] T009 [P] Create backend/src/models/parsed_task_intent.py (ParsedTaskIntent SQLModel entity with confidence scores JSON field)
- [ ] T010 [P] Create backend/src/models/task_summary.py (TaskSummary SQLModel entity with metrics JSON field)
- [ ] T011 [P] Create backend/src/models/ai_insight.py (AIInsight SQLModel entity with insight_type enum)
- [ ] T012 [P] Create backend/src/models/user_context.py (UserContext SQLModel entity for in-memory backup)
- [ ] T013 Implement Claude API client wrapper in backend/src/ai/client.py with error handling and retries
- [ ] T014 [P] Create prompt templates directory backend/src/ai/prompts/ with parse_task.txt, generate_summary.txt, create_insights.txt per research.md
- [ ] T015 Implement rate limiter in backend/src/ai/rate_limiter.py (token bucket, 100 req/user/day) per research.md
- [ ] T016 [P] Implement context manager in backend/src/services/context_manager.py (hybrid memory+DB, 10-message window, 10-min timeout) per research.md
- [ ] T017 Register AI routers in backend/src/main.py (ai.py, chat.py) with rate limit middleware

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Natural Language Task Creation (Priority: P1) 🎯 MVP

**Goal**: Enable users to create tasks using natural language input with AI parsing of title, priority, and due date/time

**Independent Test**: Send natural language input "Buy groceries tomorrow at 5pm" via API and verify task created with correct structured data (title: "Buy groceries", due_date: tomorrow, due_time: 17:00)

### Implementation for User Story 1

- [ ] T018 [P] [US1] Implement date/time parser helper in backend/src/ai/parser.py using python-dateutil for relative dates (tomorrow, next Friday, in 3 days) per research.md
- [ ] T019 [US1] Implement natural language parser in backend/src/ai/parser.py with parse_task() function calling Claude API using parse_task.txt prompt template
- [ ] T020 [US1] Implement confidence score calculation in backend/src/ai/parser.py (title, priority, due_date scores 0.0-1.0)
- [ ] T021 [US1] Implement POST /ai/parse endpoint in backend/src/routers/ai.py per contracts/api/ai-parse.yaml (accepts text, returns ParsedTaskIntent with confidence scores and recommendation)
- [ ] T022 [US1] Implement POST /ai/parse/confirm endpoint in backend/src/routers/ai.py to create Phase 2 task from confirmed intent per contracts/api/ai-parse.yaml
- [ ] T023 [P] [US1] Implement POST /ai/parse/reject endpoint in backend/src/routers/ai.py to log rejection with optional reason per contracts/api/ai-parse.yaml
- [ ] T024 [P] [US1] Implement GET /ai/rate-limit endpoint in backend/src/routers/ai.py to return RateLimitStatus per contracts/api/ai-parse.yaml
- [ ] T025 [US1] Add graceful degradation for AI service failures in parse endpoint (fallback to Phase 2 manual entry) per research.md error handling
- [ ] T026 [US1] Add FR-014 3-strike fallback logic (after 3 parse failures, redirect to manual form) in parse endpoint

**Checkpoint**: At this point, User Story 1 should be fully functional - users can create tasks via natural language API

---

## Phase 4: User Story 2 - AI Task Interpretation Display (Priority: P1) 🎯 MVP

**Goal**: Show users how AI interpreted their input with confidence indicators and allow editing before task creation

**Independent Test**: Enter natural language via UI, view interpretation breakdown with confidence scores, edit fields, and confirm to create task

### Implementation for User Story 2

- [ ] T027 [P] [US2] Create frontend/src/types/ai.ts with TypeScript types for ParsedTaskIntent, ConfidenceScores, RateLimitStatus
- [ ] T028 [P] [US2] Create frontend/src/services/aiApi.ts with API wrappers for /ai/parse, /ai/parse/confirm, /ai/parse/reject per contracts/api/ai-parse.yaml
- [ ] T029 [P] [US2] Create ConfidenceIndicator component in frontend/src/components/ConfidenceIndicator.tsx (progress bar with color coding: green ≥0.9, amber 0.7-0.89, red <0.7) per contracts/ui/ai-feedback-panel.md
- [ ] T030 [US2] Create AIInterpretationPanel component in frontend/src/components/AIInterpretationPanel.tsx with field display, confidence indicators, and edit/confirm/reject actions per contracts/ui/ai-feedback-panel.md
- [ ] T031 [US2] Add edit mode to AIInterpretationPanel with form fields (title input max 200 chars, priority dropdown, date picker, time picker) per contracts/ui/ai-feedback-panel.md
- [ ] T032 [US2] Implement form validation in AIInterpretationPanel (title required, time requires date, 100% confidence after edit) per contracts/ui/ai-feedback-panel.md
- [ ] T033 [US2] Add recommendation badge to AIInterpretationPanel (auto-accept ≥0.9 all fields, review 0.7-0.89, clarification <0.7) per contracts/ui/ai-feedback-panel.md
- [ ] T034 [US2] Implement confirm handler in AIInterpretationPanel calling /ai/parse/confirm and creating task per contracts/ui/ai-feedback-panel.md
- [ ] T035 [US2] Implement reject handler in AIInterpretationPanel calling /ai/parse/reject with optional feedback per contracts/ui/ai-feedback-panel.md
- [ ] T036 [US2] Add success/error states to AIInterpretationPanel (success message with task link, error with retry button) per contracts/ui/ai-feedback-panel.md
- [ ] T037 [US2] Integrate AIInterpretationPanel into Phase 2 task creation workflow (show after AI parse, hide after confirm/reject)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - NL parsing with explainability UI

---

## Phase 5: User Story 3 - Conversational Task Interface (Priority: P2)

**Goal**: Provide chat-based interface for natural task management interactions (queries, modifications, task creation)

**Independent Test**: Open chat interface, type "What tasks do I have today?" and verify AI lists today's tasks, then type "Mark groceries as done" and verify task status updates

### Implementation for User Story 3

- [ ] T038 [P] [US3] Implement conversation service in backend/src/services/conversation_service.py with create_conversation(), add_message(), get_active_conversation() per data-model.md
- [ ] T039 [US3] Implement intent detection in backend/src/ai/parser.py to classify user input (task_creation, task_query, task_modification, summary_request, general) for routing
- [ ] T040 [US3] Implement task query handler in backend/src/services/conversation_service.py to process "What tasks..." queries with filter logic (today, overdue, high priority, etc.)
- [ ] T041 [US3] Implement task modification handler in backend/src/services/conversation_service.py to process "Mark X as done" or "Change priority to High" commands with task lookup
- [ ] T042 [P] [US3] Implement GET /chat/conversations endpoint in backend/src/routers/chat.py to list user conversations per contracts/api/ai-conversation.yaml
- [ ] T043 [P] [US3] Implement POST /chat/conversations endpoint in backend/src/routers/chat.py to create new conversation per contracts/api/ai-conversation.yaml
- [ ] T044 [P] [US3] Implement GET /chat/conversations/{id} endpoint in backend/src/routers/chat.py to get conversation with messages per contracts/api/ai-conversation.yaml
- [ ] T045 [P] [US3] Implement DELETE /chat/conversations/{id} endpoint in backend/src/routers/chat.py to close conversation per contracts/api/ai-conversation.yaml
- [ ] T046 [US3] Implement POST /chat/conversations/{id}/messages endpoint in backend/src/routers/chat.py with intent routing and AI response generation per contracts/api/ai-conversation.yaml
- [ ] T047 [P] [US3] Implement GET /chat/context endpoint in backend/src/routers/chat.py to get user's active context per contracts/api/ai-conversation.yaml
- [ ] T048 [P] [US3] Implement DELETE /chat/context endpoint in backend/src/routers/chat.py to clear context (FR-021) per contracts/api/ai-conversation.yaml
- [ ] T049 [P] [US3] Create frontend/src/types/conversation.ts with Conversation, Message, UserContext TypeScript types
- [ ] T050 [P] [US3] Create useChat hook in frontend/src/hooks/useChat.ts with sendMessage(), confirmIntent(), clearContext(), closeConversation() per contracts/ui/chat-interface.md
- [ ] T051 [P] [US3] Create MessageBubble component in frontend/src/components/MessageBubble.tsx (user right-aligned blue, assistant left-aligned gray) per contracts/ui/chat-interface.md
- [ ] T052 [P] [US3] Create MessageInput component in frontend/src/components/MessageInput.tsx (auto-expand textarea, 10k char limit, character count, send button) per contracts/ui/chat-interface.md
- [ ] T053 [P] [US3] Create MessageList component in frontend/src/components/MessageList.tsx (scrollable, virtual scrolling for 50+ messages, chronological order) per contracts/ui/chat-interface.md
- [ ] T054 [US3] Create ChatInterface component in frontend/src/components/ChatInterface.tsx assembling header, MessageList, MessageInput with useChat hook per contracts/ui/chat-interface.md
- [ ] T055 [US3] Add ChatHeader to ChatInterface with conversation status, clear context, close conversation controls per contracts/ui/chat-interface.md
- [ ] T056 [US3] Integrate AIInterpretationPanel into ChatInterface (show when parsed_intent present in assistant message) per contracts/ui/chat-interface.md
- [ ] T057 [US3] Create chat page in frontend/src/app/chat/page.tsx with ChatInterface component and authentication guard
- [ ] T058 [US3] Add loading states to ChatInterface (pulsing indicator during AI response, disabled send button) per contracts/ui/chat-interface.md
- [ ] T059 [US3] Add error states to ChatInterface (rate limit exceeded banner with reset time, AI unavailable with fallback link, network error with retry) per contracts/ui/chat-interface.md
- [ ] T060 [US3] Add keyboard navigation to ChatInterface (Enter to send, Shift+Enter for newline, Escape to cancel, Tab order) per contracts/ui/chat-interface.md accessibility
- [ ] T061 [US3] Add ARIA labels and screen reader support to ChatInterface (aria-live for new messages, role="log" for message list) per contracts/ui/chat-interface.md accessibility

**Checkpoint**: All P1 and P2 core stories complete - NL creation, explainability, and conversational interface functional

---

## Phase 6: User Story 4 - AI Task Summaries (Priority: P2)

**Goal**: Generate daily, weekly, and monthly task summaries with productivity metrics automatically

**Independent Test**: Request "Give me my daily summary" via chat and verify response includes completed count, pending count, priority breakdown, and overdue items

### Implementation for User Story 4

- [ ] T062 [P] [US4] Implement summary metrics calculator in backend/src/ai/summarizer.py to compute total_tasks, completed, pending, overdue, completion_rate, priority_distribution from task history
- [ ] T063 [US4] Implement summary text generator in backend/src/ai/summarizer.py calling Claude API with generate_summary.txt prompt and metrics JSON per research.md
- [ ] T064 [P] [US4] Implement GET /ai/summaries endpoint in backend/src/routers/ai.py to list user summaries with period_type filter per contracts/api/ai-summaries.yaml
- [ ] T065 [US4] Implement POST /ai/summaries endpoint in backend/src/routers/ai.py to generate summary with period validation (daily/weekly/monthly/custom) and minimum 7-day check (FR-015) per contracts/api/ai-summaries.yaml
- [ ] T066 [P] [US4] Implement GET /ai/summaries/{id} endpoint in backend/src/routers/ai.py to get specific summary per contracts/api/ai-summaries.yaml
- [ ] T067 [US4] Add summary request detection to conversation intent routing (trigger summary generation when user asks "Give me my daily/weekly summary")
- [ ] T068 [P] [US4] Create TaskSummary component in frontend/src/components/TaskSummary.tsx to display metrics with visual breakdown (completion rate progress bar, priority distribution chart) per contracts/ui/chat-interface.md
- [ ] T069 [US4] Integrate TaskSummary component into ChatInterface assistant messages when summary generated
- [ ] T070 [US4] Add summary generation rate limiting (20 summaries/user/day) to POST /ai/summaries endpoint per contracts/api/ai-summaries.yaml

**Checkpoint**: Summary generation functional - users can request and view productivity metrics

---

## Phase 7: User Story 5 - AI Insights & Recommendations (Priority: P3)

**Goal**: Proactively detect patterns in task history and suggest productivity improvements

**Independent Test**: Accumulate 10+ tasks over 7+ days, request insights, and verify AI generates relevant recommendations (e.g., "You often mark High priority tasks as overdue - consider setting earlier due dates")

### Implementation for User Story 5

- [ ] T071 [P] [US5] Implement overdue pattern detector in backend/src/ai/insights.py analyzing tasks with completion_date > due_date and generating insight with supporting_data JSON
- [ ] T072 [P] [US5] Implement productivity trend analyzer in backend/src/ai/insights.py comparing completion rates across time periods (current vs previous week/month)
- [ ] T073 [P] [US5] Implement priority imbalance detector in backend/src/ai/insights.py checking if >50% tasks are High priority (suggests re-prioritization)
- [ ] T074 [P] [US5] Implement completion streak tracker in backend/src/ai/insights.py detecting consecutive days with completed tasks (positive reinforcement)
- [ ] T075 [P] [US5] Implement workload warning analyzer in backend/src/ai/insights.py detecting 3x normal weekly task count (suggests rescheduling)
- [ ] T076 [P] [US5] Implement time management analyzer in backend/src/ai/insights.py detecting tasks taking longer than expected (average completion time analysis)
- [ ] T077 [P] [US5] Implement recurring task detector in backend/src/ai/insights.py using similarity matching on task titles (suggests batching or categories)
- [ ] T078 [US5] Implement insight recommendation generator in backend/src/ai/insights.py calling Claude API with create_insights.txt prompt and detected patterns per research.md
- [ ] T079 [P] [US5] Implement GET /ai/insights endpoint in backend/src/routers/ai.py to list active (non-dismissed) insights with insight_type and priority filters per contracts/api/ai-summaries.yaml
- [ ] T080 [US5] Implement POST /ai/insights endpoint in backend/src/routers/ai.py to generate insights with minimum data check (10 tasks, 7 days per FR-015) and lookback_days parameter per contracts/api/ai-summaries.yaml
- [ ] T081 [P] [US5] Implement GET /ai/insights/{id} endpoint in backend/src/routers/ai.py to get specific insight per contracts/api/ai-summaries.yaml
- [ ] T082 [P] [US5] Implement POST /ai/insights/{id}/dismiss endpoint in backend/src/routers/ai.py to mark insight as dismissed with optional reason per contracts/api/ai-summaries.yaml
- [ ] T083 [US5] Add insight generation rate limiting (10 insights/user/day) to POST /ai/insights endpoint per contracts/api/ai-summaries.yaml
- [ ] T084 [P] [US5] Create InsightCard component in frontend/src/components/InsightCard.tsx to display insight with title, description, supporting data, priority badge, and dismiss button per contracts/ui/chat-interface.md
- [ ] T085 [US5] Create insights dashboard view in frontend/src/app/insights/page.tsx listing active insights with filters (insight_type, priority) and dismiss functionality
- [ ] T086 [US5] Add insights request detection to conversation intent routing (show active insights when user asks "Show my insights" or "What can I improve?")

**Checkpoint**: AI insights functional - proactive pattern detection and recommendations available

---

## Phase 8: User Story 6 - Multi-Turn Conversation Context (Priority: P3)

**Goal**: Maintain conversation context across multiple messages so users can reference previous messages naturally

**Independent Test**: Have conversation "Show high priority tasks" → "Mark the first one as done" → "When is the next one due?" and verify AI remembers context about which tasks were discussed

### Implementation for User Story 6

- [ ] T087 [US6] Implement task reference tracker in backend/src/services/context_manager.py to extract and store task IDs mentioned in conversation (max 50) per data-model.md
- [ ] T088 [US6] Implement topic detector in backend/src/services/context_manager.py to identify conversation topic switches (task discussion → summary request → new topic) using Claude API or heuristics
- [ ] T089 [US6] Implement pronoun resolver in backend/src/services/conversation_service.py to map "it", "the first one", "the meeting one" to referenced tasks using context
- [ ] T090 [US6] Add context window management to POST /chat/conversations/{id}/messages endpoint maintaining last 10 messages in memory per FR-010 and data-model.md
- [ ] T091 [US6] Implement conversation timeout checker in backend/src/services/context_manager.py background task (10-minute idle timeout, auto-close conversation, persist to DB) per research.md
- [ ] T092 [US6] Add context state indicators to ChatHeader showing active conversation, message count, referenced tasks, timeout warning per contracts/ui/chat-interface.md
- [ ] T093 [US6] Add explicit context reset confirmation modal in ChatInterface (triggered by clear context button) per contracts/ui/chat-interface.md
- [ ] T094 [US6] Add conversation timeout notification in ChatInterface ("Conversation timed out after 10 minutes - start new conversation") per contracts/ui/chat-interface.md

**Checkpoint**: All user stories complete - full conversational AI with context awareness functional

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

- [ ] T095 [P] Add comprehensive logging to all AI endpoints (request/response, user corrections, failures) for FR-022 debugging and quality improvement
- [ ] T096 [P] Implement AI interaction analytics tracking (parse accuracy, confidence score distribution, user edit frequency, rejection reasons) for model improvement
- [ ] T097 [P] Add performance monitoring to AI endpoints (response time tracking, Claude API latency, rate limit hit rate) for FR-023 3-second target
- [ ] T098 [P] Implement user opt-out feature in Phase 2 account settings page (FR-025) to disable AI features globally with UI/API checks
- [ ] T099 [P] Add AI features introduction/onboarding flow in frontend (first-time user guide, feature discovery tooltips)
- [ ] T100 [P] Create frontend error boundary for AI components (graceful degradation to Phase 2 on component failures)
- [ ] T101 [P] Add cost monitoring dashboard (token usage tracking, daily/monthly cost estimation, alert at 80% budget) for research.md $18/month target
- [ ] T102 [P] Implement prompt version tracking in backend/src/ai/prompts/ (version numbers, A/B testing capability for prompt optimization)
- [ ] T103 [P] Add security headers to AI endpoints (rate limit headers, CORS properly configured, no API key exposure)
- [ ] T104 [P] Create Phase 3 API documentation in Swagger/OpenAPI format (combine ai-parse.yaml, ai-conversation.yaml, ai-summaries.yaml)
- [ ] T105 Validate all requirements from spec.md are implemented (FR-001 through FR-025 checklist)
- [ ] T106 Run quickstart.md validation (follow setup guide, verify all commands work, test common issues section)
- [ ] T107 Update root README.md with Phase 3 features, quickstart link, AI service setup instructions
- [ ] T108 [P] Add Phase 3 feature flags to backend for gradual rollout (enable per user, per percentage, per plan tier)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 (NL Task Creation) + US2 (Interpretation Display): P1 - MVP - Can proceed in parallel after Phase 2
  - US3 (Conversational Interface): P2 - Depends on US1 (uses parsing) - Can start in parallel with US4
  - US4 (Task Summaries): P2 - Independent - Can proceed in parallel with US3 and US5
  - US5 (AI Insights): P3 - Independent - Can proceed in parallel with US4 and US6
  - US6 (Multi-Turn Context): P3 - Enhances US3 but testable independently - Should complete after US3
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories ✅ MVP
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories ✅ MVP
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Uses US1 parsing but independently testable
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Completely independent
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - Completely independent
- **User Story 6 (P3)**: Can start after Foundational (Phase 2) - Enhances US3 but independently testable

### Within Each User Story

- Backend models before services
- Services before endpoints
- Backend endpoints before frontend API wrappers
- Frontend API wrappers before UI components
- Core components before integrated pages
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**: All 5 tasks can run in parallel (different files)

**Phase 2 (Foundational)**:
- T007-T012 (6 model files) can run in parallel
- T014 (prompts) can run in parallel with models
- T013, T015, T016 can run in parallel (different files)
- T006 (migration) and T017 (router registration) must run sequentially

**Phase 3 (US1)**:
- T018 (date parser) can run in parallel with T019 (NL parser)
- T021-T024 (4 endpoints) can run in parallel after T019/T020 complete
- T025-T026 (error handling) run after endpoints

**Phase 4 (US2)**:
- T027-T029 (types, API wrapper, ConfidenceIndicator) can run in parallel
- T030-T036 (AIInterpretationPanel features) run sequentially
- T037 (integration) runs after T036

**Phase 5 (US3)**:
- Backend: T042-T045, T047-T048 (6 CRUD endpoints) can run in parallel after T038-T041
- Frontend: T049, T050, T051-T053 (types, hook, 3 components) can run in parallel
- T054-T061 (ChatInterface assembly) run sequentially after components

**Phase 6 (US4)**:
- T062-T063 (summarizer) run sequentially
- T064-T066 (3 endpoints) can run in parallel after T063
- T068 (TaskSummary component) can run in parallel with endpoints

**Phase 7 (US5)**:
- T071-T077 (7 detectors) can run in parallel
- T078-T083 (insight generator + endpoints) run sequentially after detectors
- T084-T085 (InsightCard + dashboard) can run in parallel after T078

**Phase 8 (US6)**:
- T087-T089 (3 context features) can run in parallel
- T090-T091 (endpoint updates) run after context features
- T092-T094 (UI updates) can run in parallel

**Phase 9 (Polish)**:
- T095-T104 (10 cross-cutting tasks) can run in parallel
- T105-T108 run sequentially at end

---

## Parallel Example: User Story 1 (Natural Language Task Creation)

```bash
# Sprint 1: Foundational work (sequential - wait for Phase 2 completion)
# Then these can run in parallel:

# Developer A: NL Parsing Engine
git checkout -b feature/us1-nl-parser
# T018: Date/time parser
# T019: NL parser with Claude API
# T020: Confidence score calculation

# Developer B: API Endpoints
git checkout -b feature/us1-api-endpoints
# T021: POST /ai/parse
# T022: POST /ai/parse/confirm
# T023: POST /ai/parse/reject
# T024: GET /ai/rate-limit

# Developer C: Error Handling
git checkout -b feature/us1-error-handling
# T025: Graceful degradation
# T026: 3-strike fallback

# All three developers can work in parallel on different files
# Merge order: A → B → C (endpoints depend on parser, error handling on endpoints)
```

---

## Parallel Example: User Story 3 (Conversational Task Interface)

```bash
# Backend Team (parallel after conversation service ready)

# Developer A: Conversation CRUD
git checkout -b feature/us3-conversation-crud
# T042: GET /chat/conversations
# T043: POST /chat/conversations
# T044: GET /chat/conversations/{id}
# T045: DELETE /chat/conversations/{id}

# Developer B: Chat Messaging
git checkout -b feature/us3-chat-messages
# T046: POST /chat/conversations/{id}/messages

# Developer C: Context Management
git checkout -b feature/us3-context-api
# T047: GET /chat/context
# T048: DELETE /chat/context

# Frontend Team (parallel after backend endpoints ready)

# Developer D: Core Components
git checkout -b feature/us3-chat-components
# T051: MessageBubble
# T052: MessageInput
# T053: MessageList

# Developer E: Chat Interface Assembly
git checkout -b feature/us3-chat-interface
# T054: ChatInterface main component
# T055: ChatHeader
# T056: AIInterpretationPanel integration

# Developer F: States & Accessibility
git checkout -b feature/us3-chat-polish
# T058: Loading states
# T059: Error states
# T060: Keyboard navigation
# T061: ARIA labels

# All 6 developers can work in parallel on different components/endpoints
```

---

## Implementation Strategy

### MVP Scope (Recommended First Delivery)

**Phase 1-4 Only** (User Stories 1 & 2):
- ✅ Natural language task creation with AI parsing
- ✅ Explainability UI with confidence indicators
- ✅ Edit before confirm capability
- ✅ Graceful degradation to Phase 2

**Estimated**: ~40 tasks (T001-T037 + selective polish tasks)
**Value**: Core AI value proposition - users can create tasks via natural language with full transparency

### Incremental Delivery Order

1. **MVP** (Phase 1-4): US1 + US2 - NL creation with explainability ← SHIP FIRST
2. **Enhancement 1** (Phase 5): US3 - Conversational interface ← High user value
3. **Enhancement 2** (Phase 6): US4 - Task summaries ← Analytics/insights
4. **Enhancement 3** (Phase 7-8): US5 + US6 - Advanced AI features ← Power user features
5. **Production Ready** (Phase 9): Polish + monitoring ← Ship to production

### Suggested Sprint Breakdown

**Sprint 1** (2 weeks): Phase 1-2 (Setup + Foundation) - 17 tasks
**Sprint 2** (2 weeks): Phase 3 (US1: NL Task Creation) - 9 tasks
**Sprint 3** (2 weeks): Phase 4 (US2: Interpretation Display) - 11 tasks ← MVP COMPLETE
**Sprint 4** (2 weeks): Phase 5 (US3: Conversational Interface) - 24 tasks
**Sprint 5** (1 week): Phase 6 (US4: Task Summaries) - 9 tasks
**Sprint 6** (2 weeks): Phase 7 (US5: AI Insights) - 16 tasks
**Sprint 7** (1 week): Phase 8 (US6: Multi-Turn Context) - 8 tasks
**Sprint 8** (1 week): Phase 9 (Polish & Launch Prep) - 14 tasks

**Total**: 8 sprints, ~108 tasks

---

## Success Criteria Per User Story

### US1: Natural Language Task Creation
- ✅ User can send "Buy groceries tomorrow at 5pm" and task created with correct title, date, time
- ✅ System extracts priority when mentioned ("High priority: submit report")
- ✅ Relative dates parsed correctly ("tomorrow", "next Friday", "in 3 days")
- ✅ Ambiguous input falls back to Phase 2 form after 3 attempts
- ✅ AI service failures gracefully redirect to manual entry

### US2: AI Task Interpretation Display
- ✅ User sees breakdown of extracted fields before task creation
- ✅ Confidence scores displayed with color coding (green/amber/red)
- ✅ User can edit any field before confirming
- ✅ Recommendation badge shows auto-accept/review/clarification needed
- ✅ Confirm creates task, Reject cancels without creating

### US3: Conversational Task Interface
- ✅ User can ask "What tasks do I have today?" and get filtered list
- ✅ User can say "Mark groceries as done" and task updates
- ✅ User can create tasks via chat with AIInterpretationPanel preview
- ✅ Chat interface accessible (keyboard nav, screen reader, ARIA labels)
- ✅ Rate limit exceeded shows banner with reset time

### US4: AI Task Summaries
- ✅ User can request daily/weekly/monthly summaries via chat
- ✅ Summaries include completed count, pending count, priority breakdown, overdue items
- ✅ Summaries show productivity trends (completion rate vs previous period)
- ✅ System requires minimum 7 days of history before generating summaries
- ✅ Summary generation rate limited to 20/user/day

### US5: AI Insights & Recommendations
- ✅ System detects overdue patterns and recommends earlier due dates
- ✅ System identifies productivity trends and highlights improvements
- ✅ System warns about workload imbalances (3x normal tasks)
- ✅ System requires minimum 10 tasks and 7 days before generating insights
- ✅ Users can dismiss insights with optional feedback

### US6: Multi-Turn Conversation Context
- ✅ User can say "Show high priority tasks" then "Mark the first one as done" and system resolves reference
- ✅ System maintains 10-message context window
- ✅ System detects topic switches and adjusts context
- ✅ Conversation times out after 10 minutes idle and user notified
- ✅ User can explicitly reset context via clear button

---

## Task Count Summary

- **Phase 1 (Setup)**: 5 tasks
- **Phase 2 (Foundational)**: 12 tasks
- **Phase 3 (US1 - P1)**: 9 tasks
- **Phase 4 (US2 - P1)**: 11 tasks
- **Phase 5 (US3 - P2)**: 24 tasks
- **Phase 6 (US4 - P2)**: 9 tasks
- **Phase 7 (US5 - P3)**: 16 tasks
- **Phase 8 (US6 - P3)**: 8 tasks
- **Phase 9 (Polish)**: 14 tasks

**Total**: 108 tasks

**Parallel Tasks**: 62 tasks marked [P] (57% can run in parallel with proper team staffing)

**MVP Scope**: 37 tasks (Phases 1-4: Setup + Foundation + US1 + US2)

**Story Distribution**:
- US1: 9 tasks (backend NL parsing + API endpoints)
- US2: 11 tasks (frontend explainability UI)
- US3: 24 tasks (full chat interface backend + frontend)
- US4: 9 tasks (summary generation backend + frontend)
- US5: 16 tasks (insights detection + recommendations backend + frontend)
- US6: 8 tasks (context management enhancements)
