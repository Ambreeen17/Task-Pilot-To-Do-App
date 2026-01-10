# Quickstart Guide: Phase 3 — AI-Assisted Todo

**Feature**: 003-ai-assisted-todo | **Date**: 2026-01-10 | **Target**: Developers

## Overview

This guide walks you through setting up the Phase 3 AI capabilities for local development, from API key configuration to testing conversational task creation.

**Estimated Setup Time**: 15 minutes

**Prerequisites**:
- Phase 2 backend and frontend running locally
- Anthropic account with API access
- Python 3.11+ and Node.js 18+

## Table of Contents

1. [Environment Setup](#1-environment-setup)
2. [Database Migration](#2-database-migration)
3. [Backend Development](#3-backend-development)
4. [Frontend Development](#4-frontend-development)
5. [Testing Strategy](#5-testing-strategy)
6. [Common Issues](#6-common-issues)

---

## 1. Environment Setup

### Get Anthropic API Key

1. Create account at [console.anthropic.com](https://console.anthropic.com)
2. Navigate to **API Keys** section
3. Click **Create Key**
4. Copy the key (starts with `sk-ant-...`)

**Important**: Free tier includes $5 credit. Monitor usage at console.anthropic.com.

### Configure Backend Environment

**File**: `backend/.env`

```bash
# Phase 2 (existing)
DATABASE_URL=postgresql://localhost/todo_db
JWT_SECRET=your-jwt-secret-here
CORS_ORIGINS=http://localhost:3000

# Phase 3 (NEW)
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_MAX_TOKENS=1024

# AI Rate Limiting
AI_RATE_LIMIT_REQUESTS=100        # Requests per day per user
AI_RATE_LIMIT_WINDOW_HOURS=24    # Time window for rate limit
AI_CONTEXT_TIMEOUT_MINUTES=10    # Conversation timeout

# AI Feature Flags (optional)
AI_FEATURES_ENABLED=true          # Global AI enable/disable
AI_AUTO_CONFIRM_THRESHOLD=0.9    # Auto-accept confidence threshold
AI_REVIEW_THRESHOLD=0.7          # Review required threshold
```

**Security Note**: Never commit `.env` files. The `.env` file is already in `.gitignore`.

### Install Python Dependencies

**File**: `backend/requirements.txt` (additions)

```txt
# Phase 3 AI Dependencies
anthropic==0.25.0          # Claude API client
python-dateutil==2.8.2     # Date parsing
```

**Install**:

```bash
cd backend
pip install -r requirements.txt
```

**Verify Installation**:

```bash
python -c "import anthropic; print(anthropic.__version__)"
# Expected output: 0.25.0
```

---

## 2. Database Migration

### Run Migration Script

Phase 3 adds 6 new tables for AI features (see `data-model.md`).

**Migration File**: `backend/alembic/versions/003_add_ai_tables.py`

```bash
cd backend

# Generate migration (if using Alembic)
alembic revision --autogenerate -m "Add Phase 3 AI tables"

# Review generated migration
# Edit if needed (see data-model.md for schema)

# Run migration
alembic upgrade head
```

**Without Alembic** (direct SQL):

```bash
cd backend
psql -U postgres -d todo_db -f ../specs/003-ai-assisted-todo/data-model.md
# (Extract SQL from migration script in data-model.md)
```

### Verify Tables Created

```bash
psql -U postgres -d todo_db -c "\dt ai_*"
```

**Expected Output**:

```
              List of relations
 Schema |         Name          | Type  |  Owner
--------+-----------------------+-------+----------
 public | ai_conversations      | table | postgres
 public | ai_insights           | table | postgres
 public | ai_messages           | table | postgres
 public | parsed_task_intents   | table | postgres
 public | task_summaries        | table | postgres
 public | user_contexts         | table | postgres
```

### Seed Test Data (Optional)

**File**: `backend/tests/fixtures/ai_fixtures.py`

```python
# Create test user with AI conversation history
def seed_test_conversation(db_session):
    user = User(email="test@example.com", hashed_password="...")
    db_session.add(user)
    db_session.commit()

    conv = AIConversation(user_id=user.id, status="active")
    db_session.add(conv)
    db_session.commit()

    msg1 = AIMessage(
        conversation_id=conv.id,
        role="user",
        content="Create a task: buy groceries tomorrow"
    )
    db_session.add(msg1)
    db_session.commit()

    print(f"✓ Seeded conversation {conv.id} for user {user.email}")
```

**Run Seeder**:

```bash
python -m backend.tests.fixtures.ai_fixtures
```

---

## 3. Backend Development

### Project Structure

```
backend/
├── src/
│   ├── ai/                     # NEW: AI module
│   │   ├── __init__.py
│   │   ├── client.py           # Claude API wrapper
│   │   ├── parser.py           # NL task parsing
│   │   ├── summarizer.py       # Summary generation
│   │   ├── insights.py         # Pattern detection
│   │   ├── rate_limiter.py     # Request throttling
│   │   └── prompts/            # Prompt templates
│   │       ├── parse_task.txt
│   │       ├── generate_summary.txt
│   │       └── create_insights.txt
│   ├── models/                 # NEW: AI entities
│   │   ├── ai_conversation.py
│   │   ├── ai_message.py
│   │   ├── parsed_task_intent.py
│   │   ├── task_summary.py
│   │   ├── ai_insight.py
│   │   └── user_context.py
│   ├── routers/                # NEW: AI endpoints
│   │   ├── ai.py               # /ai/* (parsing)
│   │   └── chat.py             # /chat/* (conversation)
│   ├── services/               # NEW: AI services
│   │   ├── conversation_service.py
│   │   └── context_manager.py
│   └── main.py                 # Register new routers
```

### Start Backend Server

```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

**Verify Running**:

```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "ai_enabled": true}
```

### Test AI Parsing Endpoint

```bash
# Get auth token first (Phase 2)
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}' \
  | jq -r '.access_token')

# Test AI parsing
curl -X POST http://localhost:8000/api/v1/ai/parse \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"Buy groceries tomorrow at 5pm"}' \
  | jq .
```

**Expected Response**:

```json
{
  "intent": {
    "original_text": "Buy groceries tomorrow at 5pm",
    "extracted_title": "Buy groceries",
    "extracted_priority": null,
    "extracted_due_date": "2026-01-11",
    "extracted_due_time": "17:00",
    "confidence_scores": {
      "title": 0.95,
      "priority": 0.0,
      "due_date": 0.98
    }
  },
  "recommendation": "auto_confirm",
  "message": "Task ready to create"
}
```

### Backend Development Workflow

**1. Create Feature Branch**:

```bash
git checkout -b feature/ai-parsing
```

**2. Write Tests First** (TDD):

```python
# backend/tests/test_ai_parsing.py
def test_parse_simple_task():
    """Test parsing simple task title"""
    result = parse_task("Buy groceries")
    assert result.extracted_title == "Buy groceries"
    assert result.confidence_scores["title"] >= 0.9
```

**3. Implement Feature**:

```python
# backend/src/ai/parser.py
def parse_task(text: str, user_timezone: str = "UTC") -> ParsedTaskIntent:
    """Parse natural language into structured task"""
    # Implementation
```

**4. Run Tests**:

```bash
pytest backend/tests/test_ai_parsing.py -v
```

**5. Manual Testing**:

Use the `/api/v1/ai/parse` endpoint with various inputs to test edge cases.

---

## 4. Frontend Development

### Install Dependencies

**File**: `frontend/package.json` (additions)

```json
{
  "dependencies": {
    "date-fns": "^3.0.0",
    "framer-motion": "^11.0.0"
  }
}
```

**Install**:

```bash
cd frontend
npm install
```

### Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   └── chat/               # NEW: Chat page
│   │       └── page.tsx
│   ├── components/             # NEW: AI components
│   │   ├── ChatInterface.tsx
│   │   ├── MessageList.tsx
│   │   ├── MessageBubble.tsx
│   │   ├── MessageInput.tsx
│   │   ├── AIInterpretationPanel.tsx
│   │   ├── ConfidenceIndicator.tsx
│   │   ├── TaskSummary.tsx
│   │   └── InsightCard.tsx
│   ├── hooks/                  # NEW: AI hooks
│   │   ├── useChat.ts
│   │   └── useAI.ts
│   ├── services/               # NEW: AI API
│   │   └── aiApi.ts
│   └── types/                  # NEW: AI types
│       ├── ai.ts
│       └── conversation.ts
```

### Start Frontend Dev Server

```bash
cd frontend
npm run dev
```

**Verify Running**: Navigate to [http://localhost:3000](http://localhost:3000)

### Test Chat Interface

1. Navigate to [http://localhost:3000/chat](http://localhost:3000/chat)
2. Log in (Phase 2 auth)
3. Type: "Buy groceries tomorrow"
4. Verify AI response with interpretation panel
5. Click [Confirm] to create task
6. Verify task appears in task list

### Frontend Development Workflow

**1. Create Component**:

```tsx
// frontend/src/components/ChatInterface.tsx
'use client';

import { useChat } from '@/hooks/useChat';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

export default function ChatInterface() {
  const { messages, sendMessage, isLoading } = useChat();

  return (
    <div className="chat-interface">
      <MessageList messages={messages} />
      <MessageInput onSend={sendMessage} disabled={isLoading} />
    </div>
  );
}
```

**2. Write Tests**:

```tsx
// frontend/src/components/__tests__/ChatInterface.test.tsx
import { render, screen, userEvent } from '@testing-library/react';
import ChatInterface from '../ChatInterface';

test('sends message on send button click', async () => {
  render(<ChatInterface />);
  const input = screen.getByPlaceholderText('Type your message');
  const sendBtn = screen.getByText('Send');

  await userEvent.type(input, 'Buy groceries');
  await userEvent.click(sendBtn);

  expect(screen.getByText('Buy groceries')).toBeInTheDocument();
});
```

**3. Run Tests**:

```bash
npm test -- ChatInterface
```

---

## 5. Testing Strategy

### Unit Tests

**Backend (pytest)**:

```bash
cd backend

# Run all AI tests
pytest tests/test_ai*.py -v

# Run specific test file
pytest tests/test_ai_parsing.py -v

# Run with coverage
pytest tests/test_ai*.py --cov=src/ai --cov-report=html
```

**Frontend (Jest)**:

```bash
cd frontend

# Run all tests
npm test

# Run specific component tests
npm test -- ChatInterface

# Run with coverage
npm test -- --coverage
```

### Integration Tests

**Backend API Tests**:

```bash
cd backend

# Start test server (separate terminal)
uvicorn src.main:app --reload --port 8001

# Run integration tests
pytest tests/integration/test_ai_endpoints.py -v
```

**Frontend E2E Tests (Playwright)**:

```bash
cd frontend

# Start dev server (if not running)
npm run dev

# Run E2E tests
npx playwright test tests/e2e/chat-flow.spec.ts
```

### Manual Testing Checklist

**Natural Language Parsing**:

- [ ] Simple task: "Buy groceries"
- [ ] With priority: "High priority: submit report"
- [ ] With date: "Buy groceries tomorrow"
- [ ] With time: "Call dentist at 2pm"
- [ ] Relative dates: "next Friday", "in 3 days"
- [ ] Ambiguous: "the thing by sometime next week"

**Conversation Flow**:

- [ ] Multi-turn: "What's due today?" → "Mark the first one complete"
- [ ] Context: "Add a task" → "Buy milk" → "Make it high priority"
- [ ] Timeout: Wait 10 minutes, verify conversation closes
- [ ] Clear context: Click [Clear], verify AI forgets previous messages

**Confidence Indicators**:

- [ ] High (≥0.9): Green bar, auto-confirm badge
- [ ] Medium (0.7-0.89): Amber bar, review badge
- [ ] Low (<0.7): Red bar, needs review badge

**Edge Cases**:

- [ ] Empty input: Send button disabled
- [ ] 10k char limit: Show warning, disable send
- [ ] Rate limit: Show error after 100 requests
- [ ] AI unavailable: Show fallback to manual entry
- [ ] Network error: Show retry button

---

## 6. Common Issues

### Issue: "anthropic module not found"

**Cause**: Python package not installed

**Fix**:

```bash
cd backend
pip install anthropic==0.25.0
```

### Issue: "Invalid API key"

**Cause**: `ANTHROPIC_API_KEY` not set or incorrect

**Fix**:

1. Verify key in `backend/.env`
2. Key should start with `sk-ant-`
3. Check console.anthropic.com for correct key
4. Restart backend server after changing .env

### Issue: "API returned 429 (Too Many Requests)"

**Cause**: Exceeded Claude API rate limits

**Fix**:

- Free tier: 50 requests/min
- Wait 60 seconds or upgrade plan
- Check usage at console.anthropic.com

### Issue: "Database table 'ai_conversations' does not exist"

**Cause**: Migration not run

**Fix**:

```bash
cd backend
alembic upgrade head
```

### Issue: "CORS error when calling /api/v1/ai/parse"

**Cause**: Frontend URL not in `CORS_ORIGINS`

**Fix** (`backend/.env`):

```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

Restart backend server.

### Issue: "Conversation timeout not working"

**Cause**: In-memory context manager not running

**Fix**:

Verify `ContextManager` background task is started in `main.py`:

```python
# backend/src/main.py
from src.services.context_manager import context_manager

@app.on_event("startup")
async def startup_event():
    context_manager.start_timeout_checker()
```

### Issue: "Confidence scores always 0.0"

**Cause**: Prompt not returning scores in correct format

**Fix**:

1. Check `backend/src/ai/prompts/parse_task.txt`
2. Verify JSON response format in prompt
3. Test with Claude directly at console.anthropic.com
4. Check `client.py` JSON parsing logic

### Issue: "Tests fail: 'No module named anthropic'"

**Cause**: Test environment missing dependencies

**Fix**:

```bash
cd backend
pip install -r requirements.txt -r requirements-dev.txt
```

---

## Next Steps

After completing this quickstart:

1. **Read Architecture Docs**: Review `plan.md` for agent responsibilities
2. **Explore Contracts**: See `contracts/api/` for full API specs
3. **Run Full Test Suite**: `npm run test:all` (frontend) and `pytest` (backend)
4. **Deploy to Staging**: Follow deployment guide in `DEPLOYMENT-VISUAL-GUIDE.md`
5. **Monitor Usage**: Check Anthropic console for API costs

## Development Commands Cheatsheet

```bash
# Backend
cd backend
uvicorn src.main:app --reload          # Start dev server
pytest tests/ -v                       # Run all tests
pytest tests/ --cov=src --cov-report=html  # Coverage
alembic upgrade head                   # Run migrations
python -m src.ai.client                # Test Claude API

# Frontend
cd frontend
npm run dev                            # Start dev server
npm test                               # Run tests
npm test -- --coverage                 # Coverage
npm run build                          # Production build
npx playwright test                    # E2E tests

# Database
psql -U postgres -d todo_db            # Connect to DB
psql -c "\dt ai_*"                     # List AI tables
psql -c "SELECT * FROM ai_conversations;"  # Query data

# Git
git checkout -b feature/ai-<name>      # Create feature branch
git add .
git commit -m "feat(ai): <description>"
git push origin feature/ai-<name>
```

## Resources

- **Anthropic Docs**: [docs.anthropic.com](https://docs.anthropic.com)
- **Claude API Reference**: [docs.anthropic.com/claude/reference](https://docs.anthropic.com/claude/reference)
- **Phase 3 Spec**: `specs/003-ai-assisted-todo/spec.md`
- **Data Model**: `specs/003-ai-assisted-todo/data-model.md`
- **API Contracts**: `specs/003-ai-assisted-todo/contracts/api/`
- **UI Contracts**: `specs/003-ai-assisted-todo/contracts/ui/`

## Support

**Issues**: Report at repository issues page

**Questions**: Check spec documents first, then ask in team chat

**API Costs**: Monitor at [console.anthropic.com](https://console.anthropic.com)
