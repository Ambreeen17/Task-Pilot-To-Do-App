# Phase 3 Research: AI-Assisted Todo

**Date**: 2026-01-09
**Phase**: 0 (Research & Technology Selection)
**Feature**: 003-ai-assisted-todo

## Overview

This document captures research findings and technology decisions for implementing AI capabilities in the Todo application. All technical uncertainties from the plan's Technical Context have been resolved through evaluation of alternatives and best practices.

## 1. AI Service Selection

### Decision: Claude API (Anthropic)

**Selected**: Claude 3.5 Sonnet via Anthropic API

**Evaluation Criteria**:
- Natural language understanding quality
- Structured data extraction capability
- API reliability and latency
- Cost per request
- Documentation and SDK quality
- Context window size

**Alternatives Evaluated**:

| Service | Pros | Cons | Cost | Decision |
|---------|------|------|------|----------|
| **Claude 3.5 Sonnet** | Excellent NL understanding, strong structured extraction, 200k context | Newer service, less community resources | $3/M input, $15/M output | ✅ **Selected** |
| OpenAI GPT-4 Turbo | Mature ecosystem, extensive docs, large community | Higher cost, rate limits stricter | $10/M input, $30/M output | ❌ Too expensive |
| OpenAI GPT-3.5 | Low cost, fast | Lower accuracy for structured extraction | $0.50/M input, $1.50/M output | ❌ Accuracy insufficient |
| Cohere Command | Good for enterprise, competitive pricing | Weaker at task attribute extraction | $1/M tokens | ❌ Lower extraction quality |
| Open-source (Llama 3) | No API costs, full control | Requires hosting, GPU infrastructure, lower accuracy | Self-hosting: $100+/month | ❌ Infrastructure complexity |

**Rationale**:
- Claude excels at following structured output instructions (JSON schema)
- Reasonable cost for expected usage (est. 1M tokens/month = $18/month)
- Python SDK (`anthropic`) well-maintained and documented
- 200k context window handles full conversation history
- Rate limits: 50 requests/min (sufficient for 100 req/user/day with rate limiting)

**Implementation**:
```python
# backend/src/ai/client.py
import anthropic
import os

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def call_claude(prompt: str, system: str = None, max_tokens: int = 1024) -> dict:
    """Wrapper for Claude API calls with error handling"""
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text
```

---

## 2. Natural Language Parsing Strategy

### Decision: Zero-shot with JSON Schema

**Selected**: Zero-shot prompting with structured JSON output

**Evaluation Criteria**:
- Setup complexity (training data requirements)
- Parsing accuracy
- Maintainability
- Response latency
- Edge case handling

**Alternatives Evaluated**:

| Approach | Pros | Cons | Accuracy Est. | Decision |
|----------|------|------|---------------|----------|
| **Zero-shot + JSON schema** | No training data, immediate deployment, flexible | Slightly lower accuracy than few-shot | 85-90% | ✅ **Selected** |
| Few-shot prompting | Higher accuracy with examples | Requires curated examples, longer prompts | 90-95% | ❌ Over-engineering for v1 |
| Fine-tuning | Highest accuracy | Expensive ($100s), requires labeled data, slow iteration | 95%+ | ❌ Overkill for scale |
| Rule-based NLP (spaCy) | No API costs, deterministic | Brittle, low accuracy, hard to maintain | 60-70% | ❌ Insufficient accuracy |
| Hybrid (rules + AI) | Best of both worlds | Complex, hard to debug | 90%+ | ❌ Too complex for v1 |

**Rationale**:
- Zero-shot meets accuracy targets (90% title, 85% priority, 95% dates per spec)
- No training data collection or maintenance
- Fast iteration (just update prompts)
- Good edge case handling via confidence scores
- Can upgrade to few-shot later if needed

**Prompt Template** (`backend/src/ai/prompts/parse_task.txt`):
```
You are a task parsing assistant. Extract structured task information from natural language.

Input: "{user_input}"

Extract the following and respond in JSON format:
{{
  "title": "extracted task title (required)",
  "priority": "Low | Medium | High (null if not mentioned)",
  "due_date": "YYYY-MM-DD (null if not mentioned)",
  "due_time": "HH:MM 24-hour format (null if not mentioned)",
  "confidence": {{
    "title": 0.0-1.0,
    "priority": 0.0-1.0,
    "due_date": 0.0-1.0
  }}
}}

Rules:
- title: First verb phrase or noun phrase (e.g., "Buy groceries", "Submit report")
- priority: Only extract if explicitly stated (high/urgent/critical → High, low/minor → Low, else Medium)
- due_date: Relative dates (tomorrow, next week) → absolute date, absolute dates → parse format
- confidence: Your confidence in each extraction (1.0 = certain, 0.5 = guessing, 0.0 = no info)

Examples of relative date parsing:
- "tomorrow" → {tomorrow_date}
- "next Friday" → {next_friday_date}
- "in 3 days" → {three_days_from_now}

Current date: {current_date}
User timezone: {user_timezone}

Respond ONLY with valid JSON, no explanation.
```

