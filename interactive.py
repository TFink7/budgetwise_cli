#!/usr/bin/env python3
import subprocess
import shlex
from typing import List


def start_services() -> None:
    """Start the budgetwise services using Docker Compose."""
    print("Starting budgetwise services...")
    subprocess.run(["docker", "compose", "up", "-d"], check=True)


def run_migrations() -> None:
    # Check if migrations table exists
    check_table = subprocess.run(
        [
            "docker",
            "compose",
            "exec",
            "db",
            "psql",
            "-U",
            "postgres",
            "-d",
            "budgetwise",
            "-c",
            "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name='alembic_version');",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    table_exists = "t" in check_table.stdout.lower()

    # For first run or if table doesn't exist
    if not table_exists:
        subprocess.run(
            [
                "docker",
                "compose",
                "exec",
                "app",
                "alembic",
                "revision",
                "--autogenerate",
                "-m",
                "Initial schema",
            ],
            check=False,
        )

    # Try to run migrations
    result = subprocess.run(
        ["docker", "compose", "exec", "app", "alembic", "upgrade", "head"],
        capture_output=True,
        text=True,
        check=False,
    )

    if "can't locate revision" in result.stderr.lower():
        subprocess.run(
            [
                "docker",
                "compose",
                "exec",
                "db",
                "psql",
                "-U",
                "postgres",
                "-d",
                "budgetwise",
                "-c",
                "DROP TABLE IF EXISTS alembic_version;",
            ],
            check=False,
        )
        subprocess.run(
            [
                "docker",
                "compose",
                "exec",
                "app",
                "alembic",
                "revision",
                "--autogenerate",
                "-m",
                "Fresh start",
            ],
            check=False,
        )
        upgrade_result = subprocess.run(
            ["docker", "compose", "exec", "app", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=False,
        )
        if upgrade_result.returncode == 0:
            print("Migration history reset")
        else:
            print(f"{upgrade_result.stderr}")
    elif result.returncode == 0:
        print("Database migrations completed successfully")
    else:
        print(f"{result.stderr}")


def shutdown_services() -> None:
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
        run_migrations()
        interactive_shell()
    finally:
        shutdown_services()
