---
id: "005"
title: "generate-readme-project"
stage: "general"
date: "2026-01-06"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "001-foundation-todo-system"
branch: "001-foundation-todo-system"
user: "human"
command: "/sp.generate-readme"
labels: ["documentation","readme","project-overview"]
links:
  spec: "null"
  plan: "null"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - "README.md"
tests: []
---

## Prompt

/sp.generate-readme

Project: Evolution of Todo - Spec-Driven AI-Native Project
Target: README.md covering all phases

Context:
- Multiple phases implemented:
  - Phase 1: Foundation Todo System (CLI, in-memory)
  - Phase 2: Full Stack Web Todo (Next.js frontend, FastAPI backend, Neon DB, Auth)
  - Future Phases: AI-assisted tasks, analytics, notifications, etc.
- Agents and Skills applied per phase:
  - Backend Agent (CRUD, Validation, Database Modeling)
  - Frontend Agent (UI Composition, State Management, Animation)
  - Database Agent (CRUD, DB Modeling)
  - QA Agent (Test Executor)
- Phase 1 may be locked
- Phase 2 and beyond incremental, non-destructive

Objective:
- Generate a comprehensive README covering **all phases**
- Include per-phase details, features, skills, and agents
- Include installation, running instructions, and testing
- Maintain clarity for developers and contributors
- Include "Next Steps / Future Phases" section

Sections to Include:

1. **Project Title & Description**
   - High-level overview
   - Purpose of the project
   - Target audience

2. **Phase Overview**
   - Table with:
     - Phase Number
     - Objective
     - Key Features
     - Agents involved
     - Skills applied
     - Status (Completed / Active / Planned)

3. **Installation**
   - Step-by-step guide
   - Dependencies
   - Env variables

4. **Usage**
   - CLI instructions (Phase 1)
   - Web UI instructions (Phase 2)
   - How to run tests

5. **Testing & QA**
   - Phase-wise QA checklist
   - How to run automated tests
   - Acceptance criteria

6. **Contribution Guide**
   - How to add new phase
   - How to assign agents & skills
   - Coding standards

7. **Future Phases / Roadmap**
   - Features planned for Phase 3, 4, 5
   - AI-assisted tasks, notifications, analytics
   - Skills & agents to be reused

8. **Acknowledgments & References**
   - Claude Code
   - Spec-Kit Plus
   - Tools / Libraries used

Output:
- Fully formatted Markdown
- Ready to save as `README.md` in project root
- Phase-wise tables and clear instructions included

Generate README now.

## Response snapshot

Generated comprehensive README.md for the Evolution of Todo project. The document covers all 5 phases with detailed tables, installation instructions, usage examples (CLI for Phase 1), testing procedures, contribution guidelines, and roadmap for future phases. Includes references to the Master Constitution and uses information from CLAUDE.md for agent/skill definitions.

## Outcome

- ✅ Impact: Created comprehensive project README with 8 major sections
- 📁 Files: README.md (project root) - 550+ lines of structured documentation
- 🔁 Next prompts: Ready for Phase 2 specification when project is ready to evolve
- 🧠 Reflection: README serves as entry point for new contributors, linking to detailed specs in specs/ directory

## Evaluation notes (flywheel)

- Failure modes observed: "none"
- Graders run and results (PASS/FAIL): "N/A - documentation task"
- Prompt variant (if applicable): "N/A"
- Next experiment: "N/A"
