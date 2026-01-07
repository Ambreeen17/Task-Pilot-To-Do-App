# Detailed Tasks: Phase 2 — Full Stack Web Todo

**Feature Branch**: 002-fullstack-web-todo
**Created**: 2026-01-06
**Status**: Ready for Execution
**Plan**: plan.md

## Overview

This document provides a detailed, testable breakdown of all tasks required to implement Phase 2.

## Task Index

| ID | Agent | Task | Priority | Effort |
|----|-------|------|----------|--------|
| D-001 | Database | PostgreSQL Schema Design | P1 | 1h | [X] |
| D-002 | Database | Neon PostgreSQL Setup | P1 | 1h | [ ] |
| B-001 | Backend | SQLModel Database Configuration | P1 | 1h | [X] |
| B-002 | Backend | User SQLModel and Schemas | P1 | 1h | [X] |
| B-003 | Backend | Task SQLModel and Schemas | P1 | 1h | [X] |
| B-004 | Backend | Auth Router - Register | P1 | 1h | [X] |
| B-005 | Backend | Auth Router - Login | P1 | 1h | [X] |
| B-006 | Backend | JWT Token Handler | P1 | 1h | [X] |
| B-007 | Backend | Task Router - CRUD | P1 | 3h | [X] |
| B-008 | Backend | Task Router - Search/Filter | P2 | 1h | [X] |
| B-009 | Backend | User Isolation Middleware | P1 | 1h | [X] |
| B-010 | Backend | FastAPI Application Setup | P1 | 1h | [X] |
| F-001 | Frontend | Next.js Project Setup | P1 | 1h | [X] |
| F-002 | Frontend | Tailwind Config and Theme | P1 | 1h | [X] |
| F-003 | Frontend | Auth Context and API Client | P1 | 1h | [X] |
| F-004 | Frontend | Login Page | P1 | 1h | [X] |
| F-005 | Frontend | Signup Page | P1 | 1h | [X] |
| F-006 | Frontend | Protected Route Component | P1 | 30m | [X] |
| F-007 | Frontend | Task List Page | P1 | 2h | [X] |
| F-008 | Frontend | Task Item Component | P1 | 1h | [X] |
| F-009 | Frontend | Task Form Modal | P1 | 1h | [ ] |
| F-010 | Frontend | Search and Filter Components | P2 | 1h | [X] |
| F-011 | Frontend | Responsive Layout | P2 | 1h | [X] |
| F-012 | Frontend | Neon Theme Styling | P2 | 1h | [X] |
| F-013 | Frontend | Framer Motion Animations | P2 | 1h | [ ] |
| Q-001 | QA | Backend Unit Tests - Auth | P1 | 1h | [X] |
| Q-002 | QA | Backend Unit Tests - Tasks | P1 | 2h | [X] |
| Q-003 | QA | API Integration Tests | P1 | 2h | [ ] |
| Q-004 | QA | User Isolation Security Tests | P1 | 1h | [X] |
| Q-005 | QA | Frontend Component Tests | P2 | 2h | [ ] |
| Q-006 | QA | E2E User Flow Tests | P2 | 2h | [X] |

---

## Database Agent Tasks

### D-001: PostgreSQL Schema Design

**Description**: Design and document the PostgreSQL schema for users and tasks tables.

**Skills Required**: Database Modeling

**Expected Output Files**:
- docs/schema.sql
- specs/002-fullstack-web-todo/contracts/db/schema.png

**Dependencies**: None

**Test Cases**:
1. Verify users table has id (UUID PK), email (UNIQUE), password_hash, timestamps
2. Verify tasks table has id (UUID PK), user_id (FK), title, description, priority, due_date, completed, timestamps
3. Verify foreign key constraint with CASCADE delete
4. Verify check constraint for priority values

**Acceptance Criteria**:
- Schema documented in SQL
- ER diagram created
- All constraints defined (PK, FK, UNIQUE, CHECK)
- Indexes defined for performance

---

