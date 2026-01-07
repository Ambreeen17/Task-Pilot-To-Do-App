---

description: "Task list for Phase 1 Foundation Todo System"
---

# Tasks: Phase 1 — Foundation Todo System

**Input**: Design documents from `specs/001-foundation-todo-system/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/cli-commands.md
**Tests**: All test tasks are MANDATORY for this feature

**Organization**: Tasks are grouped by phase to ensure proper dependency order.

## Format: `[ID] [P?] [Phase] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Phase]**: Which phase this task belongs to (F=Foundation, V=Validation, O=Operations, C=CLI, Q=QA)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project structure

---

## Phase F: Foundation (Core Data Layer)

**Purpose**: Core infrastructure that MUST be complete before ANY other work begins.

**Critical**: No other tasks can begin until Foundation phase is complete.

### Tests for Foundation (MUST FAIL before implementation)

> **NOTE**: Write tests FIRST, ensure they FAIL before implementation

- [x] T001 [F] Test Task creation with all attributes in tests/unit/test_task.py
- [x] T002 [F] Test Task.to_dict() serialization in tests/unit/test_task.py
- [x] T003 [F] Test Task.from_dict() deserialization in tests/unit/test_task.py
- [x] T004 [F] Test TaskStorage.add() and get() in tests/unit/test_storage.py
- [x] T005 [F] Test ID generation uniqueness in tests/unit/test_storage.py
- [x] T006 [F] Test TaskStorage CRUD operations in tests/unit/test_storage.py

### Implementation for Foundation

- [x] T007 [F] Create Task data class in src/task.py
  - Attributes: id (str), title (str), description (str), completed (bool)
  - Methods: __init__, to_dict, from_dict, __repr__
  - Skill: CRUD Skill (Entity creation)

- [x] T008 [F] Create TaskStorage class in src/storage.py
  - In-memory dictionary storage
  - Methods: __init__, add, get, get_all, update, delete, exists
  - Skill: CRUD Skill (Data storage)

- [x] T009 [F] Implement ID generation function in src/storage.py
  - Sequential ID generation (1, 2, 3, ...)
  - Ensures uniqueness within session
  - Skill: CRUD Skill (ID generation)

**Checkpoint**: Foundation ready - all other phases can now begin

---

## Phase V: Validation Layer

**Purpose**: Input validation and error handling for all operations.

### Tests for Validation (MUST FAIL before implementation)

- [x] T010 [V] Test title validation - empty title rejection in tests/unit/test_validator.py
- [x] T011 [V] Test title validation - max length enforcement in tests/unit/test_validator.py
- [x] T012 [V] Test description validation - max length enforcement in tests/unit/test_validator.py
- [x] T013 [V] Test task ID validation - format check in tests/unit/test_validator.py
- [x] T014 [V] Test error message formatting in tests/unit/test_validator.py

### Implementation for Validation

- [x] T015 [V] Create validation module in src/validator.py
  - Function: validate_title(title: str) -> tuple[bool, str]
  - Function: validate_description(desc: str) -> tuple[bool, str]
  - Function: validate_task_id(id: str) -> tuple[bool, str]
  - Function: sanitize_input(text: str) -> str
  - Skill: Validation Skill (Input validation)

**Checkpoint**: Validation ready - Operations phase can use validation functions

---

## Phase O: Core Operations

**Purpose**: CRUD operations for task management.

### Tests for Operations (MUST FAIL before implementation)

- [x] T016 [O] Test create_task() operation in tests/unit/test_operations.py
- [x] T017 [O] Test list_tasks() operation in tests/unit/test_operations.py
- [x] T018 [O] Test update_task() operation in tests/unit/test_operations.py
- [x] T019 [O] Test delete_task() operation in tests/unit/test_operations.py
- [x] T020 [O] Test mark_complete() operation in tests/unit/test_operations.py
- [x] T021 [O] Test operation error handling in tests/unit/test_operations.py

### Implementation for Operations

- [x] T022 [P] [O] Implement create_task() in src/operations.py
  - Generates unique ID, creates Task, stores in TaskStorage
  - Skill: CRUD Skill (Create), Validation Skill (Title validation)

- [x] T023 [P] [O] Implement list_tasks() in src/operations.py
  - Retrieves all tasks from storage
  - Skill: CRUD Skill (Read)

