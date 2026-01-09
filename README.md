# Evolution of Todo — Spec-Driven AI-Native Project

<p align="center">
  <strong>A 5-phase journey from CLI todo app to AI-powered cloud-native productivity platform</strong>
</p>

<p align="center">
  <a href="#phase-overview">Phases</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#testing--qa">Testing</a> •
  <a href="#contribution-guide">Contribute</a> •
  <a href="#roadmap">Roadmap</a>
</p>

---

## Project Description

**Evolution of Todo** is a demonstration project showcasing Spec-Driven Development (SDD) combined with AI-Native execution. The project evolves through five distinct phases, each adding capabilities while preserving previous functionality.

### What This Project Demonstrates

- **Spec-Driven Development**: Every feature begins with formal specifications before any code is written
- **AI-Native Execution**: Claude Code interprets specs, generates plans, produces verified code, and validates outcomes
- **Phase-Based Evolution**: Each phase builds upon the previous, demonstrating incremental, non-destructive growth
- **Auditability**: Complete traceable history through Prompt History Records (PHRs) and Architecture Decision Records (ADRs)

### Target Audience

- Developers learning spec-driven development methodologies
- Teams adopting AI-native development practices
- Projects seeking structured evolution frameworks
- Contributors to the Spec-Kit Plus ecosystem

---

## Phase Overview

| Phase | Objective | Key Features | Agents | Skills | Status |
|-------|-----------|--------------|--------|--------|--------|
| **1** | Foundation Todo System | CLI interface, in-memory storage, CRUD operations | Backend, QA | CRUD, Validation, UI Composition | ✅ Completed |
| **2** | Full-Stack Web App | Next.js UI, FastAPI backend, PostgreSQL persistence, Authentication | Frontend, Backend, Database, QA | UI Composition, State Management, API Integration, Database Modeling, Auth | 🔄 In Progress (Backend Done, Frontend Pending) |
| **3** | AI-Powered Layer | Natural language tasks, AI chat interface, smart insights | Frontend, Backend, QA | NLP Integration, Animation, Accessibility | 📋 Backlog |
| **4** | Cloud Infrastructure | Docker containers, Kubernetes orchestration, Helm charts | DevOps, Backend | Containerization, Orchestration, Observability | 📋 Backlog |
| **5** | Production Deployment | Managed K8s, auto-scaling, CI/CD pipelines, event-driven patterns | DevOps, Backend | Deployment, Scalability, Monitoring | 📋 Backlog |

### Phase 1: Foundation (Completed)

**Objective**: Build a functional Todo system establishing core behavior and domain rules.

**Key Features**:
- Create, read, update, delete tasks
- Task completion tracking (complete/incomplete)
- Interactive REPL mode
- Session-scoped in-memory storage
- Input validation with user-friendly errors

**Tech Stack**: Python 3.11+, Standard Library Only

**Agents Applied**:
- Backend Agent: Domain model, storage, CRUD operations, CLI
- QA Agent: Unit tests, integration tests, acceptance criteria

**Skills Used**:
- CRUD Skill: Entity creation, storage, ID generation
- Validation Skill: Title, description, ID validation
- UI Composition Skill: Output formatting, CLI interface, REPL

### Phase 2: Full-Stack Web (🔄 In Progress - Backend Complete, Frontend Pending)

**Objective**: Transform into a modern web application with persistence and authentication.

**Key Features**:
- ✅ Persistent PostgreSQL storage (Neon DB)
- ✅ User authentication (registration, login, JWT sessions)
- ✅ User-scoped task isolation
- ✅ Advanced task attributes (priority, due dates)
- ✅ Search and filter functionality
- ⏳ Responsive web UI with animations (Next.js + Tailwind + Framer Motion)

**Tech Stack**: Next.js, FastAPI, SQLModel, PostgreSQL, JWT

**Backend Status**:
- ✅ FastAPI REST API complete
- ✅ 12 unit and integration tests passing
- ✅ Authentication with JWT and pbkdf2_sha256 password hashing
- ✅ Task CRUD endpoints with user isolation
- ✅ Search and filter functionality

**Frontend Status**: Pending implementation

### Phase 3: AI-Powered (Backlog)

**Objective**: Add conversational and AI-assisted task management.

**Key Features**:
- Natural language task creation
- AI chat interface for task operations
- Intent detection from natural language
- AI-generated task summaries and insights
- Smart suggestions for organization

### Phase 4: Cloud Infrastructure (Backlog)

**Objective**: Containerize and prepare for cloud deployment.

