# Master Constitution
## Evolution of Todo — Spec-Driven AI-Native Project

**Version**: 1.0.0 | **Ratified**: 2026-01-06 | **Last Amended**: 2026-01-06

---

## 1. Vision & Purpose

This Master Constitution establishes the foundational governance framework for the "Evolution of Todo — Spec-Driven AI-Native Project." It serves as the single source of truth for all project phases, development practices, and architectural decisions.

### Project Vision

The vision of this project is to demonstrate how a simple todo management system can evolve through five distinct phases into a sophisticated, AI-powered, cloud-native application. Each phase builds upon the previous, adding capabilities while preserving core domain behavior. The project serves as both a functional application and a demonstration of spec-driven, AI-native development methodology.

### Why Spec-Driven Development

Spec-Driven Development ensures that every feature, API, and behavioral change is first documented, reviewed, and validated before implementation begins. This approach eliminates ambiguity, prevents scope creep, and creates an audit trail of all decisions. By mandating specifications before code, the project maintains coherence across multiple phases and multiple contributors. Specifications become contracts that implementation must fulfill.

### Why AI-Native Development Is Central

AI-Native development positions artificial intelligence as the primary executor of development work. Claude Code interprets specifications, generates implementation plans, produces verified code artifacts, and validates outcomes. Human contributors provide direction, review, and approval while AI handles the mechanical work of translation from specification to implementation. This symbiosis maximizes productivity while maintaining human oversight.

### How the Project Evolves Phase by Phase

The project evolves through five discrete, additive phases. Each phase follows the Specification → Plan → Implementation → Validation lifecycle. Phases may evolve freely until explicitly locked. Locking is a deliberate decision made after successful validation, signaling that the phase has reached a stable state. Future phases build upon locked phases but must not break their guarantees.

---

## 2. Core Development Principles

### Spec Before Code

No implementation begins until a formal specification document exists, has been reviewed, and has received approval. Specifications must include user stories with priorities, functional requirements, success criteria, and edge cases. This principle ensures that all stakeholders share a common understanding before any code is written.

### Deterministic Outputs

Given identical specifications and inputs, the system must produce identical outputs. Claude Code must follow the same decision-making framework regardless of when or by whom it is invoked. This principle enables reproducible builds, reliable code reviews, and consistent behavior across all development sessions.

### Auditability

Every decision, specification, plan, and implementation must be traceable to its source. The Prompt History Record system captures all user inputs and AI responses. Architecture Decision Records document significant choices with rationale. This principle ensures that future contributors can understand why the system exists in its current form.

### Reusability

All patterns, skills, and agents developed during any phase must be documented, abstracted, and made available for reuse in subsequent phases. Knowledge captured during Phase 1 must be immediately applicable during Phase 5 without redevelopment. This principle ensures compounding productivity gains across the project lifecycle.

### No Breaking Changes

Each phase must maintain compatibility with previous phases. New features may extend behavior but must not remove, alter, or break existing functionality. This principle protects users who depend on earlier features and ensures that the project evolves through addition.

### Human Review + AI Execution

Human reviewers approve specifications and validate implementations. AI executes the mechanical work of translation and implementation. Neither operates independently. This principle ensures that human intent guides development while AI provides the execution capacity.

### Incremental Evolution

The project grows through small, verifiable increments. Each increment adds measurable value without introducing unnecessary complexity. Large features are decomposed into independently implementable and testable pieces. This principle reduces risk and enables frequent validation.

---

## 3. Phase Governance Model

### What Constitutes a Phase

A phase represents a coherent set of features, infrastructure, or capabilities that are specified, implemented, and validated as a unit. Phases have clear objectives, defined scopes, and measurable outputs. Phases are additive in that they build upon previous work without removing or altering existing capabilities.

### Phase Lifecycle

Each phase progresses through five stages:

1. **Specify**: The `/sp.specify` command generates a feature specification document based on user requirements. The specification includes user stories, functional requirements, success criteria, and edge cases.

2. **Plan**: The `/sp.plan` command generates an implementation plan based on the specification. The plan includes technical context, project structure, complexity tracking, and architecture decisions.

3. **Implement**: The `/sp.implement` command executes the tasks defined in the plan. Implementation follows established patterns and produces verified artifacts.

4. **Validate**: Validation ensures that all specification requirements are met, existing functionality remains intact, and the implementation meets quality standards. Validation produces a formal report.

5. **Lock (Optional)**: Locking is a deliberate decision made after successful validation. A locked phase becomes stable and its guarantees become immutable. Phases may remain unlocked indefinitely if continued evolution is expected.

### Locking Policy

Locking is optional and applied only after completion. A phase may continue to evolve without locking. Locking signals that the phase has reached a stable state and that future changes should occur in subsequent phases. Once locked, a phase cannot be modified except for non-functional changes that preserve existing behavior.

