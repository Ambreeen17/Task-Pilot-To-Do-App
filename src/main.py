#!/usr/bin/env python3
"""Todo System CLI - Phase 1 Foundation."""

import argparse
import sys
from typing import List, Optional

from storage import TaskStorage
from task import Task
from operations import create_task, list_tasks, update_task, delete_task, mark_complete
from output import format_task, format_task_list, format_success, format_error, format_empty_list
from validator import validate_task_id


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.

    Args:
        args: Optional list of arguments (defaults to sys.argv[1:])

    Returns:
        Parsed namespace with command and arguments
    """
    parser = argparse.ArgumentParser(
        prog="todo",
        description="Todo System - A simple command-line task manager",
        epilog="Use 'todo <command> --help' for more information on a specific command."
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # create command
    create_parser = subparsers.add_parser("create", help="Create a new task")
    create_parser.add_argument("title", help="Task title")
    create_parser.add_argument("description", nargs="?", default="", help="Task description (optional)")

    # list command
    list_parser = subparsers.add_parser("list", help="List all tasks")
    list_parser.add_argument("--completed", action="store_true", help="Show only completed tasks")
    list_parser.add_argument("--pending", action="store_true", help="Show only pending tasks")

    # get command
    get_parser = subparsers.add_parser("get", help="Get a specific task")
    get_parser.add_argument("task_id", help="Task ID")

    # update command
    update_parser = subparsers.add_parser("update", help="Update an existing task")
    update_parser.add_argument("task_id", help="Task ID")
    update_parser.add_argument("--title", help="New task title")
    update_parser.add_argument("--description", help="New task description")

    # delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("task_id", help="Task ID")

    # complete command
    complete_parser = subparsers.add_parser("complete", help="Mark a task as complete")
    complete_parser.add_argument("task_id", help="Task ID")

    # incomplete command
    incomplete_parser = subparsers.add_parser("incomplete", help="Mark a task as incomplete")
    incomplete_parser.add_argument("task_id", help="Task ID")

    # interactive command
    subparsers.add_parser("interactive", help="Enter interactive REPL mode")

    return parser.parse_args(args)


def cmd_create(storage: TaskStorage, args: argparse.Namespace) -> int:
    """Handle create command."""
    result = create_task(storage, args.title, args.description)
    if isinstance(result, tuple):
        print(format_error(result[1]))
        return 1
    print(format_success(f'Created task {result.id}: "{result.title}"'))
    return 0


def cmd_list(storage: TaskStorage, args: argparse.Namespace) -> int:
    """Handle list command."""
    tasks = list_tasks(storage)

    # Filter if needed
    if args.completed:
        tasks = [t for t in tasks if t.completed]
    elif args.pending:
        tasks = [t for t in tasks if not t.completed]

    print(format_task_list(tasks))
    return 0


def cmd_get(storage: TaskStorage, args: argparse.Namespace) -> int:
    """Handle get command."""
    # Validate task_id format
    is_valid, error = validate_task_id(args.task_id)
    if not is_valid:
        print(format_error(error))
        return 2

    task = storage.get(args.task_id)
    if task is None:
        print(format_error(f"Task not found: {args.task_id}"))
        return 1
    print(format_task(task))
    return 0


def cmd_update(storage: TaskStorage, args: argparse.Namespace) -> int:
    """Handle update command."""
    # Validate task_id format
    is_valid, error = validate_task_id(args.task_id)
    if not is_valid:
        print(format_error(error))
        return 2

    # Check if at least one field is being updated
    if args.title is None and args.description is None:
        print(format_error("No changes specified. Use --title or --description."))
        return 2

    result = update_task(
        storage,
        args.task_id,
        title=args.title,
        description=args.description
    )
    if isinstance(result, tuple):
        print(format_error(result[1]))
        return 1
    print(format_success(f'Updated task {result.id}: "{result.title}"'))
    return 0


def cmd_delete(storage: TaskStorage, args: argparse.Namespace) -> int:
    """Handle delete command."""
    # Validate task_id format
    is_valid, error = validate_task_id(args.task_id)
    if not is_valid:
        print(format_error(error))
        return 2

    result = delete_task(storage, args.task_id)
    if isinstance(result, tuple):
        print(format_error(result[1]))
        return 1
    print(format_success(f"Deleted task {args.task_id}"))
    return 0


def cmd_complete(storage: TaskStorage, args: argparse.Namespace) -> int:
    """Handle complete command."""
    # Validate task_id format
    is_valid, error = validate_task_id(args.task_id)
    if not is_valid:
        print(format_error(error))
        return 2

    result = mark_complete(storage, args.task_id, complete=True)
    if isinstance(result, tuple):
        print(format_error(result[1]))
        return 1
    print(format_success(f'Task {result.id} marked as completed: "{result.title}"'))
    return 0


def cmd_incomplete(storage: TaskStorage, args: argparse.Namespace) -> int:
    """Handle incomplete command."""
    # Validate task_id format
    is_valid, error = validate_task_id(args.task_id)
    if not is_valid:
        print(format_error(error))
        return 2

    result = mark_complete(storage, args.task_id, complete=False)
    if isinstance(result, tuple):
        print(format_error(result[1]))
        return 1
    print(format_success(f'Task {result.id} marked as incomplete: "{result.title}"'))
    return 0


def cmd_interactive(storage: TaskStorage) -> int:
    """Enter interactive REPL mode."""
    print("Todo System v1.0.0")
    print("Type 'help' for available commands.")
    print()

    while True:
        try:
            cmd_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return 0

        if not cmd_input:
            continue

        parts = cmd_input.split()
        sub_cmd = parts[0].lower()

        if sub_cmd in ("exit", "quit"):
            print("Goodbye!")
            return 0
        elif sub_cmd == "help":
            print("""
