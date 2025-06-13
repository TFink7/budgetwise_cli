import typer
from .commands import add, move, report, close_month

app = typer.Typer(help="BudgetWise envelope budgeting")

# Register commands directly, but import implementations
app.command(
    help="Add a transaction to an envelope. • Format: add <envelope> <amount> [note]"
)(add.add_transaction)
app.command(
    help="Move money between envelopes. • Format: move <source> <destination> <amount>"
)(move.move_funds)
app.command(help="Generate financial reports. • Format: report [YYYY-MM]")(
    report.generate_report
)
app.command(
    name="close-month",
    help="Close a month and roll balances. • Format: close-month <year> <month>",
)(close_month.close_month)

if __name__ == "__main__":
    app()