---

## 4. Repository & Branch Strategy

### Single Repository

All project artifacts, including source code, specifications, plans, tasks, and documentation, reside in a single Git repository. This ensures that the complete project history is preserved and accessible from one location.

### Branch Per Phase

Development occurs on branches named `phase-n` where n corresponds to the phase number. The `phase-1` branch contains the Phase 1 implementation. The `phase-2` branch contains Phase 2 development. Future phases follow the same pattern. Active work on a phase occurs on its dedicated branch.

### Main as Stable Integration Branch

The `main` branch serves as the stable integration branch. It contains the validated, production-ready state of the project. Changes are merged to `main` after validation passes. The `main` branch always represents the most recent stable version of the project.

### Phase Branches for Active Work

Phase branches contain active development work. They may be in various states of completion and may not be stable. Feature branches may be created from phase branches for parallel development, then merged back after review.

### Merge Rules

Changes flow from feature branches to phase branches, and from phase branches to `main` after validation. Merge to `main` requires passing all validation checks. No changes flow backward from later phases to earlier phases or to `main`.

---

## 5. Technology Baseline

All phases must respect this technology baseline. Deviations require explicit approval through an Architecture Decision Record and must not break compatibility with existing functionality.

### Frontend

- **Framework**: Next.js (App Router) for server-side rendering, routing, and React-based UI components
- **Styling**: Tailwind CSS for utility-first styling with design system consistency
- **Component Architecture**: Component-driven UI development with reusable, composable components
- **Animation**: Framer Motion or equivalent for smooth transitions and user feedback
- **Accessibility**: WCAG 2.1 AA compliance required for all interactive elements

### Backend

- **Framework**: FastAPI for high-performance async API development with automatic OpenAPI documentation
- **ORM**: SQLModel for type-safe database interactions with Pydantic validation
- **Database**: PostgreSQL (Neon serverless recommended) for reliable, scalable data persistence

### AI & Spec Tooling

- **Execution Engine**: Claude Code for AI-native development, specification interpretation, and code generation
- **Workflow Framework**: Spec-Kit Plus for command structures, templates, and governance enforcement

---

## 6. Phase 1 — Foundation Phase

### Objective

Build a functional Todo system establishing core behavior and domain rules. Phase 1 creates the foundational domain model and CRUD operations that all subsequent phases will extend.

### Scope

Phase 1 delivers the following core capabilities:

- **Task Creation**: Users can create tasks with descriptions and basic attributes
- **Task Update**: Users can modify task content and attributes after creation
- **Task Deletion**: Users can remove existing tasks by identifier
- **Task Listing**: Users can view all existing tasks
- **Task Completion**: Users can mark tasks as complete or incomplete

### Output

Phase 1 produces:

- **Functional Implementation**: Working code that fulfills all core capabilities
- **Clear Domain Model**: Well-defined task entity with attributes and behaviors
- **Behavior Definitions**: Documented specifications that later phases will extend

### Success Criteria

- All CRUD operations function correctly
- Task model supports core attributes (description, completion status)
- Domain rules are enforced consistently
- Specification documents capture all behaviors

---

## 7. Phase 2 — Full-Stack Web Evolution

### Objective

Transform Phase 1 into a modern, full-stack web application. Phase 2 adds persistence, authentication, and a professional user interface while preserving Phase 1 core behaviors.

### Scope

Phase 2 delivers:

- **Persistent Storage**: All task data persists in PostgreSQL database with proper schema design
- **Authentication**: User registration, login, and session management
- **User-Scoped Todos**: Each user's tasks are isolated and accessible only to that user
- **Advanced Task Attributes**: Priority levels, status tracking, due dates, categories, and tags
- **Modern UI/UX**: Responsive web interface with professional design, animations, and accessibility

### Output

Phase 2 produces:

- Full-stack web application with Next.js frontend and FastAPI backend
- RESTful API with documented endpoints
- Persistent database with migration support
- User authentication system
- Feature-rich task management UI

---

## 8. Phase 3 — AI-Powered Interaction Layer

### Objective

Introduce conversational and AI-assisted task management. Phase 3 adds intelligent interfaces that understand natural language and provide proactive assistance.

### Scope

Phase 3 delivers:

- **Natural Language Task Creation**: Users can describe tasks in natural language, and the system extracts structured data
- **AI Chat Interface**: Conversational interface for task management operations
- **Intent Detection**: Automatic identification of user intentions from natural language input
- **Task Summaries**: AI-generated summaries of task lists, priorities, and deadlines
- **Smart Insights**: Proactive suggestions for task organization, scheduling, and completion

### Output

Phase 3 produces:

- Natural language processing integration
- Conversational UI components
- Intent classification system
- Task analytics and insights engine
- Enhanced user productivity features