### D-002: Neon PostgreSQL Setup

**Description**: Set up Neon PostgreSQL database and configure connection.

**Skills Required**: Database Modeling

**Expected Output Files**:
- .env.example entry for DATABASE_URL

**Dependencies**: D-001

**Test Cases**:
1. Verify database connection succeeds
2. Verify migration can create tables

**Acceptance Criteria**:
- Neon project created
- Connection string available
- Tables can be created successfully

---

## Backend Agent Tasks

### B-001: SQLModel Database Configuration

**Description**: Create SQLModel database engine and session configuration.

**Skills Required**: CRUD, Database Modeling

**Expected Output Files**:
- backend/src/database.py

**Dependencies**: D-002

**Test Cases**:
1. Verify engine creation
2. Verify session local configuration
3. Verify tables can be created from models

**Acceptance Criteria**:
- Engine configured for PostgreSQL
- SessionLocal available for dependency injection
- init_db() function creates all tables

---

### B-002: User SQLModel and Schemas

**Description**: Create User SQLModel entity and Pydantic schemas for authentication.

**Skills Required**: CRUD, Validation

**Expected Output Files**:
- backend/src/models/user.py
- backend/src/schemas/user.py

**Dependencies**: B-001

**Test Cases**:
1. Verify User model has all required fields
2. Verify UserCreate validates email format
3. Verify UserResponse excludes password_hash

**Acceptance Criteria**:
- User SQLModel with table=True
- UserCreate with email validation
- UserLogin with email/password
- UserResponse without password_hash

---

### B-003: Task SQLModel and Schemas

**Description**: Create Task SQLModel entity and Pydantic schemas.

**Skills Required**: CRUD, Validation

**Expected Output Files**:
- backend/src/models/task.py
- backend/src/schemas/task.py

**Dependencies**: B-002

**Test Cases**:
1. Verify Task model links to User with foreign key
2. Verify TaskCreate validates title (1-500 chars)
3. Verify TaskResponse has all fields

**Acceptance Criteria**:
- Task SQLModel with user_id FK
- TaskCreate with title validation
- TaskUpdate with optional fields
- TaskResponse with all fields

---

### B-004: Auth Router - Register

**Description**: Create user registration endpoint with email validation and password hashing.

**Skills Required**: CRUD, Validation, Auth

**Expected Output Files**:
- backend/src/routers/auth.py

**Dependencies**: B-002, B-003

**Test Cases**:
1. Register with valid email/password returns 201
2. Register with duplicate email returns 409
3. Register with invalid email returns 422
4. Register with short password returns 422

**Acceptance Criteria**:
- POST /auth/register endpoint exists
- Validates email format
- Enforces 8+ character password
- Hashes password with bcrypt
- Rejects duplicate emails

---

### B-005: Auth Router - Login

**Description**: Create user login endpoint with JWT token generation.

**Skills Required**: CRUD, Validation, Auth

**Expected Output Files**:
- backend/src/routers/auth.py (login function)

**Dependencies**: B-004

**Test Cases**:
1. Login with valid credentials returns token
2. Login with invalid password returns 401
3. Login with non-existent email returns 401

**Acceptance Criteria**:
- POST /auth/login endpoint exists
- Validates credentials
- Returns JWT access token
- Token includes user_id and expiry

---

### B-006: JWT Token Handler

**Description**: Create JWT token creation and validation utilities.

**Skills Required**: Auth, Validation

**Expected Output Files**:
- backend/src/auth.py

**Dependencies**: B-004

**Test Cases**:
1. Create token with user_id payload
2. Decode valid token
3. Expired token raises exception
4. Invalid signature raises exception

**Acceptance Criteria**:
- create_access_token() function
- decode_token() function
- Token expires after 24 hours
- Proper exception for expired/invalid tokens

---

### B-007: Task Router - CRUD

**Description**: Create task CRUD endpoints (create, read, update, delete, toggle).

**Skills Required**: CRUD, Validation

