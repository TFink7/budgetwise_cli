import typer
from decimal import Decimal
from rich import print as rprint

from budgetwise_cli.infra.db import get_session
from budgetwise_cli.services.budget_service import BudgetService

app = typer.Typer()


@app.command()
def move(src: str, dst: str, amount: Decimal) -> None:
    # Transfer money between envelopes
    if amount <= 0:
        typer.echo("Enter a positive amount to transfer", err=True)
        raise typer.Exit(1)

    try:
        with get_session() as db:
            BudgetService(db).move(src, dst, amount)

        rprint(f"Moved [bold]{amount:.2f}[/] from [red]{src}[/] to [green]{dst}[/]")

    except Exception as e:
        typer.echo(f"Error moving funds: {str(e)}", err=True)
        raise typer.Exit(1)