**Confidence Score Usage**:
- ≥0.9: Auto-accept (high confidence)
- 0.7-0.89: Show in UI, allow edit
- <0.7: Flag as uncertain, prompt user review

---

## 3. Context Management Pattern

### Decision: Hybrid (In-Memory + Database)

**Selected**: Active conversations in-memory, persist to PostgreSQL after timeout

**Evaluation Criteria**:
- Response latency for active chats
- Memory efficiency
- Durability for historical analysis
- Scalability
- Implementation complexity

**Alternatives Evaluated**:

| Approach | Pros | Cons | Latency | Decision |
|----------|------|------|---------|----------|
| **Hybrid (memory + DB)** | Fast for active, durable for history, memory efficient | Moderate complexity | <10ms | ✅ **Selected** |
| Pure in-memory | Fastest | Loses data on restart, high memory | <5ms | ❌ Data loss risk |
| Pure database | Simple, durable | Slower for active chats | 20-50ms | ❌ Latency too high |
| Redis cache | Fast, durable | Adds dependency, cost | <15ms | ❌ Unnecessary complexity |
| Serverless (DynamoDB) | Auto-scaling | Higher cost, vendor lock-in | 30-100ms | ❌ Not applicable (self-hosted) |

**Rationale**:
- Active conversations (<10 min idle) kept in memory for fast access
- After timeout or explicit close, persist to database
- Conversation history loaded from DB for insights/summaries
- Memory limit: Max 1000 active conversations (est. 10MB)
- PostgreSQL sufficient for scale (no need for Redis)

**Implementation Strategy**:
```python
# backend/src/services/context_manager.py
from typing import Dict, Optional
from datetime import datetime, timedelta

class ConversationContext:
    """In-memory conversation state"""
    def __init__(self, user_id: int, conversation_id: int):
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.messages: List[Message] = []
        self.referenced_tasks: List[int] = []
        self.last_activity: datetime = datetime.now()
        self.topic: Optional[str] = None

class ContextManager:
    """Manages conversation context with hybrid storage"""

    def __init__(self):
        self.active_contexts: Dict[int, ConversationContext] = {}  # user_id → context
        self.timeout_minutes = 10

    def get_context(self, user_id: int) -> ConversationContext:
        """Get or create context for user"""
        if user_id in self.active_contexts:
            ctx = self.active_contexts[user_id]
            if datetime.now() - ctx.last_activity < timedelta(minutes=self.timeout_minutes):
                return ctx
            else:
                # Timeout: persist to DB and create new
                self.persist_context(ctx)
                del self.active_contexts[user_id]

        # Load from DB or create new
        return self.load_or_create_context(user_id)

    def update_context(self, user_id: int, message: Message, task_refs: List[int] = None):
        """Add message to context, maintain 10-message window"""
        ctx = self.get_context(user_id)
        ctx.messages.append(message)
        ctx.messages = ctx.messages[-10:]  # Keep last 10 messages
        if task_refs:
            ctx.referenced_tasks.extend(task_refs)
        ctx.last_activity = datetime.now()
```

---

## 4. Date & Time Parsing Library

### Decision: python-dateutil

**Selected**: `python-dateutil` for flexible date parsing

**Evaluation Criteria**:
- Support for relative dates (tomorrow, next week)
- Timezone awareness
- Parsing accuracy
- Maintenance status
- Integration complexity

**Alternatives Evaluated**:

| Library | Pros | Cons | Decision |
|---------|------|------|----------|
| **python-dateutil** | Flexible, timezone-aware, battle-tested | Large dependency | ✅ **Selected** |
| Arrow | Modern API, similar features | Less mature, smaller community | ❌ dateutil more stable |
| Pendulum | Excellent timezone handling | Heavier, overkill for needs | ❌ Unnecessary overhead |
| Custom regex | Lightweight | Brittle, hard to maintain, no timezone | ❌ Too error-prone |
| AI-only parsing | No extra dependency | Less reliable, inconsistent formats | ❌ Backup to dateutil better |