- [x] T024 [P] [O] Implement update_task() in src/operations.py
  - Updates specified fields, preserves others
  - Skill: CRUD Skill (Update), Validation Skill (Input validation)

- [x] T025 [O] Implement delete_task() in src/operations.py
  - Removes task from storage by ID
  - Skill: CRUD Skill (Delete)

- [x] T026 [O] Implement mark_complete() in src/operations.py
  - Toggles completed status
  - Skill: CRUD Skill (Update)

**Checkpoint**: Operations ready - CLI interface can now be built

---

## Phase C: CLI Interface

**Purpose**: Console-based user interface with REPL mode.

### Tests for CLI (MUST FAIL before implementation)

- [x] T027 [C] Test CLI argument parsing in tests/unit/test_cli.py
- [x] T028 [C] Test command routing in tests/unit/test_cli.py
- [x] T029 [C] Test output formatting in tests/unit/test_cli.py
- [x] T030 [C] Test REPL loop in tests/integration/test_repl.py
- [x] T031 [C] Test interactive commands in tests/integration/test_repl.py

### Implementation for CLI

- [x] T032 [C] Create output formatting module in src/output.py
  - Function: format_task(task: Task) -> str
  - Function: format_task_list(tasks: List[Task]) -> str
  - Function: format_success(message: str) -> str
  - Function: format_error(message: str) -> str
  - Function: format_empty_list() -> str
  - Skill: UI Composition Skill (Display formatting)

- [x] T033 [C] Implement CLI argument parsing in src/main.py
  - Parse command: create, list, get, update, delete, complete, incomplete, interactive
  - Parse arguments per command specification
  - Skill: UI Composition Skill (Input parsing)

- [x] T034 [C] Implement CLI command handlers in src/main.py
  - Route commands to operations
  - Format output for display
  - Handle errors with user-friendly messages
  - Skill: UI Composition Skill (Command handling)

- [x] T035 [C] Implement interactive REPL mode in src/main.py
  - Continuous input loop
  - Commands: help, create, list, get, update, delete, complete, incomplete, clear, exit
  - Skill: UI Composition Skill (Interactive interface)

**Checkpoint**: CLI ready - QA can run full integration tests

---

## Phase Q: QA & Regression

**Purpose**: Comprehensive testing and acceptance validation.

### Integration Tests

- [x] T036 [Q] Test full create → list → update → complete → delete flow in tests/integration/test_full_flow.py
- [x] T037 [Q] Test error recovery scenarios in tests/integration/test_error_recovery.py
- [x] T038 [Q] Test deterministic output in tests/integration/test_determinism.py
- [x] T039 [Q] Test edge cases (empty list, invalid IDs) in tests/integration/test_edge_cases.py

### Acceptance Checklist

- [x] T040 [Q] Verify SC-001: Create task and verify in list in tests/acceptance/test_sc001.py
- [x] T041 [Q] Verify SC-002: Update task and verify change in tests/acceptance/test_sc002.py
- [x] T042 [Q] Verify SC-003: Delete task and verify removal in tests/acceptance/test_sc003.py
- [x] T043 [Q] Verify SC-004: All operations provide feedback in tests/acceptance/test_sc004.py
- [x] T044 [Q] Verify SC-005: All tasks have unique IDs in tests/acceptance/test_sc005.py
- [x] T045 [Q] Verify SC-006: Edge cases handled gracefully in tests/acceptance/test_sc006.py

### Final Validation

- [x] T046 [Q] Run full test suite and verify 100% pass rate
- [x] T047 [Q] Verify quickstart.md works correctly
- [x] T048 [Q] Document test coverage report

---

## Task Summary Table

