# Implementation Plan: Phase 3 — AI-Assisted Todo

**Branch**: `003-ai-assisted-todo` | **Date**: 2026-01-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-ai-assisted-todo/spec.md`

## Summary

Add AI capabilities to the Phase 2 Todo application, enabling natural language task creation, conversational task management, AI-generated summaries, and proactive insights. The AI layer sits on top of Phase 2 without modifying core task management logic, using Claude API for natural language processing and maintaining graceful degradation when AI services are unavailable.

## Technical Context

**Language/Version**: Python 3.11+ (Backend), TypeScript 5.x (Frontend)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, Claude API (Anthropic), python-dateutil
- Frontend: Next.js, React, Framer Motion, Tailwind CSS
**Storage**: PostgreSQL (existing Phase 2 schema + new AI tables for conversations, context, summaries)
**Testing**: pytest (Backend AI parsing), Jest (Frontend chat UI), Playwright (E2E conversation flows)
**Target Platform**: Web (responsive: 320px mobile to desktop)
**Project Type**: Web application (extends Phase 2 frontend + backend)
**Performance Goals**:
- AI response <3s (95th percentile)
- NL parsing accuracy: 90% title, 85% priority, 95% dates
- Summary generation <2s (daily), <5s (weekly)
**Constraints**:
- Rate limiting: 100 AI requests/user/day
- Token limit: 10,000 tokens/request
- Minimum data for insights: 7 days, 10 tasks
- Context window: 10 messages
**Scale/Scope**: Single-tenant, extends Phase 2 user base, AI features opt-in

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Project Constitution**: Template not filled - using standard software engineering practices

- [x] Specification complete with testable acceptance criteria (6 user stories, 25 FRs, 15 success criteria)
- [x] Dependencies clearly identified (Claude API, conversation state management, NL parsing libraries)
- [x] User stories prioritized (P1: NL parsing + explainability, P2: conversation + summaries, P3: insights + context)
- [x] Edge cases identified (10 scenarios: ambiguity, failures, timezone, rate limits, etc.)
- [x] Graceful degradation strategy (Phase 2 always functional when AI unavailable)
- [x] Privacy and security considerations (user-scoped data, opt-out capability, secure API keys)
- [x] Out of scope clearly defined (voice input, multi-language, custom training, proactive notifications)

## Project Structure

### Documentation (this feature)

```text
specs/003-ai-assisted-todo/
├── plan.md              # This file (/sp.plan command output)
├── spec.md              # Feature specification
├── research.md          # Phase 0 output (AI service selection, NL parsing strategies)
├── data-model.md        # Phase 1 output (AI conversation entities, context storage)
├── quickstart.md        # Phase 1 output (AI API setup, development workflow)
├── contracts/           # Phase 1 output (AI API endpoints, chat UI contracts)
│   ├── api/
│   │   ├── ai-parse.yaml
│   │   ├── ai-conversation.yaml
│   │   └── ai-summaries.yaml
│   └── ui/
│       ├── chat-interface.md
│       └── ai-feedback-panel.md
├── checklists/          # Quality validation
│   └── requirements.md  # Specification validation (complete)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── ai/                          # NEW: AI module
│   │   ├── __init__.py
│   │   ├── client.py                # Claude API client wrapper
│   │   ├── parser.py                # Natural language task parsing
│   │   ├── summarizer.py            # Task summary generation
│   │   ├── insights.py              # Pattern detection and recommendations
│   │   ├── prompts/                 # Prompt templates
│   │   │   ├── parse_task.txt
│   │   │   ├── generate_summary.txt
│   │   │   └── create_insights.txt
│   │   └── rate_limiter.py          # Request throttling
│   ├── models/
│   │   ├── ai_conversation.py       # NEW: Conversation entity
│   │   ├── ai_message.py            # NEW: Message entity
│   │   ├── parsed_task_intent.py    # NEW: Parsed NL intent
│   │   ├── task_summary.py          # NEW: Summary entity
│   │   ├── ai_insight.py            # NEW: Insight entity
│   │   └── user_context.py          # NEW: Conversation context
│   ├── routers/
│   │   ├── ai.py                    # NEW: /ai/* endpoints
│   │   └── chat.py                  # NEW: /chat/* endpoints
│   └── services/
│       ├── conversation_service.py  # NEW: Multi-turn conversation logic
│       └── context_manager.py       # NEW: Context window management
├── tests/
│   ├── test_ai_parsing.py           # NEW: NL parsing tests
│   ├── test_conversation.py         # NEW: Multi-turn dialogue tests
│   ├── test_summaries.py            # NEW: Summary generation tests
│   ├── test_insights.py             # NEW: Pattern detection tests
│   └── test_rate_limiting.py        # NEW: Rate limit enforcement tests
└── .env.example                     # Updated with ANTHROPIC_API_KEY

