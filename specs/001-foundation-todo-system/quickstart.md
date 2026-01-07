# Quickstart: Phase 1 — Foundation Todo System

This guide helps you get started with the Phase 1 Todo console application.

## Prerequisites

- Python 3.11 or higher
- No external dependencies required

## Installation

Clone the repository and navigate to the project root:

```bash
git clone https://github.com/Ambreeen17/TO-DO-APP-PHASE1.git
cd TO-DO-APP-PHASE1
```

## Running the Application

### Interactive Mode (REPL)

Start the interactive command interface:

```bash
python src/main.py
# or
python src/main.py interactive
```

### Single Command Mode

Execute a single command and exit:

```bash
# Create a task
python src/main.py create "Buy groceries" "Milk, eggs, bread"

# List all tasks
python src/main.py list

# Mark a task as complete
python src/main.py complete 1

# Delete a task
python src/main.py delete 1
```

## Usage Examples

### Creating Tasks

```bash
# Create a task with title only
$ python src/main.py create "Buy groceries"
Created task 1: "Buy groceries"

# Create a task with title and description
$ python src/main.py create "Pay bills" "Electricity bill due"
Created task 2: "Pay bills"
```

### Viewing Tasks

```bash
# List all tasks
$ python src/main.py list
Tasks:
1. [ ] Buy groceries
2. [ ] Pay bills - Electricity bill due

2 tasks total (0 completed, 2 pending)

# Get task details
$ python src/main.py get 1
Task 1:
  Title: Buy groceries
  Description:
  Completed: No
```

### Updating Tasks

```bash
# Update title
$ python src/main.py update 1 --title "Buy groceries and supplies"
Updated task 1: "Buy groceries and supplies"

# Update description
$ python src/main.py update 1 --description "Milk, eggs, bread, butter"
Updated task 1: "Buy groceries and supplies"

# Mark as complete
$ python src/main.py complete 1
Task 1 marked as completed: "Buy groceries and supplies"
```

### Deleting Tasks

```bash
# Delete a task
$ python src/main.py delete 1
Deleted task 1

# Verify deletion
$ python src/main.py list
Tasks:
2. [ ] Pay bills - Electricity bill due

1 task total (0 completed, 1 pending)
```

### Interactive Mode Session

```bash
$ python src/main.py
Todo System v1.0.0
Type 'help' for available commands.

> create "Buy groceries" "Milk, eggs, bread"
Created task 1: "Buy groceries"

> create "Pay bills" "Electricity"
Created task 2: "Pay bills"

> list
1. [ ] Buy groceries - Milk, eggs, bread
2. [ ] Pay bills - Electricity

> complete 1
Task 1 marked as completed: "Buy groceries"

> list
1. [x] Buy groceries - Milk, eggs, bread
2. [ ] Pay bills - Electricity

> exit
Goodbye!
```

## Command Reference

| Command | Description |
|---------|-------------|
| `create "title" "desc"` | Create a new task |
| `list` | List all tasks |
| `get <id>` | Get task details |
| `update <id> --title "x" --desc "y" --complete --incomplete` | Update a task |
| `delete <id>` | Delete a task |
| `complete <id>` | Mark task complete |
| `incomplete <id>` | Mark task incomplete |
| `interactive` | Enter REPL mode |
| `help` | Show help |
| `exit` | Exit (in REPL mode) |

## Error Handling

The application provides clear error messages:

```bash
# Invalid task ID
$ python src/main.py get 999
Error: Task not found: 999

# Empty title
$ python src/main.py create ""
Error: Title cannot be empty

# Delete non-existent task
$ python src/main.py delete 999
Error: Task not found: 999
```

## Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Or using unittest
python -m unittest discover -s tests -v
```

## Project Structure

```
TO-DO-APP-PHASE1/
├── src/
│   ├── __init__.py
│   ├── main.py          # CLI entry point
│   ├── task.py          # Task data class
│   ├── storage.py       # In-memory storage
│   ├── validator.py     # Input validation
│   ├── operations.py    # CRUD operations
│   └── output.py        # Display formatting
├── tests/
│   ├── test_task.py
│   ├── test_storage.py
│   ├── test_validator.py
│   ├── test_operations.py
│   └── test_integration.py
├── specs/001-foundation-todo-system/
│   ├── spec.md          # Feature specification
│   ├── plan.md          # Implementation plan
│   ├── data-model.md    # Data model documentation
│   ├── quickstart.md    # This file
│   └── contracts/
│       └── cli-commands.md
└── docs/
    └── constitution.md  # Project constitution
```

## Limitations (Phase 1)

- Data persists only for the current session
- No persistence across program restarts
- Single-user console interface only
- No authentication or user accounts
- No backup or export functionality

## Next Steps

After completing Phase 1, the project will evolve to:

- **Phase 2**: Web UI, persistent storage, user authentication
- **Phase 3**: AI-powered natural language input
- **Phase 4**: Containerized deployment
- **Phase 5**: Production cloud deployment

## Getting Help

- View CLI help: `python src/main.py --help`
- View command help: `python src/main.py <command> --help`
- Check the specification: `specs/001-foundation-todo-system/spec.md`
- Review CLI contracts: `specs/001-foundation-todo-system/contracts/cli-commands.md`
