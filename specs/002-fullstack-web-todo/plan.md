# Implementation Plan: Phase 2 — Full Stack Web Todo

**Feature Branch**: `002-fullstack-web-todo`
**Created**: 2026-01-06
**Status**: Ready for Execution
**Spec**: [specs/002-fullstack-web-todo/spec.md](specs/002-fullstack-web-todo/spec.md)

## Summary

Transform the Phase 1 CLI Todo application into a full-stack web application with persistent storage, authentication, and a modern neon-themed UI. This phase adds user accounts, database persistence, JWT authentication, and a responsive web interface while preserving all Phase 1 domain rules.

## Technical Context

**Language/Version**: Python 3.11+ (Backend), TypeScript 5.x (Frontend)
**Primary Dependencies**: FastAPI, SQLModel, Next.js, React, Tailwind CSS, Framer Motion
**Storage**: PostgreSQL (Neon managed)
**Testing**: pytest (Backend), Jest (Frontend), Playwright (E2E)
**Target Platform**: Web (responsive: 320px mobile to desktop)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Page load <2s, API response <500ms, 95% CRUD success rate
**Constraints**: JWT 24h expiry, bcrypt password hashing, user-scoped task isolation
**Scale/Scope**: Single-tenant, 1-N users with private task lists

## Constitution Check

*GATE: Must pass before proceeding to task generation*

- [x] Specification complete with testable acceptance criteria
- [x] Dependencies clearly identified (Next.js, FastAPI, PostgreSQL, JWT, bcrypt)
- [x] User stories mapped to functional requirements
- [x] Edge cases identified (8 scenarios with expected handling)
- [x] Invariants documented for data integrity and security
- [x] Out of scope clearly defined (Phase 3 features deferred)

## Project Structure

### Documentation (this feature)

specs/002-fullstack-web-todo/
├── plan.md              # This file (/sp.plan command output)
├── spec.md              # Feature specification
├── data-model.md        # Database schema documentation
├── quickstart.md        # Development setup guide
├── contracts/           # API and UI contracts
│   ├── api/
│   └── ui/
└── tasks.md             # Detailed task breakdown (/sp.tasks command)

### Source Code (repository root)

backend/
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # User SQLModel
│   │   └── task.py             # Task SQLModel
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py             # Pydantic schemas
│   │   └── task.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py             # /auth endpoints
│   │   └── tasks.py            # /tasks endpoints
│   ├── database.py             # Connection management
│   └── auth.py                 # JWT handling
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   └── test_tasks.py
├── requirements.txt
└── .env.example

frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx           # Landing/redirect
│   │   ├── globals.css
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── signup/
│   │   │   └── page.tsx
│   │   └── tasks/
│   │       ├── page.tsx
│   │       └── layout.tsx
│   ├── components/
│   │   ├── ui/
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   └── Modal.tsx
│   │   ├── TaskList.tsx
│   │   ├── TaskItem.tsx
│   │   ├── TaskForm.tsx
│   │   ├── SearchBar.tsx
│   │   └── FilterBar.tsx
│   ├── context/
│   │   └── AuthContext.tsx
│   ├── lib/
│   │   └── api.ts             # API client
│   └── hooks/
│       └── useTasks.ts
├── public/
├── tailwind.config.js
├── next.config.js
├── package.json
└── tsconfig.json

tests/
├── contract/
├── integration/
└── unit/

**Structure Decision**: Web application with separate frontend (Next.js) and backend (FastAPI) directories. This enables clear separation of concerns, independent deployment, and team scaling.

## Agent Task Assignments

### Backend Agent

| Task ID | Description | Priority | Effort |
|---------|-------------|----------|--------|
| B-001 | Database schema and models (SQLModel) | P1 | 2h |
| B-002 | User registration endpoint (POST /auth/register) | P1 | 1h |
| B-003 | User login endpoint (POST /auth/login) | P1 | 1h |
| B-004 | JWT token generation and validation | P1 | 1h |
| B-005 | Task CRUD endpoints (POST/GET/PUT/DELETE /tasks) | P1 | 3h |
| B-006 | Task completion toggle endpoint | P1 | 30m |
| B-007 | Search and filter endpoints | P2 | 1h |
| B-008 | User isolation middleware | P1 | 1h |

### Frontend Agent

| Task ID | Description | Priority | Effort |
|---------|-------------|----------|--------|
| F-001 | Next.js project setup with Tailwind | P1 | 1h |
| F-002 | Authentication pages (Login/Signup) | P1 | 2h |
| F-003 | Task list page with CRUD operations | P1 | 3h |
| F-004 | Task creation/edit modal | P1 | 2h |
| F-005 | Priority and due date selectors | P2 | 1h |
| F-006 | Search and filter UI | P2 | 1h |
| F-007 | Responsive layout (mobile/desktop) | P2 | 1h |
| F-008 | Neon theme implementation | P2 | 1h |
| F-009 | Framer Motion animations | P2 | 1h |
| F-010 | State management (React Context) | P1 | 1h |