**Key Features**:
- Docker multi-stage builds
- Kubernetes manifests (Minikube)
- Helm charts for deployment
- Local observability stack (logs, metrics, traces)

### Phase 5: Production Deployment (Backlog)

**Objective**: Achieve production readiness with managed cloud infrastructure.

**Key Features**:
- DigitalOcean Kubernetes (DOKS) deployment
- Horizontal pod autoscaling
- CI/CD pipeline integration
- Event-driven patterns (message queues)
- Production monitoring and alerting

---

## Installation

### Prerequisites

- **Phase 1**: Python 3.11+
- **Phase 2+**: Node.js 18+, Python 3.11+, PostgreSQL
- **Phase 4+**: Docker, Kubernetes (Minikube), Helm
- **Phase 5+**: kubectl, cloud CLI (DigitalOcean)

### Quick Install (Phase 1)

```bash
# Clone the repository
git clone https://github.com/Ambreeen17/TO-DO-APP-PHASE1.git
cd TO-DO-APP-PHASE1

# No external dependencies required for Phase 1
# Python standard library only
```

### Environment Variables (Future Phases)

Create a `.env` file based on `.env.example`:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/todo_db

# Auth
JWT_SECRET=your-secret-key-here
JWT_EXPIRY=3600

# AI Services (Phase 3)
ANTHROPIC_API_KEY=your-api-key

# Cloud (Phases 4-5)
DOKS_TOKEN=your-digitalocean-token
KUBE_CONFIG=~/.kube/config
```

---

## Usage

### Phase 1: CLI Usage

#### Single Commands

```bash
# Create a task
python src/main.py create "Buy groceries" "Milk, eggs, bread"

# List all tasks
python src/main.py list

# Get task details
python src/main.py get 1

# Update a task
python src/main.py update 1 --title "Buy groceries and supplies"

# Mark complete
python src/main.py complete 1

# Mark incomplete
python src/main.py incomplete 1

# Delete a task
python src/main.py delete 1
```

#### Interactive REPL Mode

```bash
# Enter interactive mode
python src/main.py

# Available commands in REPL:
> create "Task title" "Optional description"
> list
> get <id>
> update <id> --title "New title" --description "New desc"
> complete <id>
> incomplete <id>
> delete <id>
> help
> exit
```

#### REPL Example Session

```
$ python src/main.py
Todo System v1.0.0
Type 'help' for available commands.

> create "Buy groceries" "Milk, eggs, bread"
Created task 1: "Buy groceries"

> create "Pay bills" "Electricity bill"
Created task 2: "Pay bills"

> list
1. [ ] Buy groceries - Milk, eggs, bread
2. [ ] Pay bills - Electricity bill

2 tasks total (0 completed, 2 pending)

> complete 1
Task 1 marked as completed: "Buy groceries"

> list
1. [x] Buy groceries - Milk, eggs, bread
2. [ ] Pay bills - Electricity bill

> delete 2
Deleted task 2

> list
1. [x] Buy groceries - Milk, eggs, bread

> exit
Goodbye!
```

### Phase 2+: Web UI (Coming Soon)

```bash
# Start development server
npm run dev          # Frontend (Next.js)
uvicorn app.main:app --reload  # Backend (FastAPI)

# Access at http://localhost:3000
```

---

## Testing & QA

### Running Tests

#### Phase 1 Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/unit/ -v           # Unit tests
python -m pytest tests/integration/ -v    # Integration tests
python -m pytest tests/acceptance/ -v     # Acceptance tests

# Generate coverage report
python -m pytest tests/ --cov=src --cov-report=html
```

#### Test Results (Phase 1)

| Category | Tests | Status |
|----------|-------|--------|
| Unit Tests | 87 | ✅ All Passing |
| Integration Tests | 18 | ✅ All Passing |
| Acceptance Tests | 6 | ✅ All Passing |
| **Total** | **111** | **✅ 100% Pass** |

### Phase-wise QA Checklist

- [ ] **Phase 1 QA**:
  - [x] All CRUD operations tested
  - [x] Input validation tested
  - [x] Error handling verified
  - [x] Deterministic output confirmed
  - [x] Edge cases handled

- [ ] **Phase 2 QA** (Planned):
  - [ ] Database migrations tested
  - [ ] Authentication flows verified
  - [ ] API endpoints tested
  - [ ] UI components accessibility tested
  - [ ] Cross-browser compatibility verified

### Acceptance Criteria

Each phase defines acceptance criteria in `specs/<phase>/acceptance_checklist.md`. All criteria must pass before a phase can be locked.