frontend/
├── src/
│   ├── app/
│   │   └── chat/                    # NEW: Chat interface page
│   │       └── page.tsx
│   ├── components/
│   │   ├── ChatInterface.tsx        # NEW: Main chat UI
│   │   ├── MessageList.tsx          # NEW: Message display
│   │   ├── MessageInput.tsx         # NEW: Text input with submit
│   │   ├── AIInterpretation.tsx     # NEW: Parsed task preview
│   │   ├── ConfidenceIndicator.tsx  # NEW: Confidence score display
│   │   ├── TaskSummary.tsx          # NEW: Summary display
│   │   └── InsightCard.tsx          # NEW: Insight/recommendation card
│   ├── hooks/
│   │   ├── useChat.ts               # NEW: Chat state management
│   │   └── useAI.ts                 # NEW: AI API calls
│   └── services/
│       └── aiApi.ts                 # NEW: AI endpoint wrappers
└── tests/
    ├── chat-interface.test.tsx      # NEW: Chat UI tests
    └── ai-interpretation.test.tsx   # NEW: Interpretation display tests
```

**Structure Decision**: Extends Phase 2 web application structure. AI capabilities added as a new module in backend (`src/ai/`) and new components in frontend (`components/Chat*`, `app/chat/`). Phase 2 code remains unchanged - AI layer is additive only.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. AI features are opt-in and Phase 2 functionality is preserved without modification.

## Agent & Skill Mapping

### AI Agent
**Responsibilities**:
- Natural language understanding and parsing
- Intent detection from user input
- Summary and insight generation
- Conversation context management

**Skills Invoked**:
- **NLU Skill**: Parse natural language into structured task attributes (title, priority, due date)
- **Summarization Skill**: Generate daily/weekly/monthly task summaries with metrics
- **Insight Skill**: Detect patterns in task history and generate actionable recommendations
- **Context Skill**: Maintain conversation state across multi-turn interactions

**Inputs**: User natural language text, task history, conversation context
**Outputs**: Parsed task intent (with confidence scores), summaries, insights, conversational responses

**Quality Gates**:
- NL parsing accuracy ≥90% (title), ≥85% (priority), ≥95% (dates)
- Response latency <3s (95th percentile)
- Fallback to manual entry if parsing fails 3 times

---

### Backend Agent
**Responsibilities**:
- AI API endpoint implementation
- Prompt orchestration to Claude API
- User-scoped context storage
- Rate limiting enforcement
- Graceful degradation logic

**Skills Invoked**:
- **API Integration Skill**: Integrate Claude API with error handling and retries
- **CRUD Skill**: Store/retrieve conversations, messages, summaries, insights
- **Validation Skill**: Validate AI outputs before presenting to user
- **State Management Skill**: Manage conversation context window (10 messages)

**Inputs**: AI agent outputs, user requests, Phase 2 task data
**Outputs**: REST API responses, stored AI entities (conversations, summaries, insights)

**Quality Gates**:
- All AI endpoints require authentication (JWT from Phase 2)
- Rate limiting: 100 requests/user/day enforced
- AI service failures don't break Phase 2 functionality
- All AI interactions logged for debugging

---

### Frontend Agent
**Responsibilities**:
- Chat UI implementation
- AI interpretation display
- Confidence indicator visualization
- Insight dashboard rendering

**Skills Invoked**:
- **UI Composition Skill**: Assemble chat interface, message bubbles, interpretation panels
- **State Management Skill**: Manage conversation state, message history, AI responses
- **Animation Skill**: Smooth transitions for AI responses, loading states, confidence indicators

**Inputs**: User text input, AI API responses, Phase 2 task data
**Outputs**: Interactive chat UI, interpretation previews, summaries, insights

**Quality Gates**:
- Chat interface accessible (keyboard navigation, screen reader support)
- Loading states shown during AI processing (<3s)
- Graceful fallback to Phase 2 UI when AI unavailable
- Responsive design (mobile to desktop)

---

### QA Agent
**Responsibilities**:
- AI behavior validation
- Hallucination checks
- Acceptance test execution
- Edge case verification

**Skills Invoked**:
- **Test Executor Skill**: Run pytest, Jest, Playwright test suites
- **Validation Skill**: Verify AI outputs against expected results
- **Edge Case Skill**: Test ambiguous inputs, failures, boundary conditions

**Test Coverage**:
- Unit tests: AI parsing functions, summary generation, insight detection
- Integration tests: End-to-end NL task creation, conversation flows
- Acceptance tests: All 6 user stories with defined scenarios
- Edge case tests: 10 identified edge cases from spec

**Quality Gates**:
- 90% code coverage for AI module
- All acceptance scenarios passing
- Zero regressions in Phase 2 tests
- Hallucination rate <5% (incorrect task attributes)

## Dependencies & Execution Flow

```text
Phase 0: Research
├── AI service selection (Claude API vs alternatives)
├── NL parsing strategies (zero-shot vs few-shot prompting)
└── Context management patterns (in-memory vs database)
    ↓
