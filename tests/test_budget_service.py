import pytest
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session

from budgetwise_cli.domain import models as m
from budgetwise_cli.services.budget_service import BudgetService


# test adding an expense to an envelope
def test_add_expense(budget_service: BudgetService, db: Session) -> None:
    tx = budget_service.add_transaction("Groceries", Decimal("-20.00"), "Grocery Store")
    db.commit()

    assert tx.amount == Decimal("-20.00")
    assert tx.note == "Grocery Store"
    assert tx.type == m.TransactionType.EXPENSE
    assert tx.envelope.name == "Groceries"


# test adding an income to an envelope
def test_add_income(budget_service: BudgetService, db: Session) -> None:
    tx = budget_service.add_transaction("Salary", Decimal("1000.00"), "Monthly Salary")
    db.commit()

    assert tx.amount == Decimal("1000.00")
    assert tx.note == "Monthly Salary"
    assert tx.type == m.TransactionType.INCOME
    assert tx.envelope.name == "Salary"


# test moving funds between envelopes
def test_move_between_envelopes(budget_service: BudgetService, db: Session) -> None:
    budget_service.move("Groceries", "Salary", Decimal("20.00"))
    db.commit()

    groceries_tx = (
        db.query(m.Transaction)
        .filter(
            m.Transaction.envelope.has(m.Envelope.name == "Groceries"),
            m.Transaction.type == m.TransactionType.EXPENSE,
        )
        .one()
    )

    salary_tx = (
        db.query(m.Transaction)
        .filter(
            m.Transaction.envelope.has(m.Envelope.name == "Salary"),
            m.Transaction.type == m.TransactionType.INCOME,
        )
        .one()
    )

    assert groceries_tx.amount == Decimal("-20.00")
    assert salary_tx.amount == Decimal("20.00")
    assert groceries_tx.note is not None and "transfer to Salary" in groceries_tx.note
    assert salary_tx.note is not None and "transfer from Groceries" in salary_tx.note


# test moving negative amount
def test_move_negative_amount(budget_service: BudgetService) -> None:
    with pytest.raises(ValueError, match="Amount must be positive"):
        budget_service.move("Groceries", "Salary", Decimal("-10.00"))


# test empty report
def test_empty_report(budget_service: BudgetService, db: Session) -> None:
    today = date.today()
    report = budget_service.report(today, today)
    assert len(report) == 0


# Test that providing an invalid date range raises an error.


def test_invalid_date_report(budget_service: BudgetService) -> None:

    with pytest.raises(ValueError):
        budget_service.report(date(2024, 3, 15), date(2024, 3, 1))


# test report with transactions


def test_report_with_transactions(budget_service: BudgetService, db: Session) -> None:
    start_date = date(2024, 2, 1)
    end_date = date(2024, 2, 29)

    # Add some transactions in date range
    ts1 = datetime(2024, 2, 5, tzinfo=timezone.utc)
    budget_service.add_transaction(
        "Groceries", Decimal("-50.00"), "Weekly Groceries", ts=ts1
    )
    budget_service.add_transaction(
        "Salary", Decimal("2000.00"), "February Salary", ts=ts1
    )

    # Add some transactions outside date range
    ts2 = datetime(2024, 3, 1, tzinfo=timezone.utc)
    budget_service.add_transaction(
        "Groceries", Decimal("-30.00"), "March Groceries", ts=ts2
    )
    budget_service.add_transaction("Salary", Decimal("1500.00"), "March Salary", ts=ts2)

    db.commit()

    report = budget_service.report(start_date, end_date)
    assert len(report) == 2
    assert report["Groceries"] == Decimal("-50.00")
    assert report["Salary"] == Decimal("2000.00")


# test closing a month with transactions
def test_close_month(budget_service: BudgetService, db: Session) -> None:
    # set up initial transactions for March
    march_date = datetime(2024, 3, 1, tzinfo=timezone.utc)
    budget_service.add_transaction(
        "Groceries", Decimal("-150.00"), "March Groceries", ts=march_date
    )
    budget_service.add_transaction(
        "Leisure", Decimal("-100.00"), "March Leisure", ts=march_date
    )
    budget_service.add_transaction(
        "Salary", Decimal("3000.00"), "March Salary", ts=march_date
    )
    db.commit()

    budget_service.close_month(2024, 3)
    db.commit()

    # verify balances rolled over
    april_start = date(2024, 4, 1)
    april_end = date(2024, 4, 30)
    april_report = budget_service.report(april_start, april_end)

    assert april_report["Groceries"] == Decimal("-150.00")
    assert april_report["Leisure"] == Decimal("-100.00")
    assert april_report["Salary"] == Decimal("3000.00")


# Test closing a month that's already been closed.
def test_closing_already_closed_month(
    budget_service: BudgetService, db: Session
) -> None:

    # First close
    budget_service.close_month(2024, 5)
    db.commit()

    # Second close should fail
    with pytest.raises(ValueError):
        budget_service.close_month(2024, 5)


# test getting or creating an envelope
def test_get_existing_envelope(budget_service: BudgetService, db: Session) -> None:
    # Create envelope first
    db.add(m.Envelope(name="Test", budget=Decimal("100")))
    db.commit()

    # Should retrieve existing envelope
    env = budget_service._get_or_create_envelope("Test")
    assert env.name == "Test"
    assert env.budget == Decimal("100")


def test_create_new_envelope(budget_service: BudgetService, db: Session) -> None:
    # Create a new envelope
    env = budget_service._get_or_create_envelope("New Category")
    db.commit()

    assert env.name == "New Category"
    assert env.budget == Decimal("0")
