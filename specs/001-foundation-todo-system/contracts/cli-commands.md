# CLI Command Contracts: Phase 1 — Foundation Todo System

This document defines the command-line interface contracts for the Phase 1 Todo system.

## Command Overview

| Command | Description |
|---------|-------------|
| `create` | Create a new task |
| `list` | List all tasks |
| `get` | Get a specific task |
| `update` | Update an existing task |
| `delete` | Delete a task |
| `complete` | Mark a task as complete |
| `incomplete` | Mark a task as incomplete |
| `interactive` | Enter interactive REPL mode |

## Global Options

| Option | Description |
|--------|-------------|
| `--help` | Display help message |
| `--version` | Display version information |

## Command Details

### create

Create a new task with a title and optional description.

**Usage:**
```bash
python main.py create "Task title" "Optional description"
```

**Arguments:**

| Position | Name | Type | Required | Default | Description |
|----------|------|------|----------|---------|-------------|
| 1 | title | string | Yes | N/A | Short task title |
| 2 | description | string | No | `""` | Detailed task description |

**Output (Success):**
```
Created task 1: "Buy groceries"
```

**Output (Error):**
```
Error: Title cannot be empty
```

---

### list

Display all tasks in a formatted list.

**Usage:**
```bash
python main.py list
```

**Options:**
| Option | Description |
|--------|-------------|
| `--completed` | Show only completed tasks |
| `--pending` | Show only pending tasks |
| `--json` | Output in JSON format |

**Output (With Tasks):**
```
Tasks:
1. [ ] Buy groceries - Milk, eggs, bread
2. [x] Pay bills - Electricity bill
3. [ ] Call mom

3 tasks total (1 completed, 2 pending)
```

**Output (Empty):**
```
No tasks yet. Create one with: python main.py create "Your task"
```

---

### get

Display details of a specific task.

**Usage:**
```bash
python main.py get <task_id>
```

**Arguments:**

| Position | Name | Type | Required | Description |
|----------|------|------|----------|-------------|
| 1 | task_id | string | Yes | The task ID to retrieve |

**Output (Success):**
```
Task 1:
  Title: Buy groceries
  Description: Milk, eggs, bread
  Completed: No
```

**Output (Error):**
```
Error: Task not found: 1
```

---

### update

Update an existing task's title, description, or completion status.

**Usage:**
```bash
python main.py update <task_id> [--title "New title"] [--description "New description"] [--complete | --incomplete]
```

**Arguments:**

| Position | Name | Type | Required | Description |
|----------|------|------|----------|-------------|
| 1 | task_id | string | Yes | The task ID to update |

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--title` | string | New task title |
| `--description` | string | New task description |
| `--complete` | flag | Mark task as completed |
| `--incomplete` | flag | Mark task as incomplete |

**Output (Success):**
```
Updated task 1: "Buy groceries"
```

**Output (Error):**
```
Error: Task not found: 1
Error: Title cannot be empty
```

---

### delete

Delete an existing task.

**Usage:**
```bash
python main.py delete <task_id>
```

**Arguments:**

| Position | Name | Type | Required | Description |
|----------|------|------|----------|-------------|
| 1 | task_id | string | Yes | The task ID to delete |

**Output (Success):**
```
Deleted task 1
```

**Output (Error):**
```
Error: Task not found: 1
```

---

### complete

Mark a task as completed.

**Usage:**
```bash
python main.py complete <task_id>
```

**Arguments:**

| Position | Name | Type | Required | Description |
|----------|------|------|----------|-------------|
| 1 | task_id | string | Yes | The task ID to mark complete |

**Output (Success):**
```
Task 1 marked as completed: "Buy groceries"
```

**Output (Error):**
```
Error: Task not found: 1
```

---

### incomplete

Mark a task as incomplete (not completed).

**Usage:**
```bash
python main.py incomplete <task_id>
```

**Arguments:**

| Position | Name | Type | Required | Description |
|----------|------|------|----------|-------------|
| 1 | task_id | string | Yes | The task ID to mark incomplete |

**Output (Success):**
```
Task 1 marked as incomplete: "Buy groceries"
```

**Output (Error):**
```
Error: Task not found: 1
```

---

### interactive

Enter interactive REPL mode for continuous task management.

**Usage:**
```bash
python main.py interactive
# or just
python main.py
```

**REPL Commands:**

| Command | Description | Example |
|---------|-------------|---------|
| `help` | Show available commands | `help` |
| `create "title" "desc"` | Create a task | `create "Buy groceries" "Milk, eggs"` |
| `list` | List all tasks | `list` |
| `get <id>` | Get task details | `get 1` |
| `update <id> --title "x"` | Update task | `update 1 --title "New title"` |
| `delete <id>` | Delete task | `delete 1` |
| `complete <id>` | Mark complete | `complete 1` |
| `incomplete <id>` | Mark incomplete | `incomplete 1` |
| `clear` | Clear all tasks | `clear` |
| `exit` | Exit REPL | `exit` |

**REPL Example Session:**
```
$ python main.py interactive
Todo System v1.0.0
Type 'help' for available commands.

> create "Buy groceries" "Milk, eggs, bread"
Created task 1: "Buy groceries"

> create "Pay bills" "Electricity bill"
Created task 2: "Pay bills"

> list
1. [ ] Buy groceries - Milk, eggs, bread
2. [ ] Pay bills - Electricity bill

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

## Error Messages

| Error Type | Message | Example |
|------------|---------|---------|
| Task not found | `Error: Task not found: {id}` | `Error: Task not found: 5` |
| Empty title | `Error: Title cannot be empty` | `Error: Title cannot be empty` |
| Title too long | `Error: Title exceeds maximum length (500)` | `Error: Title exceeds maximum length (500)` |
| Description too long | `Error: Description exceeds maximum length (5000)` | `Error: Description exceeds maximum length (5000)` |
| Invalid ID format | `Error: Invalid task ID format` | `Error: Invalid task ID format` |
| No changes specified | `Error: No changes specified` | `Error: No changes specified` |
| Already completed | `Error: Task {id} is already completed` | `Error: Task 1 is already completed` |
| Already incomplete | `Error: Task {id} is already incomplete` | `Error: Task 1 is already incomplete` |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid command or arguments |

## Input Format

### Title Input Rules

- Minimum: 1 character
- Maximum: 500 characters
- Leading/trailing whitespace is preserved

### Description Input Rules

- Minimum: 0 characters
- Maximum: 5000 characters
- Leading/trailing whitespace is preserved

### Task ID Format

- String representation of a positive integer
- Examples: `1`, `42`, `100`