---

## Contribution Guide

### Adding a New Phase

1. **Create Phase Branch**
   ```bash
   git checkout -b phase-n
   ```

2. **Generate Specifications**
   ```bash
   /sp.specify "Phase N: [Feature Description]"
   ```

3. **Plan Implementation**
   ```bash
   /sp.plan
   ```

4. **Generate Tasks**
   ```bash
   /sp.tasks
   ```

5. **Implement**
   ```bash
   /sp.implement
   ```

6. **Validate**
   ```bash
   /sp.validate
   ```

### Agent Assignment

| Agent | Responsibilities |
|-------|------------------|
| System Architect | Overall architecture, phase boundaries, integration safety |
| Frontend Agent | UI structure, components, design system, animations |
| Backend Agent | APIs, business logic, validation, authentication |
| Database Agent | Schemas, relationships, migrations |
| QA Agent | Phase compatibility, regression checks, quality gates |

### Skill Usage

Invoke skills through the agent framework:

- **CRUD Skill**: Entity creation, storage, ID generation
- **Validation Skill**: Input validation, error messages
- **UI Composition Skill**: Component assembly, layout
- **State Management Skill**: Local state, server sync, cache invalidation
- **Auth Skill**: Password hashing, tokens, sessions
- **Database Modeling Skill**: Schema definition, relationships, queries

### Coding Standards

All code must:
- Follow the specification exactly
- Include unit tests for all functions
- Pass linting and type checking
- Maintain deterministic outputs
- Be fully documented

---

## Project Structure

```
TO-DO-APP/
├── .claude/              # Claude Code configuration
├── .specify/             # SpecKit Plus templates and scripts
├── .github/              # GitHub Actions, templates
├── docs/                 # Documentation
│   └── constitution.md   # Master governance document
├── history/              # Audit trail
│   ├── prompts/          # Prompt History Records
│   └── adr/              # Architecture Decision Records
├── specs/                # Phase specifications
│   └── 001-foundation-todo-system/
│       ├── spec.md       # Feature specification
│       ├── plan.md       # Implementation plan
│       ├── tasks.md      # Task breakdown
│       ├── data-model.md # Entity definitions
│       ├── quickstart.md # User guide
│       └── contracts/    # API contracts
├── src/                  # Phase 1 source code
│   ├── main.py           # CLI entry point
│   ├── task.py           # Task entity
│   ├── storage.py        # In-memory storage
│   ├── validator.py      # Input validation
│   ├── operations.py     # CRUD operations
│   └── output.py         # Display formatting
├── tests/                # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── acceptance/       # Acceptance tests
├── CLAUDE.md             # Claude Code rules
└── README.md             # This file
```

---

## Roadmap

### Phase 3: AI-Powered Interaction Layer

- [ ] Natural language task creation
- [ ] AI chat interface
- [ ] Intent detection
- [ ] Task summaries
- [ ] Smart suggestions

**Skills to Apply**: NLP Integration, Animation, Accessibility

### Phase 4: Local Cloud-Native Infrastructure

- [ ] Docker multi-stage builds
- [ ] Kubernetes manifests
- [ ] Helm charts
- [ ] Local observability stack

**Skills to Apply**: Containerization, Orchestration, Observability

### Phase 5: Production Cloud Deployment

- [ ] DOKS deployment
- [ ] Auto-scaling configuration
- [ ] CI/CD pipeline
- [ ] Event-driven patterns
- [ ] Production monitoring

**Skills to Apply**: Deployment, Scalability, Monitoring

---

## Acknowledgments & References

### Tools & Libraries

- **Claude Code** - AI-native development execution engine
- **Spec-Kit Plus** - Specification-driven workflow framework
- **Python 3.11+** - Phase 1 implementation language
- **Next.js** - Phase 2+ frontend framework
- **FastAPI** - Phase 2+ backend framework
- **SQLModel** - Phase 2+ ORM
- **PostgreSQL** - Phase 2+ database
- **pytest** - Testing framework

### Documentation

- [Spec-Kit Plus Documentation](https://github.com/specify/spec-kit-plus)
- [Claude Code Guide](https://docs.claude.com/)
- [Python Testing](https://docs.python.org/3/library/unittest.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)

---

## License

This project is part of the Spec-Driven AI-Native Development methodology demonstration.

---

<p align="center">
  Built with <a href="https://github.com/specify/spec-kit-plus">Spec-Kit Plus</a> and <a href="https://claude.com/">Claude Code</a>
</p>
