import typer
from decimal import Decimal
from rich import print as rprint
from budgetwise_cli.services.budget_service import BudgetService
from budgetwise_cli.infra.db import get_session

app = typer.Typer()


@app.command()
def add(env: str, amount: Decimal, note: str = "") -> None:
    # Add income or expense into an envelope
    try:
        with get_session() as db:
            tx = BudgetService(db).add_transaction(env, amount, note)
        rprint(
            f"Added transaction: [bold]{tx.type.value}[/bold] of [bold]{tx.amount}[/bold] to envelope [bold]{tx.envelope.name}[/bold]"
        )
    except Exception as e:
        typer.echo(f"error adding transaction: {str(e)}", err=True)
        raise typer.Exit(1)