**Expected Output Files**:
- backend/src/routers/tasks.py

**Dependencies**: B-003, B-006

**Test Cases**:
1. Create task returns 201 with task data
2. Get tasks returns only user's tasks
3. Update task returns updated data
4. Delete task returns 204
5. Toggle completion changes status

**Acceptance Criteria**:
- POST /tasks creates task for authenticated user
- GET /tasks lists user's tasks
- GET /tasks/{id} returns single task
- PUT /tasks/{id} updates task
- DELETE /tasks/{id} removes task
- PATCH /tasks/{id}/toggle changes completed

---

### B-008: Task Router - Search/Filter

**Description**: Add search and filter functionality to task endpoints.

**Skills Required**: CRUD, Validation

**Expected Output Files**:
- backend/src/routers/tasks.py (updated)

**Dependencies**: B-007

**Test Cases**:
1. Search filters by title/description
2. Filter by status (completed/incomplete)
3. Filter by priority (Low/Medium/High)
4. Combined search and filter works

**Acceptance Criteria**:
- GET /tasks?search=keyword
- GET /tasks?status=completed
- GET /tasks?priority=High
- GET /tasks?search=x&status=completed

---

### B-009: User Isolation Middleware

**Description**: Create dependency to ensure users can only access their own tasks.

**Skills Required**: Auth, Validation

**Expected Output Files**:
- backend/src/dependencies.py

**Dependencies**: B-006

**Test Cases**:
1. User A cannot access User B's task (returns 403)
2. Non-existent task returns 404
3. Task ownership verified on GET, PUT, DELETE, PATCH

**Acceptance Criteria**:
- get_current_user() extracts user from JWT
- get_task_or_404() verifies ownership
- Returns 403 for unauthorized access
- Returns 404 for non-existent task

---

### B-010: FastAPI Application Setup

**Description**: Configure FastAPI application with CORS, routers, and health check.

**Skills Required**: CRUD

**Expected Output Files**:
- backend/src/main.py
- backend/src/__init__.py

**Dependencies**: B-004, B-007

**Test Cases**:
1. GET /health returns 200
2. CORS headers present
3. All routes registered

**Acceptance Criteria**:
- FastAPI app created with title and version
- CORS middleware configured
- Auth router included
- Tasks router included
- Health check endpoint at /

---

## Frontend Agent Tasks

### F-001: Next.js Project Setup

**Description**: Initialize Next.js project with TypeScript.

**Skills Required**: UI Composition

**Expected Output Files**:
- frontend/package.json
- frontend/tsconfig.json
- frontend/next.config.js
- frontend/src/app/page.tsx

**Dependencies**: None

**Test Cases**:
1. npm install succeeds
2. npm run dev starts server
3. Home page loads at localhost:3000

**Acceptance Criteria**:
- Next.js 14+ with App Router
- TypeScript configured
- ESLint configured
- Default page renders

---

### F-002: Tailwind Config and Theme

**Description**: Configure Tailwind CSS with neon theme colors.

**Skills Required**: UI Composition

**Expected Output Files**:
- frontend/tailwind.config.js
- frontend/src/app/globals.css

**Dependencies**: F-001

**Test Cases**:
1. Tailwind classes work in components
2. Custom colors available (neon-cyan, neon-magenta)
3. Dark mode styles apply

**Acceptance Criteria**:
- tailwind.config.js with custom theme
- Neon colors defined (cyan, magenta, dark bg)
- Global CSS with base styles

---

### F-003: Auth Context and API Client

**Description**: Create authentication state management and API client.

**Skills Required**: State Management, API Integration

**Expected Output Files**:
- frontend/src/context/AuthContext.tsx
- frontend/src/lib/api.ts

**Dependencies**: F-001

**Test Cases**:
1. Login stores JWT in localStorage
2. Logout clears auth state
3. API requests include Authorization header

**Acceptance Criteria**:
- AuthContext with login, logout, user state
- api.ts with axios instance and interceptors
- Token stored in localStorage
- 401 responses trigger logout