Phase 1: Design
├── Data model (AI entities)
├── API contracts (AI endpoints)
└── UI contracts (chat interface)
    ↓
Backend AI APIs
├── /ai/parse (NL → structured task)
├── /ai/summary (generate summaries)
├── /ai/insights (pattern detection)
└── /chat/* (conversational interface)
    ↓
Frontend Chat UI
├── ChatInterface component
├── AIInterpretation preview
└── Confidence indicators
    ↓
Insights Dashboard
├── TaskSummary display
├── InsightCard rendering
└── Trend visualization
    ↓
QA Validation
├── AI behavior tests
├── Hallucination checks
└── Acceptance tests
```

## Risk & Safety Checklist

| Risk | Mitigation | Owner |
|------|-----------|-------|
| AI misinterprets critical tasks | Always show interpretation preview before confirmation; User must approve | AI Agent |
| AI service costs exceed budget | Rate limiting (100 req/user/day); Cache common queries | Backend Agent |
| AI service downtime breaks app | Graceful degradation to Phase 2 manual interface | Backend Agent |
| Poor AI performance frustrates users | Beta badge; Easy fallback to manual entry; Collect feedback | Frontend Agent |
| Privacy concerns about AI processing | Clear data usage communication; Allow opt-out | Backend Agent |
| Context window limits break conversations | Explicit context reset option; Show context status in UI | Backend Agent |
| Insufficient task history for insights | Minimum thresholds (7 days, 10 tasks); Sample insights for new users | AI Agent |
| Hallucinations (incorrect data extraction) | Confidence scores displayed; User can edit before confirm | AI Agent |
| Infinite conversation loops | 3-strike rule (fallback after 3 failures); Max 10 exchanges tracking | Backend Agent |
| Token limits exceeded | 10,000 token limit per request; Truncate long inputs | Backend Agent |

## Technology Decisions (from Research Phase 0)

### AI Service: Claude API (Anthropic)
**Decision**: Use Claude 3.5 Sonnet via Anthropic API
**Rationale**:
- Strong NL understanding capabilities
- Well-documented API with Python SDK
- Reasonable cost ($3/million input tokens, $15/million output tokens)
- Good context window (200k tokens)
**Alternatives Considered**:
- OpenAI GPT-4: More expensive, similar capabilities
- Open-source models (Llama): Requires self-hosting, lower accuracy
- Cohere: Less robust for structured extraction

### NL Parsing Strategy: Zero-shot with structured output
**Decision**: Use Claude with JSON schema for structured extraction
**Rationale**:
- No training data required
- Immediate deployment
- Flexible for edge cases
**Alternatives Considered**:
- Few-shot prompting: Requires curated examples, more complex
- Fine-tuning: Too expensive, overkill for this scale
- Rule-based NLP: Too brittle, low accuracy

### Context Management: Hybrid (in-memory + database)
**Decision**: Active conversations in-memory, persist to database after timeout
**Rationale**:
- Fast access for active chats
- Durability for historical analysis
- Memory efficient (only active conversations loaded)
**Alternatives Considered**:
- Pure in-memory: Loses context on restart
- Pure database: Slower for active conversations
- Redis: Adds complexity, unnecessary for scale

### Date Parsing: python-dateutil
**Decision**: Use `dateutil.parser` for flexible date parsing
**Rationale**:
- Handles relative dates (tomorrow, next week)
- Timezone aware
- Battle-tested library
**Alternatives Considered**:
- Custom regex: Too brittle
- AI-only parsing: Less reliable for dates
- Arrow library: Similar but less flexible

## Next Steps

1. **Phase 0 Output**: Generate `research.md` with detailed AI service setup, NL parsing examples, context management implementation
2. **Phase 1 Output**: Generate `data-model.md` (AI entities), `contracts/` (API specs), `quickstart.md` (development guide)
3. **Agent Context Update**: Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude`
4. **Phase 2 Execution**: Run `/sp.tasks` to generate detailed task breakdown
5. **Implementation**: Execute tasks in priority order (P1 → P2 → P3)
6. **QA Validation**: Run acceptance tests, validate against success criteria

## Success Metrics (Phase 3)

- **Adoption**: 70% of active users try NL task creation within first week
- **Usage**: 40% of tasks created via NL after 30 days
- **Performance**: 90% title accuracy, 85% priority, 95% dates
- **Speed**: 35% faster task creation via NL vs manual
- **Reliability**: <5% AI fallback rate (robust parsing)
- **Satisfaction**: 4+ stars on AI features
- **Stability**: Zero Phase 2 regressions (all tests passing)
