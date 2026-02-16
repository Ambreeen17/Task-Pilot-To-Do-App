---
id: "001"
title: "create-master-constitution"
stage: "constitution"
date: "2026-01-06"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "none"
branch: "master"
user: "human"
command: "/sp.constitution"
labels: ["constitution","governance","project-setup"]
links:
  spec: "null"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - "docs/constitution.md"
tests: []

## Prompt

You are Claude Code operating in Spec-Driven Development mode using Spec-Kit Plus.

Your task is to generate a COMPLETE MASTER CONSTITUTION for a fresh project named:

"Evolution of Todo — Spec-Driven AI-Native Project"

This is a NEW PROJECT.
No phase is pre-locked.
All phases must be fully defined and governed from start to finish.

The constitution must:
- Cover the entire project lifecycle
- Define all phases (1 to 5)
- Be phase-wise, but NOT pre-locked
- Support future locking after completion
- Be reusable, extendable, and professional

CORE DEVELOPMENT DIRECTIVES:
1. Spec-Driven Development is mandatory.
2. No implementation may start without an approved specification.
3. Claude Code is the ONLY execution engine.
4. Spec-Kit Plus governs: /sp.specify, /sp.plan, /sp.implement
5. Phases must be incremental and additive.
6. Regression prevention is mandatory.
7. Reusable intelligence is required: Agents, Subagents, Skills

OUTPUT REQUIREMENTS:
Generate a professional Markdown document suitable for: docs/constitution.md

Use: Clear headings, Formal tone, Phase-wise structure, Future-proof design

MANDATORY CONSTITUTION STRUCTURE:
# Master Constitution
## Evolution of Todo — Spec-Driven AI-Native Project

## 1. Vision & Purpose
## 2. Core Development Principles
## 3. Phase Governance Model
## 4. Repository & Branch Strategy
## 5. Technology Baseline
## 6. Phase 1 — Foundation Phase
## 7. Phase 2 — Full-Stack Web Evolution
## 8. Phase 3 — AI-Powered Interaction Layer
## 9. Phase 4 — Local Cloud-Native Infrastructure
## 10. Phase 5 — Production Cloud Deployment
## 11. Phase Execution Rules
## 12. Agent Architecture
## 13. Reusable Skills Library
## 14. Deployment Strategy
## 15. Amendment & Evolution Policy
## 16. Final Authority

IMPORTANT:
- Do NOT lock any phase by default
- Locking is a future decision after completion
- Focus on governance, not implementation details

## Response snapshot

Created comprehensive Master Constitution at `docs/constitution.md` covering all 5 project phases with full governance framework. Constitution establishes spec-driven development mandates, phase governance model with optional locking, technology baseline (Next.js, FastAPI, PostgreSQL), agent architecture with subagents, reusable skills library, and deployment strategy. All templates validated for alignment.

## Outcome

- ✅ Impact: Project governance framework established for Evolution of Todo project
- 📁 Files: docs/constitution.md
- 🔁 Next prompts: Ready to begin Phase 1 specification with /sp.specify
- 🧠 Reflection: Constitution provides single source of truth for all project decisions

## Evaluation notes (flywheel)

- Failure modes observed: "none"
- Graders run and results (PASS/FAIL): "N/A - constitution creation"
- Next experiment: "N/A"
