import typer
from datetime import date
from typing import cast
from budgetwise_cli.infra.db import get_session
from budgetwise_cli.services.budget_service import BudgetService
from rich import print as rprint

app = typer.Typer()


def _validate_year_month(
    ctx: typer.Context, param: typer.CallbackParam, value: str
) -> tuple[int, int]:
    try:
        y, m = map(int, value.split("-"))

        # Validate month range
        if not (1 <= m <= 12):
            raise ValueError(f"Month must be between 01 and 12, got {m:02d}")
        # Validate year range
        if not (1000 <= y <= 9999):
            raise ValueError(f"Enter a valid 4 digit year, got {y}")
        return (y, m)

    except ValueError as e:
        if str(e).startswith("Month must be") or str(e).startswith("Enter a valid"):
            raise typer.BadParameter(str(e)) from None
        else:
            raise typer.BadParameter("Input in format YYYY-MM") from None


@app.command()
def close_month(
    year_month: str = typer.Option(
        date.today().strftime("%Y-%m"),
        "--month",
        "-m",
        help="Month to close in YYYY-MM format",
        callback=_validate_year_month,
    )
) -> None:
    """Close a month and roll over balances.

    Format: close-month --month YYYY-MM

    Examples:
      close-month                 # Close current month
      close-month --month 2025-06 # Close June 2025
      close-month -m 2025-05      # Close May 2025 (short option)
    """
    year_month_tuple = cast(tuple[int, int], year_month)
    year_num, month_num = year_month_tuple
    try:
        with get_session() as db:
            BudgetService(db).close_month(year_num, month_num)
        rprint(f"Closed month [bold]{year_num}-{month_num:02d}[/bold] successfully")
    except Exception as e:
        typer.echo(f"Error closing month: {str(e)}", err=True)
        raise typer.Exit(1)