| ID | Phase | Agent | Skill | Output | Dependencies |
|----|-------|-------|-------|--------|--------------|
| T001 | F | QA | Test Executor | tests/unit/test_task.py | - |
| T002 | F | QA | Test Executor | tests/unit/test_task.py | - |
| T003 | F | QA | Test Executor | tests/unit/test_task.py | - |
| T004 | F | QA | Test Executor | tests/unit/test_storage.py | - |
| T005 | F | QA | Test Executor | tests/unit/test_storage.py | - |
| T006 | F | QA | Test Executor | tests/unit/test_storage.py | - |
| T007 | F | Backend | CRUD Skill | src/task.py | - |
| T008 | F | Backend | CRUD Skill | src/storage.py | - |
| T009 | F | Backend | CRUD Skill | src/storage.py | T008 |
| T010 | V | QA | Test Executor | tests/unit/test_validator.py | T007 |
| T011 | V | QA | Test Executor | tests/unit/test_validator.py | T007 |
| T012 | V | QA | Test Executor | tests/unit/test_validator.py | T007 |
| T013 | V | QA | Test Executor | tests/unit/test_validator.py | T007 |
| T014 | V | QA | Test Executor | tests/unit/test_validator.py | T007 |
| T015 | V | Backend | Validation Skill | src/validator.py | T007 |
| T016 | O | QA | Test Executor | tests/unit/test_operations.py | T007 |
| T017 | O | QA | Test Executor | tests/unit/test_operations.py | T007 |
| T018 | O | QA | Test Executor | tests/unit/test_operations.py | T007 |
| T019 | O | QA | Test Executor | tests/unit/test_operations.py | T007 |
| T020 | O | QA | Test Executor | tests/unit/test_operations.py | T007 |
| T021 | O | QA | Test Executor | tests/unit/test_operations.py | T007 |
| T022 | O | Backend | CRUD, Validation | src/operations.py | T009, T015 |
| T023 | O | Backend | CRUD Skill | src/operations.py | T008 |
| T024 | O | Backend | CRUD, Validation | src/operations.py | T008, T015 |
| T025 | O | Backend | CRUD Skill | src/operations.py | T008 |
| T026 | O | Backend | CRUD Skill | src/operations.py | T008 |
| T027 | C | QA | Test Executor | tests/unit/test_cli.py | T022 |
| T028 | C | QA | Test Executor | tests/unit/test_cli.py | T022 |
| T029 | C | QA | Test Executor | tests/unit/test_cli.py | T022 |
| T030 | C | QA | Test Executor | tests/integration/test_repl.py | T035 |
| T031 | C | QA | Test Executor | tests/integration/test_repl.py | T035 |
| T032 | C | Backend | UI Composition | src/output.py | T007 |
| T033 | C | Backend | UI Composition | src/main.py | T022 |
| T034 | C | Backend | UI Composition | src/main.py | T022, T032 |
| T035 | C | Backend | UI Composition | src/main.py | T032, T033 |
| T036 | Q | QA | Test Executor | tests/integration/test_full_flow.py | T022-T026, T035 |
| T037 | Q | QA | Test Executor | tests/integration/test_error_recovery.py | T022-T026, T035 |
| T038 | Q | QA | Test Executor | tests/integration/test_determinism.py | T022-T026, T035 |
| T039 | Q | QA | Test Executor | tests/integration/test_edge_cases.py | T022-T026, T035 |
| T040 | Q | QA | Test Executor | tests/acceptance/test_sc001.py | T022 |
| T041 | Q | QA | Test Executor | tests/acceptance/test_sc002.py | T024 |
| T042 | Q | QA | Test Executor | tests/acceptance/test_sc003.py | T025 |
| T043 | Q | QA | Test Executor | tests/acceptance/test_sc004.py | T032-T035 |
| T044 | Q | QA | Test Executor | tests/acceptance/test_sc005.py | T009 |
| T045 | Q | QA | Test Executor | tests/acceptance/test_sc006.py | T015, T022-T026 |
| T046 | Q | QA | Test Executor | All tests | T001-T045 |
| T047 | Q | QA | Test Executor | quickstart.md validation | T035 |
| T048 | Q | QA | Test Executor | Coverage report | T046 |

---

## Dependency Graph

```
FOUNDATION (T001-T009) ──────┬──────────────────────────────────────
                              │
                              ▼
VALIDATION (T010-T015) ──────┼──────────────────────────────────────
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
    OPERATIONS           OPERATIONS           OPERATIONS
    (T022 Create)        (T023 List)         (T024 Update)
          │                   │                   │
          │                   │                   ▼
          │                   │              OPERATIONS
          │                   │              (T025 Delete)
          │                   │                   │
          │                   │                   ▼
          │                   │              OPERATIONS
          │                   │              (T026 Complete)
          │                   │                   │
          └───────────────────┴───────────────────┘
                              │
                              ▼
                    CLI OUTPUT (T032)
                              │
                              ▼
                    CLI ARG PARSE (T033)
                              │
                              ▼
                    CLI HANDLERS (T034)
                              │
                              ▼
                    CLI REPL (T035)
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
    INTEGRATION           INTEGRATION           INTEGRATION
    (T036-T039)           (T036-T039)           (T036-T039)
          │                   │                   │
          └───────────────────┴───────────────────┘
                              │
                              ▼
                    ACCEPTANCE (T040-T045)
                              │
                              ▼
                    FINAL VALIDATION (T046-T048)
```

