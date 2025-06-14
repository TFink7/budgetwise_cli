#!/usr/bin/env python3
import subprocess
import shlex
from typing import List


def start_services() -> None:
    """Start the budgetwise services using Docker Compose."""
    print("Starting budgetwise services...")
    subprocess.run(["docker", "compose", "up", "-d"], check=True)


def shutdown_services() -> None:
    """Stop all budgetwise services."""
    print("Shutting down services...")
    subprocess.run(["docker", "compose", "down"], check=True)


def run_command(cmd: str) -> subprocess.CompletedProcess[bytes]:
    # Run a budgetwise command in the container.
    docker_cmd: List[str] = [
        "docker",
        "compose",
        "exec",
        "app",
        "python",
        "-m",
        "budgetwise_cli.cli.app",
    ]

    args: List[str] = shlex.split(cmd)

    full_cmd: List[str] = docker_cmd + args
    return subprocess.run(full_cmd, check=False, text=False)


def interactive_shell() -> None:
    """Run an interactive budgetwise shell."""
    print("Welcome to BudgetWise Interactive Shell!")
    print("Type 'exit' to quit, 'help' for available commands.")

    while True:
        try:
            cmd = input("\nbudgetwise> ")
            cmd = cmd.strip()

            if cmd.lower() == "exit":
                break
            elif cmd.lower() == "help":
                run_command("--help")
            elif cmd:
                run_command(cmd)
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    try:
        start_services()
        interactive_shell()
    finally:
        shutdown_services()