---

### F-004: Login Page

**Description**: Create login page with email/password form.

**Skills Required**: UI Composition, State Management

**Expected Output Files**:
- frontend/src/app/login/page.tsx

**Dependencies**: F-002, F-003

**Test Cases**:
1. Form validates email format
2. Form validates password min length
3. Submit calls login API
4. Success redirects to /tasks

**Acceptance Criteria**:
- Email input with validation
- Password input (8+ chars)
- Submit button
- Error messages on failure
- Loading state during submit

---

### F-005: Signup Page

**Description**: Create signup page with registration form.

**Skills Required**: UI Composition, State Management

**Expected Output Files**:
- frontend/src/app/signup/page.tsx

**Dependencies**: F-002, F-003

**Test Cases**:
1. Form validates email format
2. Form validates password match
3. Submit calls register API
4. Success redirects to /tasks

**Acceptance Criteria**:
- Email input with validation
- Password input (8+ chars)
- Confirm password input
- Error on duplicate email
- Loading state during submit

---

### F-006: Protected Route Component

**Description**: Create wrapper component that redirects unauthenticated users.

**Skills Required**: UI Composition

**Expected Output Files**:
- frontend/src/components/ProtectedRoute.tsx

**Dependencies**: F-003

**Test Cases**:
1. Authenticated user sees content
2. Unauthenticated user redirected to /login
3. Loading state while checking auth

**Acceptance Criteria**:
- Redirects to /login if not authenticated
- Shows loading spinner during check
- Renders children if authenticated

---

### F-007: Task List Page

**Description**: Create main task list page with all tasks.

**Skills Required**: UI Composition, API Integration

**Expected Output Files**:
- frontend/src/app/tasks/page.tsx
- frontend/src/app/tasks/layout.tsx

**Dependencies**: F-003, F-006

**Test Cases**:
1. Page loads with tasks from API
2. Tasks displayed in list
3. Logout button works
4. New Task button opens modal

**Acceptance Criteria**:
- Fetches tasks on mount
- Renders TaskList component
- Shows empty state if no tasks
- Shows loading state while fetching

---

### F-008: Task Item Component

**Description**: Create individual task item with completion toggle.

**Skills Required**: UI Composition, Animation

**Expected Output Files**:
- frontend/src/components/TaskItem.tsx

**Dependencies**: F-002, F-007

**Test Cases**:
1. Checkbox toggles completion
2. Title displays correctly
3. Priority badge shows correct color
4. Due date displays
5. Edit/Delete buttons visible

**Acceptance Criteria**:
- Checkbox with animation
- Priority badge (Low=green, Medium=yellow, High=red)
- Due date with overdue indicator
- Edit and Delete buttons
- Strikethrough on completed

---

### F-009: Task Form Modal

**Description**: Create modal for creating and editing tasks.

**Skills Required**: UI Composition, State Management

**Expected Output Files**:
- frontend/src/components/TaskForm.tsx

**Dependencies**: F-002, F-003

**Test Cases**:
1. Create mode has empty fields
2. Edit mode pre-fills task data
3. Title validation (1-500 chars)
4. Priority selector works
5. Due date picker works

**Acceptance Criteria**:
- Modal overlay with animation
- Title input with validation
- Description textarea
- Priority dropdown (Low/Medium/High)
- Due date picker
- Submit and Cancel buttons

---

### F-010: Search and Filter Components

**Description**: Create search bar and filter dropdowns.

**Skills Required**: UI Composition, API Integration

**Expected Output Files**:
- frontend/src/components/SearchBar.tsx
- frontend/src/components/FilterBar.tsx

**Dependencies**: F-007

**Test Cases**:
1. Search input debounced (300ms)
2. Filter dropdown updates task list
3. Clear filters button works
4. Search and filters combine

**Acceptance Criteria**:
- Search input with debounce
- Status filter (All, Active, Completed)
- Priority filter (All, Low, Medium, High)
- Clear filters button

