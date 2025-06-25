import typer
from .commands import add, move, report, close_month

app = typer.Typer(help="BudgetWise envelope budgeting")


app.command(
    name="add",
    help="Add a transaction to an envelope. • Format: add envelope amount note",
)(add.add)

app.command(
    name="move",
    help="Move money between envelopes. • Format: move source destination amount",
)(move.move)

app.command(
    name="report", help="Generate financial reports. • Format: report year-month"
)(report.report)

app.command(
    name="close-month",
    help="Close a month and roll balances. • Format: close-month --month year-month",
)(close_month.cmd_close_month)

if __name__ == "__main__":
    app()