---

## 9. Phase 4 — Local Cloud-Native Infrastructure

### Objective

Containerize and orchestrate the system locally. Phase 4 prepares the application for cloud deployment through containerization and local orchestration.

### Scope

Phase 4 delivers:

- **Dockerization**: Containerized application with multi-stage builds and optimized images
- **Kubernetes Orchestration**: Local Kubernetes configuration using Minikube
- **Helm Charts**: Package management for Kubernetes deployments
- **Local Observability**: Logging, metrics, and tracing infrastructure for local development

### Output

Phase 4 produces:

- Docker images for all application components
- Kubernetes manifests for deployment
- Helm charts for easy installation
- Local development environment
- Observability stack configuration

---

## 10. Phase 5 — Production Cloud Deployment

### Objective

Deploy the system to a real cloud environment. Phase 5 achieves production readiness with managed Kubernetes and scalable infrastructure.

### Scope

Phase 5 delivers:

- **Managed Kubernetes**: Deployment to DigitalOcean Kubernetes (DOKS) or equivalent
- **Scalability**: Horizontal pod autoscaling and load balancing configuration
- **Event-Driven Patterns**: Message queues and event processing for async operations
- **Production Readiness**: Health checks, readiness probes, graceful shutdown, and monitoring

### Output

Phase 5 produces:

- Production Kubernetes cluster configuration
- CI/CD pipeline for automated deployment
- Scalable infrastructure with auto-scaling
- Event-driven architecture components
- Production monitoring and alerting

---

## 11. Phase Execution Rules

### Independent Specifications Required

Each phase must be decomposed into multiple specifications. A monolithic specification covering all concerns is prohibited. This ensures focused review, parallel development, and comprehensive coverage.

### Recommended Specification Types

Each phase should include the following specification types as applicable:

- **UI Specification**: Defines web interface structure, component hierarchy, user flows, and visual design requirements
- **API Specification**: Defines REST endpoints, request/response schemas, authentication flows, and error responses
- **Data Model Specification**: Defines database schema, relationships, migrations, and query patterns
- **Auth Specification**: Defines user registration, login, session management, and security measures
- **Integration Specification**: Defines frontend-backend communication, state management, and error handling

### Specification Organization

All specifications reside in the `specs/` directory organized by phase number. Each phase has its own subdirectory containing all related specifications, plans, and tasks.

---

## 12. Agent Architecture

The project employs specialized agents that operate within their defined responsibilities. Agents may invoke subagents for domain-specific tasks and may invoke skills for reusable operations.

### System Architect Agent

**Responsibilities:**
- Overall architecture: Define and maintain system architecture across all phases
- Phase boundaries: Ensure clean separation between phases and proper integration points
- Integration safety: Verify that new components integrate correctly without breaking existing functionality

### Frontend Agent

**Responsibilities:**
- UI structure: Maintain Next.js App Router organization and component architecture
- Components: Develop reusable UI components following design system
- Design system: Ensure visual consistency and accessibility compliance

**Subagents:**
- **Navbar Agent**: Navigation components, responsive menu, and user menu integration
- **Footer Agent**: Footer content, links, and responsive behavior
- **Layout Agent**: Page layouts, spacing, grid systems, and responsive breakpoints
- **Animation Agent**: Transition definitions, timing functions, and motion patterns
- **Theme Agent**: Design tokens, color schemes, typography, and consistency rules

### Backend Agent

**Responsibilities:**
- APIs: Design and implement RESTful endpoints with proper versioning
- Business logic: Implement domain rules and workflow validation
- Validation: Ensure request validation and error handling

**Subagents:**
- **Auth Subagent**: Authentication endpoints, token management, and security
- **Todo Logic Subagent**: CRUD operations, business rules, and task lifecycle
- **Validation Subagent**: Request validation, error responses, and data integrity

### Database Agent

**Responsibilities:**
- Schemas: Design SQLModel classes with proper typing and relationships
- Relations: Define foreign keys, cascading rules, and query patterns
- Migrations: Generate and apply database migrations safely

### QA & Regression Agent

**Responsibilities:**
- Phase compatibility: Verify that new work integrates correctly with existing phases
- Regression checks: Detect behavioral changes that violate previous phase guarantees
- Quality gates: Enforce quality standards before merge approval

---

## 13. Reusable Skills Library

Skills are reusable operations that any agent or subagent may invoke. Skills are documented, parameterized, and must not be hard-coded within specific implementations.

### CRUD Skill

**Purpose**: Create, read, update, and delete operations for domain entities

**Operations:**
- Create entity with validation
- Read entity by identifier or query
- Update entity with optimistic locking
- Delete entity with cascade options

### Validation Skill

**Purpose**: Input validation and error reporting