---

## Skill Usage Mapping

| Skill | Tasks Using | Purpose |
|-------|-------------|---------|
| CRUD Skill | T007, T008, T009, T022, T023, T024, T025, T026 | Entity creation, storage, CRUD operations |
| Validation Skill | T015, T022, T024 | Input validation for title, description, IDs |
| UI Composition Skill | T032, T033, T034, T035 | Output formatting, CLI interface, REPL |
| Test Executor Skill | T001-T006, T010-T014, T016-T021, T027-T031, T036-T048 | All test tasks |

---

## Parallel Execution Opportunities

### Within Foundation (T001-T009)
- T001-T003 can run in parallel (different test functions)
- T004-T006 can run in parallel (different test functions)
- T007-T009 must be sequential (dependencies)

### Within Validation (T010-T015)
- T010-T014 can run in parallel (different validation tests)
- T015 depends on T007 (Task class must exist)

### Within Operations (T016-T026)
- T016-T021 can run in parallel (different operation tests)
- T022-T026 depend on T008, T009, T015

### Within CLI (T027-T035)
- T027-T029 can run in parallel (different CLI tests)
- T030-T031 depend on T035
- T032 independent
- T033-T035 sequential (dependencies)

### QA Phase (T036-T048)
- T036-T039 can run in parallel (different integration tests)
- T040-T045 can run in parallel (different acceptance tests)
- T046-T048 depend on all previous tests

---

## Dependencies & Execution Order

### Mandatory Sequential Order

1. **Foundation Phase**: T001 → T009 (all must complete)
2. **Validation Phase**: T010 → T015 (depends on T007)
3. **Operations Phase**: T016 → T026 (depends on Foundation + Validation)
4. **CLI Phase**: T027 → T035 (depends on Operations)
5. **QA Phase**: T036 → T048 (depends on all implementation)

### Recommended Parallel Strategy

With multiple agents available:

- **Agent 1**: Tests T001-T006, then implementation T007-T009
- **Agent 2**: Tests T010-T014, then implementation T015 (waits for T007)
- **Agent 3**: Tests T016-T021, then implementation T022-T026 (waits for Foundation)
- **Agent 4**: Tests T027-T029, T030-T031, then implementation T032-T035 (waits for Operations)
- **Agent 5**: QA Phase T036-T048 (waits for all implementation)

---

## Completion Criteria

### Implementation Complete When:
- [x] All implementation tasks (T007-T009, T015, T022-T026, T032-T035) are complete
- [x] All files exist at specified paths
- [x] Code passes linting (if configured)

### Testing Complete When:
- [x] All test tasks (T001-T006, T010-T014, T016-T021, T027-T031, T036-T045) are complete
- [x] All tests pass (T046)
- [x] Test coverage meets requirements

### Acceptance Complete When:
- [x] All success criteria verified (T040-T045)
- [x] Quickstart guide validated (T047)
- [x] Coverage report generated (T048)

---

## Next Steps

1. **Execute Foundation Phase**: Start with tests T001-T003, then implement T007-T009
2. **Execute Validation Phase**: After T007, write tests T010-T014, implement T015
3. **Execute Operations Phase**: After Foundation, write tests T016-T021, implement T022-T026
4. **Execute CLI Phase**: After Operations, write tests T027-T031, implement T032-T035
5. **Execute QA Phase**: After CLI, run integration tests T036-T039, acceptance T040-T045
6. **Final Validation**: Run T046-T048 to complete Phase 1

---

## Notes

- **[P]**标记的任务可以在同一阶段并行运行（不同的文件，无依赖）
- **所有测试任务必须在实现之前完成，且必须FAIL**
- **提交代码**：每个任务或逻辑组完成后提交
- **避免**：模糊任务、同一文件冲突、破坏独立性的跨任务依赖
- **停止点**：在任何检查点停止，单独验证功能
