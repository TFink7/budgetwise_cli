import typer
from .commands import add, move, report, close_month

app = typer.Typer(help="BudgetWise envelope budgeting", rich_help_panel="Commands")

app.add_typer(
    add.app,
    name="add",
    help="""Add a transaction to an envelope.

Format: add <envelope> <amount> [note]

Examples:
  add Groceries 50.00 "Weekly shopping"
  add Salary 1500.00 "Monthly income"
""",
)

app.add_typer(
    move.app,
    name="move",
    help="""Move money between envelopes.

Format: move <source> <destination> <amount>

Examples:
  move Salary Groceries 200.00
  move Savings Emergency 500.00
""",
)

app.add_typer(
    report.app,
    name="report",
    help="""Generate financial reports.

Format: report [YYYY-MM]

Examples:
  report         # Current month
  report 2025-06 # June 2025
""",
)

app.add_typer(
    close_month.app,
    name="close-month",
    help="""Close a month and roll over balances.

Format: close-month --month YYYY-MM

Examples:
  close-month                 # Close current month
  close-month --month 2025-06 # Close June 2025
""",
)

if __name__ == "__main__":
    app()