**Operations:**
- Schema validation with detailed error messages
- Business rule validation
- Cross-field validation
- Error response formatting

### State Management Skill

**Purpose**: Client and server state management

**Operations:**
- Local state persistence
- Server state synchronization
- Cache invalidation
- Optimistic updates

### UI Composition Skill

**Purpose**: Component assembly and layout

**Operations:**
- Component composition patterns
- Props passing and context
- Conditional rendering
- List rendering with keys

### Auth Skill

**Purpose**: Authentication and authorization operations

**Operations:**
- Password hashing and verification
- Token generation and validation
- Session management
- Route protection

### API Integration Skill

**Purpose**: Frontend-backend communication

**Operations:**
- HTTP client configuration
- Request/response interception
- Error handling
- Retry logic

### Database Modeling Skill

**Purpose**: Schema definition and queries

**Operations:**
- Model definition with SQLModel
- Relationship configuration
- Query building
- Migration generation

### Animation Skill

**Purpose**: Motion and transitions

**Operations:**
- Enter/exit animations
- Transition timing
- Gesture animations
- Layout animations

### Accessibility Skill

**Purpose**: Accessibility compliance

**Operations:**
- ARIA attribute management
- Keyboard navigation
- Screen reader optimization
- Focus management

### Skills Invocation Rules

- Skills must be invoked through the agent framework, not hard-coded in implementation
- Skills accept parameters and return results in standardized formats
- Skills may depend on other skills but must avoid circular dependencies
- Skills must be documented with usage examples and parameter descriptions

---

## 14. Deployment Strategy

### Phase-Appropriate Deployment Rules

Each phase has deployment requirements suited to its scope:

- **Phase 1**: Local development execution, no deployment required
- **Phase 2**: Local development server with hot reload, optional staging deployment
- **Phase 3**: Local development with AI service integration, optional cloud deployment
- **Phase 4**: Local Kubernetes deployment for testing
- **Phase 5**: Production cloud deployment with CI/CD pipeline

### Local vs Cloud Deployment

**Local Development**: All phases support local development for rapid iteration. Local environments should mirror production configurations where feasible.

**Cloud Deployment**: Phases 2 through 5 support cloud deployment. Phase 4 introduces local cloud infrastructure. Phase 5 transitions to production cloud deployment.

### Environment Variable Management

- Environment variables follow naming conventions across all phases
- Sensitive values are stored securely and never committed to version control
- Environment-specific configurations are managed through separate files
- Validation ensures required variables are present before startup

---

## 15. Amendment & Evolution Policy

### Constitution May Evolve

This constitution may be amended as the project evolves. Amendments must follow the specified change management process and maintain compatibility with locked phases.

### Existing Sections May Be Refined

Sections may be clarified, expanded, or reorganized. Refinements must not change the fundamental meaning or intent of existing provisions. Typographical corrections and clarifications are permitted without version increment.

### No Backward Breaking Changes

Amendments must not introduce breaking changes to locked phases. Any change that would affect the behavior of a locked phase is prohibited. This ensures that users who depend on earlier features can continue to rely on their continued availability.

### New Rules Must Remain Compatible

New provisions must be compatible with existing locked phases. When adding new rules, ensure that existing implementations can continue to function correctly. Deprecation paths may be used for voluntary adoption of new patterns.

### Amendment Process

Amendments require:
1. Clear documentation of the proposed change
2. Review for compatibility with locked phases
3. Validation that existing implementations remain functional
4. Version increment according to semantic versioning rules

---

## 16. Final Authority

This constitution is the single source of truth for all project governance. It supersedes all other instructions, guidelines, or directives that may exist in the repository.

### Claude Code Must Strictly Follow

Claude Code must verify compliance with this constitution before executing any command, generating any code, or making any architectural decision. All AI-native operations must respect the principles, rules, and structures defined herein.

### All Planning and Execution Must Comply

All specification, planning, and implementation work must comply with this constitution. Any conflict between this constitution and other documentation must be resolved in favor of this constitution.

### Precedence Order

In case of conflict, this constitution takes precedence over:
1. README files
2. Command documentation
3. Template instructions
4. Prior decisions not captured in this document
5. External guidance that contradicts these principles

---

## Appendix A: Phase Summary

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | Active | Foundation Phase — Core Todo CRUD operations |
| Phase 2 | Pending | Full-Stack Web Evolution — Persistence, Auth, Modern UI |
| Phase 3 | Pending | AI-Powered Interaction Layer — Natural language, Chat, Insights |
| Phase 4 | Pending | Local Cloud-Native Infrastructure — Docker, Kubernetes, Helm |
| Phase 5 | Pending | Production Cloud Deployment — Managed K8s, Scalability, Production |

## Appendix B: Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2026-01-06 | Initial constitution with all 5 phases defined |