**Rationale**:
- Handles relative dates: "tomorrow", "next Friday", "in 3 days"
- Timezone-aware (uses user's timezone from Phase 2 account settings)
- Robust parsing: "Jan 15", "2026-01-15", "15 January 2026"
- Used by major projects (Django, Flask, etc.)
- Falls back gracefully on parse failures

**Implementation**:
```python
# backend/src/ai/parser.py
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import pytz

def parse_date(date_str: str, user_timezone: str) -> Optional[datetime]:
    """Parse natural language date with user timezone"""
    tz = pytz.timezone(user_timezone)
    now = datetime.now(tz)

    # Handle relative dates
    date_str_lower = date_str.lower()
    if date_str_lower == "today":
        return now.date()
    elif date_str_lower == "tomorrow":
        return (now + timedelta(days=1)).date()
    elif "next week" in date_str_lower:
        return (now + timedelta(days=7)).date()
    elif "next" in date_str_lower and any(day in date_str_lower for day in ["monday", "tuesday", ...]):
        # Next [day of week]
        target_day = extract_day_of_week(date_str_lower)
        return get_next_weekday(now, target_day).date()

    # Fall back to dateutil parser
    try:
        parsed = date_parser.parse(date_str, default=now)
        return parsed.date()
    except:
        return None  # Parsing failed
```

---

## 5. Rate Limiting Strategy

### Decision: In-memory token bucket per user

**Selected**: Token bucket algorithm with in-memory counters

**Evaluation Criteria**:
- Accuracy (prevent abuse)
- Performance overhead
- Implementation simplicity
- Scalability

**Alternatives Evaluated**:

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| **Token bucket (memory)** | Accurate, fast, simple | Lost on restart (acceptable) | ✅ **Selected** |
| Database counters | Persistent, accurate | Slower, DB load | ❌ Overkill |
| Redis | Fast, distributed | Adds dependency | ❌ Unnecessary |
| Fixed window | Simplest | Burst issues at boundaries | ❌ Less fair |
| Sliding window | Most accurate | Complex | ❌ Over-engineering |

**Rationale**:
- 100 requests/user/day = ~4 requests/hour average
- Token bucket refills smoothly, prevents bursts
- In-memory sufficient (lost counters on restart are acceptable)
- No external dependencies

**Implementation**:
```python
# backend/src/ai/rate_limiter.py
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple

class RateLimiter:
    """Token bucket rate limiter per user"""

    def __init__(self, max_requests: int = 100, window_hours: int = 24):
        self.max_requests = max_requests
        self.window_hours = window_hours
        self.buckets: Dict[int, Tuple[int, datetime]] = {}  # user_id → (tokens, last_refill)

    def check_limit(self, user_id: int) -> Tuple[bool, int]:
        """Check if user has tokens available. Returns (allowed, remaining)"""
        now = datetime.now()

        if user_id not in self.buckets:
            self.buckets[user_id] = (self.max_requests - 1, now)
            return (True, self.max_requests - 1)

        tokens, last_refill = self.buckets[user_id]

        # Refill tokens if window passed
        hours_since_refill = (now - last_refill).total_seconds() / 3600
        if hours_since_refill >= self.window_hours:
            tokens = self.max_requests
            last_refill = now

        if tokens > 0:
            self.buckets[user_id] = (tokens - 1, last_refill)
            return (True, tokens - 1)
        else:
            return (False, 0)
```

---

## 6. Prompt Engineering Best Practices

### Guidelines for Prompt Templates

**Structure**:
1. Role definition ("You are a [X]")
2. Task description (what to do)
3. Output format (JSON schema)
4. Rules and constraints (edge cases)
5. Examples (optional, for few-shot)
6. Context variables (current date, user timezone)

**Example Prompt Categories**:

#### Task Parsing
- Input: Natural language task description
- Output: Structured task (title, priority, due date) + confidence scores
- Template: `parse_task.txt`

#### Summary Generation
- Input: Task list with metadata (completed, pending, overdue)
- Output: Human-readable summary with metrics
- Template: `generate_summary.txt`

#### Insight Detection
- Input: Task history over time period
- Output: Detected patterns + actionable recommendations
- Template: `create_insights.txt`

**Confidence Calibration**:
- Compare AI confidence scores vs actual accuracy
- Adjust thresholds over time based on production data
- Log all predictions with ground truth (user corrections) for analysis

---

## 7. Error Handling & Fallback Strategy

### Graceful Degradation Patterns

**AI Service Failures**:
```python
def parse_task_with_fallback(user_input: str, user: User) -> ParsedTaskIntent:
    """Parse task with graceful fallback"""
    try:
        # Primary: AI parsing
        result = ai_client.parse_task(user_input, user.timezone)
        return result
    except AnthropicAPIError as e:
        logger.error(f"Claude API error: {e}")
        # Fallback 1: Basic regex parsing
        result = regex_fallback_parser(user_input)
        if result:
            return result
        # Fallback 2: Treat entire input as title
        return ParsedTaskIntent(
            title=user_input[:100],  # Truncate to 100 chars
            priority=None,
            due_date=None,
            confidence={"title": 0.5, "priority": 0.0, "due_date": 0.0}
        )
```

**Rate Limit Exceeded**:
```python
if not rate_limiter.check_limit(user.id):
    return {
        "error": "Rate limit exceeded",
        "message": "You've reached the daily limit of 100 AI requests. Try again tomorrow or use manual task entry.",
        "fallback_url": "/tasks/create",  # Link to Phase 2 manual form
        "reset_time": "2026-01-10T00:00:00Z"
    }
```

**Parsing Failures** (3-strike rule):
```python
def handle_parse_failure(user_id: int, attempt: int):
    """Track parse failures and fallback after 3 attempts"""
    if attempt >= 3:
        return {
            "message": "Having trouble understanding. Let's use the manual form instead.",
            "action": "redirect",
            "url": "/tasks/create"
        }
    else:
        return {
            "message": f"Could you rephrase that? (Attempt {attempt}/3)",
            "suggestions": [
                "Try: 'Buy groceries tomorrow'",
                "Or: 'High priority: Submit report by Friday'"
            ]
        }
```

---

## 8. Security Considerations

### API Key Management

**Storage**: Environment variables only (never in code or database)
```bash
# .env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

**Access Control**: API key accessible only by backend service (not exposed to frontend)

**Rotation**: Document key rotation procedure in `quickstart.md`

### Data Privacy

**User Data to AI**:
- Only send task titles/descriptions that user explicitly types
- Never send personal info (email, passwords) to AI
- Task data sent only for active user's own tasks (no cross-user data)

**AI Responses**:
- Validate all AI outputs before storing (no SQL injection, XSS)
- Sanitize confidence scores (0.0-1.0 range)
- Log AI responses for audit but strip PII

**Opt-Out**:
- Provide user setting to disable AI features entirely
- When disabled, hide AI UI elements and reject AI API calls

---

## 9. Cost Estimation & Optimization

### Expected Usage

**Assumptions**:
- 100 users
- 50% adoption rate (50 users use AI)
- 10 AI requests/user/day average (well under 100 limit)
- 500 total AI requests/day
- 200 tokens/request average (150 input + 50 output)

**Monthly Cost**:
```
Input tokens:  500 req/day × 30 days × 150 tokens = 2.25M tokens
Output tokens: 500 req/day × 30 days × 50 tokens  = 0.75M tokens

Cost = (2.25M × $3) + (0.75M × $15) = $6.75 + $11.25 = $18/month
```

**Optimization Strategies**:
1. **Caching**: Cache common queries (e.g., "What's due today?") for 5 minutes
2. **Prompt optimization**: Minimize input tokens, concise system prompts
3. **Batch summaries**: Generate daily summaries once per user, not on-demand
4. **Rate limiting**: Enforce 100 req/user/day to cap costs

**Cost Cap**: $50/month budget → ~2700 requests/day max

---

## 10. Testing Strategy

### AI Component Testing

**Unit Tests**:
- Mock Claude API responses
- Test confidence score calculations
- Validate JSON parsing logic
- Edge cases (empty input, very long input, special characters)

**Integration Tests**:
- End-to-end: User input → AI parse → Task created
- Conversation flow: Multi-turn dialogue maintains context
- Fallback scenarios: AI unavailable → Phase 2 works

**Acceptance Tests**:
- All 6 user stories from spec
- Natural language accuracy benchmarks
- Performance (response time <3s)

**Hallucination Detection**:
- Log AI predictions vs user corrections
- Track accuracy metrics in production
- Alert if accuracy drops below thresholds

---

## Summary of Decisions

| Question | Decision | Rationale |
|----------|----------|-----------|
| AI Service | Claude 3.5 Sonnet | Best NL understanding, reasonable cost, good docs |
| Parsing Strategy | Zero-shot + JSON | No training data, flexible, meets accuracy targets |
| Context Storage | Hybrid (memory + DB) | Fast for active, durable for history |
| Date Parsing | python-dateutil | Robust, timezone-aware, handles relative dates |
| Rate Limiting | Token bucket | Accurate, fair, simple |
| Cost | $18/month estimated | Within budget, room for growth |
| Security | Env vars, user-scoped | Standard best practices |

**Ready for Phase 1**: All technical unknowns resolved. Proceed to data model design and API contracts.
