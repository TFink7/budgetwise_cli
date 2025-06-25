import typer
from decimal import Decimal
from rich import print as rprint
from budgetwise_cli.infra.db import get_session
from budgetwise_cli.services.budget_service import BudgetService


def add(
    env: str = typer.Argument(..., help="Envelope name"),
    amount: str = typer.Argument(
        ..., help="Transaction amount (use negative for expenses)"
    ),
    note: str = typer.Argument("", help="Optional transaction note"),
    expense: bool = typer.Option(
        False, "--expense", "-e", help="Mark as expense (amount will be negative)"
    ),
) -> None:
    """Add a transaction to an envelope.

    Format: add <envelope> <amount> [note]
    Or use: add <envelope> <amount> --expense [note]

    Examples:
      add Groceries 50.00 --expense "Weekly shopping"
      add Salary 1500.00 "Monthly income"
      add Entertainment 25.50 --expense
    """
    try:
        # Parse amount and apply sign if needed
        decimal_amount = Decimal(amount)
        if expense and decimal_amount > 0:
            decimal_amount = -decimal_amount

        with get_session() as db:
            tx = BudgetService(db).add_transaction(env, decimal_amount, note)

            tx_info = {
                "type": tx.type.value if tx.type else "Unknown",
                "amount": tx.amount,
                "envelope_name": tx.envelope.name if tx.envelope else env,
            }

        rprint(
            f"Added transaction: [bold]{tx_info['type']}[/bold] of "
            f"[bold]{tx_info['amount']}[/bold] to envelope "
            f"[bold]{tx_info['envelope_name']}[/bold]"
        )
    except Exception as e:
        typer.echo(f"error adding transaction: {str(e)}", err=True)
        raise typer.Exit(1)
