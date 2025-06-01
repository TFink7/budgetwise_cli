import typer
from datetime import date, datetime
from rich.table import Table
from rich.console import Console

from budgetwise_cli.infra.db import get_session
from budgetwise_cli.services.budget_service import BudgetService

app = typer.Typer()
console = Console()


def parse_date(val: str) -> date:
    try:
        return datetime.strptime(val, "%Y-%m-%d").date()
    except ValueError:
        raise typer.BadParameter("Date must be in YYYY-MM-DD format") from None


@app.command()
def month(
    month: str = typer.Argument(
        date.today().strftime("%Y-%m"), help="Month to report (YYYY-MM)"
    )
) -> None:
    # Generate a report of envelope balances for a specific month
    year_num, month_num = map(int, month.split("-"))
    first = date(year_num, month_num, 1)
    last = date(year_num, month_num, 1).replace(day=28) + date.resolution * 4

    try:
        with get_session() as db:
            data = BudgetService(db).report(first, last)
    except Exception as e:
        typer.echo(f"Error generating report: {str(e)}", err=True)
        raise typer.Exit(1)

    table = Table(title=f"Budget report {month}")
    table.add_column("Envelope", style="bold")
    table.add_column("Balance", justify="right", style="green")
    for env, balance in data.items():
        table.add_row(env, f"{balance:.2f}")
    console.print(table)
