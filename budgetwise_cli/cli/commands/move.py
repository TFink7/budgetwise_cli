import typer
from decimal import Decimal
from rich import print as rprint

from budgetwise_cli.infra.db import get_session
from budgetwise_cli.services.budget_service import BudgetService

app = typer.Typer()


@app.command()
def move(src: str, dst: str, amount: str) -> None:
    # Transfer money between envelopes
    try:
        decimal_amount = Decimal(amount)

        if decimal_amount <= 0:
            typer.echo("Enter a positive amount to transfer", err=True)
            raise typer.Exit(1)

        with get_session() as db:
            BudgetService(db).move(src, dst, decimal_amount)

        rprint(
            f"Moved [bold]{decimal_amount:.2f}[/] from [red]{src}[/] to [green]{dst}[/]"
        )

    except ValueError:
        # Handle invalid decimal format
        typer.echo(
            f"Invalid amount format: {amount}. Please enter a valid number.", err=True
        )
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error moving funds: {str(e)}", err=True)
        raise typer.Exit(1)