---

### F-011: Responsive Layout

**Description**: Ensure all pages work on mobile (320px) and desktop.

**Skills Required**: UI Composition

**Expected Output Files**:
- frontend/src/app/responsive.css (if needed)

**Dependencies**: F-004, F-005, F-007

**Test Cases**:
1. Mobile: Stack vertically
2. Desktop: Side-by-side layout
3. Touch targets min 44px
4. No horizontal scroll

**Acceptance Criteria**:
- Mobile-first CSS
- Breakpoints at 768px
- Touch-friendly buttons
- No overflow issues

---

### F-012: Neon Theme Styling

**Description**: Apply neon/robotic theme to all components.

**Skills Required**: UI Composition

**Expected Output Files**:
- frontend/src/components/ui/*.tsx

**Dependencies**: F-002

**Test Cases**:
1. Dark background (#0a0a0f)
2. Cyan neon accents (#00f0ff)
3. Magenta neon accents (#ff00ff)
4. Glow effects on interactive elements

**Acceptance Criteria**:
- Consistent color scheme
- Neon glow effects on buttons
- Dark card backgrounds
- Robotic/tech aesthetic

---

### F-013: Framer Motion Animations

**Description**: Add smooth animations to UI interactions.

**Skills Required**: UI Composition, Animation

**Expected Output Files**:
- frontend/src/components/Animated*.tsx

**Dependencies**: F-012

**Test Cases**:
1. Page transitions smooth
2. Modal enter/exit animated
3. List items animate on add/remove
4. Hover states animated

**Acceptance Criteria**:
- Page fade-in (300ms)
- Modal scale-in (300ms)
- List item slide (200ms)
- Hover scale (150ms)

---

## QA Agent Tasks

### Q-001: Backend Unit Tests - Auth

**Description**: Write unit tests for authentication endpoints.

**Skills Required**: Test Executor

**Expected Output Files**:
- backend/tests/test_auth.py

**Dependencies**: B-004, B-005

**Test Cases**:
1. Test successful registration
2. Test duplicate email rejection
3. Test successful login
4. Test invalid password rejection
5. Test invalid email format

**Acceptance Criteria**:
- 90%+ code coverage for auth router
- All test cases pass
- Tests use pytest fixtures

---

### Q-002: Backend Unit Tests - Tasks

**Description**: Write unit tests for task CRUD endpoints.

**Skills Required**: Test Executor

**Expected Output Files**:
- backend/tests/test_tasks.py

**Dependencies**: B-007, B-008

**Test Cases**:
1. Test task creation
2. Test task list filtering by user
3. Test task update
4. Test task deletion
5. Test completion toggle
6. Test search functionality
7. Test priority filter

**Acceptance Criteria**:
- 90%+ code coverage for tasks router
- All test cases pass
- Tests mock database session

---

### Q-003: API Integration Tests

**Description**: Write integration tests for full API workflows.

**Skills Required**: Test Executor

**Expected Output Files**:
- backend/tests/test_integration.py

**Dependencies**: Q-001, Q-002

**Test Cases**:
1. Register -> Login -> Create Task -> Get Task
2. Register -> Login -> Create Multiple Tasks -> Filter
3. Register -> Login -> Create Task -> Update -> Verify
4. Register -> Login -> Create Task -> Delete -> Verify Gone

**Acceptance Criteria**:
- Tests cover complete user flows
- Tests use test database
- Tests verify actual database state

---

### Q-004: User Isolation Security Tests

**Description**: Write tests to verify user-task isolation.

**Skills Required**: Test Executor

**Expected Output Files**:
- backend/tests/test_security.py

**Dependencies**: B-009

**Test Cases**:
1. User A cannot GET User B's task
2. User A cannot PUT User B's task
3. User A cannot DELETE User B's task
4. User A cannot PATCH User B's task
5. Invalid token returns 401

**Acceptance Criteria**:
- All security tests pass
- 100% isolation verified
- Tests use two different users

---

### Q-005: Frontend Component Tests

**Description**: Write Jest tests for React components.

**Skills Required**: Test Executor

**Expected Output Files**:
- frontend/src/**/*.test.tsx