### Database Agent

| Task ID | Description | Priority | Effort |
|---------|-------------|----------|--------|
| D-001 | PostgreSQL schema design | P1 | 1h |
| D-002 | Neon PostgreSQL setup and connection | P1 | 1h |

### QA Agent

| Task ID | Description | Priority | Effort |
|---------|-------------|----------|--------|
| Q-001 | Backend unit tests (pytest) | P1 | 2h |
| Q-002 | Frontend component tests | P2 | 2h |
| Q-003 | API integration tests | P1 | 2h |
| Q-004 | User isolation security tests | P1 | 1h |
| Q-005 | UI responsiveness testing | P2 | 1h |
| Q-006 | End-to-end user flow tests | P2 | 2h |

## Dependency Graph

Critical Path: D-001 -> B-001 -> B-002/003/004 -> B-005 -> F-001 -> F-003 -> Q-001/003

Full dependency chain:
- D-001 -> D-002 (Database setup)
- D-002 -> B-001 (Models require DB)
- B-001 -> B-002/003/004 -> B-005 -> B-006 -> B-007 -> B-008 (Auth -> Tasks -> User isolation)
- B-008 -> F-001 (Backend ready for API integration)
- F-001 -> F-002/F-003/F-010 (Frontend foundation)
- F-003 -> F-004 -> F-005 -> F-006 -> F-007 -> F-008 -> F-009 (Task features -> Polish)
- F-009 -> QA Testing (Q-001 -> Q-002 -> Q-003 -> Q-004 -> Q-005 -> Q-006)

## Skill Usage Table

| Skill | Agent | Usage Context |
|-------|-------|---------------|
| CRUD | Backend | Task CRUD endpoints, User registration |
| Validation | Backend | Input validation, JWT token validation |
| Auth | Backend | JWT implementation, password hashing |
| Database Modeling | Database | User and Task schema design |
| UI Composition | Frontend | Task list, forms, modals |
| Animation | Frontend | Framer Motion transitions |
| State Management | Frontend | Auth context, task state |
| API Integration | Frontend | Axios/Fetch for backend calls |
| Test Executor | QA | pytest, Jest, Playwright |

## Database Schema

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    priority VARCHAR(20) DEFAULT 'Medium',
    due_date TIMESTAMP,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
```

## Implementation Phases

### Phase 2.1: Foundation (Week 1)
1. Database Setup - Neon PostgreSQL connection, SQLModel schemas
2. Authentication System - Registration, bcrypt, JWT, Login
3. Basic API Layer - FastAPI, CORS, Health check

### Phase 2.2: Core Features (Week 2)
1. Task CRUD API - Create, Read, Update, Delete, Toggle
2. Search and Filter - Title/description search, status/priority filters
3. User Isolation - JWT validation, task ownership, 403 handling

### Phase 2.3: Frontend (Week 3)
1. Authentication UI - Login, Signup, Auth state, Protected routes
2. Task Management UI - List, Forms, Completion, Priority/Due date
3. Search and Filters UI - Search bar, Filter controls, Sort options

### Phase 2.4: Polish (Week 4)
1. Responsive Design - Mobile layout, Touch targets, Desktop
2. Neon Theme - Dark mode, Neon accents, Robotic elements
3. Animations - List transitions, Form submissions, Navigation

### Phase 2.5: Testing (Week 5)
1. Backend Tests - Auth, CRUD, User isolation
2. Frontend Tests - Components, Integration
3. E2E Tests - Registration flow, Task management, Search/Filter

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Account creation time | < 2 min | User flow timing |
| Task CRUD success rate | > 95% | API response codes |
| Data persistence | 100% | Tasks survive sessions |
| Page load time | < 2 sec | Lighthouse |
| Search response | < 500ms | API latency |
| Mobile compatibility | 320px+ | Responsive testing |
| User isolation | 100% | Security tests |
| Test coverage | > 80% | Code coverage |

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| JWT token expiry during use | Medium | Refresh token flow (future Phase 3) |
| Database connection issues | High | Connection pooling, retry logic |
| Frontend-backend integration | Medium | Contract testing, shared types |
| Responsive design complexity | Low | Mobile-first development |

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Separate frontend/backend | Clear separation, independent deployment, team scaling | Monolith would couple UI and API concerns |

## Next Steps

1. Run /sp.tasks to generate detailed task breakdown
2. Execute agent implementations in dependency order
3. Begin with Database foundation (D-001, D-002)
4. Follow critical path to frontend integration