Available commands:
  create "title" "desc"  - Create a new task
  list                   - List all tasks
  get <id>               - Get task details
  update <id> --title "x" --description "y" - Update a task
  delete <id>            - Delete a task
  complete <id>          - Mark task as complete
  incomplete <id>        - Mark task as incomplete
  clear                  - Clear all tasks
  exit                   - Exit REPL
""")
        elif sub_cmd == "create":
            if len(parts) < 2:
                print(format_error("Usage: create \"title\" \"description\""))
            else:
                # Parse quoted arguments
                title = parts[1].strip('"')
                desc = parts[2].strip('"') if len(parts) > 2 else ""
                result = create_task(storage, title, desc)
                if isinstance(result, tuple):
                    print(format_error(result[1]))
                else:
                    print(format_success(f'Created task {result.id}: "{result.title}"'))
        elif sub_cmd == "list":
            tasks = list_tasks(storage)
            print(format_task_list(tasks))
        elif sub_cmd == "get":
            if len(parts) < 2:
                print(format_error("Usage: get <id>"))
            else:
                task_id = parts[1]
                task = storage.get(task_id)
                if task is None:
                    print(format_error(f"Task not found: {task_id}"))
                else:
                    print(format_task(task))
        elif sub_cmd == "update":
            if len(parts) < 2:
                print(format_error("Usage: update <id> [--title \"x\"] [--description \"y\"]"))
            else:
                task_id = parts[1]
                title = None
                description = None
                i = 2
                while i < len(parts):
                    if parts[i] == "--title" and i + 1 < len(parts):
                        title = parts[i + 1].strip('"')
                        i += 2
                    elif parts[i] == "--description" and i + 1 < len(parts):
                        description = parts[i + 1].strip('"')
                        i += 2
                    else:
                        i += 1
                result = update_task(storage, task_id, title=title, description=description)
                if isinstance(result, tuple):
                    print(format_error(result[1]))
                else:
                    print(format_success(f'Updated task {result.id}: "{result.title}"'))
        elif sub_cmd == "delete":
            if len(parts) < 2:
                print(format_error("Usage: delete <id>"))
            else:
                task_id = parts[1]
                result = delete_task(storage, task_id)
                if isinstance(result, tuple):
                    print(format_error(result[1]))
                else:
                    print(format_success(f"Deleted task {task_id}"))
        elif sub_cmd == "complete":
            if len(parts) < 2:
                print(format_error("Usage: complete <id>"))
            else:
                task_id = parts[1]
                result = mark_complete(storage, task_id, complete=True)
                if isinstance(result, tuple):
                    print(format_error(result[1]))
                else:
                    print(format_success(f'Task {result.id} marked as completed: "{result.title}"'))
        elif sub_cmd == "incomplete":
            if len(parts) < 2:
                print(format_error("Usage: incomplete <id>"))
            else:
                task_id = parts[1]
                result = mark_complete(storage, task_id, complete=False)
                if isinstance(result, tuple):
                    print(format_error(result[1]))
                else:
                    print(format_success(f'Task {result.id} marked as incomplete: "{result.title}"'))
        elif sub_cmd == "clear":
            # Delete all tasks
            tasks = list_tasks(storage)
            for task in tasks:
                delete_task(storage, task.id)
            print(format_success("All tasks cleared"))
        else:
            print(format_error(f"Unknown command: {sub_cmd}"))


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI.

    Args:
        args: Optional list of arguments

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parsed = parse_args(args)

    if parsed.command is None:
        # No command specified, enter interactive mode
        storage = TaskStorage()
        return cmd_interactive(storage)

    storage = TaskStorage()

    # Route to appropriate handler
    commands = {
        "create": cmd_create,
        "list": cmd_list,
        "get": cmd_get,
        "update": cmd_update,
        "delete": cmd_delete,
        "complete": cmd_complete,
        "incomplete": cmd_incomplete,
        "interactive": lambda s, a: cmd_interactive(s),
    }

    handler = commands.get(parsed.command)
    if handler:
        return handler(storage, parsed)
    else:
        print(format_error(f"Unknown command: {parsed.command}"))
        return 2


if __name__ == "__main__":
    sys.exit(main())