**Dependencies**: F-004, F-005, F-008

**Test Cases**:
1. Login form validation
2. Signup form validation
3. TaskItem renders correctly
4. TaskItem checkbox toggle
5. TaskList displays tasks

**Acceptance Criteria**:
- 80%+ component coverage
- Tests use React Testing Library
- Mock API calls appropriately

---

### Q-006: E2E User Flow Tests

**Description**: Write Playwright tests for complete user flows.

**Skills Required**: Test Executor

**Expected Output Files**:
- frontend/tests/e2e/*.spec.ts

**Dependencies**: All frontend tasks, Q-005

**Test Cases**:
1. User registration flow
2. User login flow
3. Create task flow
4. Update task flow
5. Delete task flow
6. Search and filter flow

**Acceptance Criteria**:
- Tests run in browser
- All flows tested end-to-end
- Tests handle loading states
- Tests verify UI updates

---

## Agent-Skill Mapping

| Agent | Skills Required | Tasks |
|-------|----------------|-------|
| Database | Database Modeling | D-001, D-002 |
| Backend | CRUD, Validation, Auth | B-001 through B-010 |
| Frontend | UI Composition, State Management, Animation, API Integration | F-001 through F-013 |
| QA | Test Executor | Q-001 through Q-006 |

## Dependency Graph

```
Phase 2 Execution Order:
=========================

Week 1 - Foundation
-------------------
D-001 ──► D-002 ──► B-001 ──► B-002 ──► B-003 ──► B-004 ──► B-005
                           │                   │
                           └──► B-006 ─────────┘
                                    │
                                    ▼
                               B-010 (App Setup)
                                    │
Week 2 - Core Features
-----------------------------------
                               B-007 ──► B-008
                                    │
                                    ▼
                               B-009 (Middleware)

Week 3 - Frontend
-----------------------------------
F-001 ──► F-002 ──► F-003 ──► F-004 ──► F-005 ──► F-006
                                    │               │
                                    └──► F-007 ─────┘
                                             │
                                             ▼
                                        F-008 ──► F-009
                                             │
                                             ▼
                                        F-010 ──► F-011
                                             │
                                             ▼
                                        F-012 ──► F-013

Week 4-5 - Testing
-----------------------------------
All Backend ──► Q-001 ──► Q-002 ──► Q-003 ──► Q-004
                                              │
All Frontend ────────────────────────────────┤
         ──► Q-005 ──► Q-006 ◄────────────────┘
```

## Expected Output Files

### Backend
```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app, CORS, health
│   ├── database.py             # Engine, session, init_db
│   ├── auth.py                 # JWT handling
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # User SQLModel
│   │   └── task.py             # Task SQLModel
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py             # User Pydantic schemas
│   │   └── task.py             # Task Pydantic schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py             # /auth endpoints
│   │   └── tasks.py            # /tasks endpoints
│   └── dependencies.py         # Auth, task ownership
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_tasks.py
│   ├── test_integration.py
│   └── test_security.py
├── requirements.txt
└── .env.example
```

### Frontend
```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx           # Landing
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
│   │   ├── FilterBar.tsx
│   │   └── ProtectedRoute.tsx
│   ├── context/
│   │   └── AuthContext.tsx
│   ├── lib/
│   │   └── api.ts             # Axios client
│   └── hooks/
│       └── useTasks.ts
├── public/
├── tailwind.config.js
├── next.config.js
├── package.json
├── tsconfig.json
└── tests/
    └── e2e/
        └── *.spec.ts
```

## Next Steps

1. Execute tasks in dependency order
2. Start with D-001 (Database Schema Design)
3. Complete database tasks before backend
4. Complete backend before frontend
5. Complete frontend before QA testing
6. Run all tests before merge
