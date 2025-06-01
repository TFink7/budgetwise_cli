import typer
from .commands import add, move, report, close_month

app = typer.Typer(help="BudgetWise envelope budgeting")
app.add_typer(add.app, name="add")
app.add_typer(move.app, name="move")
app.add_typer(report.app, name="report")
app.add_typer(close_month.app, name="close-month")

if __name__ == "__main__":
    app()
