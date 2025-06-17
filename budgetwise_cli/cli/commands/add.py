import typer
from decimal import Decimal
from rich import print as rprint
from budgetwise_cli.services.budget_service import BudgetService
from budgetwise_cli.infra.db import get_session


def add(env: str, amount: str, note: str = "") -> None:
    """Add a transaction to an envelope.

    Format: add <envelope> <amount> [note]

    Examples:
      add Groceries 50.00 "Weekly shopping"
      add Salary 1500.00 "Monthly income"
      add Entertainment 25.50
    """
    try:
        decimal_amount = Decimal(amount)
        with get_session() as db:
            tx = BudgetService(db).add_transaction(env, decimal_amount, note)
        rprint(
            f"Added transaction: [bold]{tx.type.value}[/bold] of [bold]{tx.amount}[/bold] to envelope [bold]{tx.envelope.name}[/bold]"
        )
    except Exception as e:
        typer.echo(f"error adding transaction: {str(e)}", err=True)
        raise typer.Exit(1)
