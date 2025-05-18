from calendar import monthrange
from datetime import timedelta, date, datetime, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from budgetwise_cli.domain import models as m


class BudgetService:
    # Budgeting operations related to envelopes and transactions

    def __init__(self, db: Session) -> None:
        self.db = db

    def add_transaction(
        self,
        envelope_name: str,
        amount: Decimal,
        note: str = "",
        ts: datetime | None = None,
    ) -> m.Transaction:
        # Create Envelope if it doesn't exist and Insert a new transaction
        env = self._get_or_create_envelope(envelope_name)
        tx_type = m.TransactionType.INCOME if amount > 0 else m.TransactionType.EXPENSE
        tx = m.Transaction(
            type=tx_type,
            amount=amount,
            note=note,
            ts=ts or datetime.now(timezone.utc),
            envelope=env,
        )
        self.db.add(tx)
        self.db.flush()
        return tx

    def move(self, src: str, dst: str, amount: Decimal) -> None:
        # Transfer money between envelopes if budget changes are needed
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self.add_transaction(src, -amount, f"transfer to {dst}")
        self.add_transaction(dst, amount, f"transfer from {src}")

    # Date reporting and monthly management
    def report(self, start: date, end: date) -> dict[str, Decimal]:
        stmt = (
            select(m.Envelope.name, func.sum(m.Transaction.amount))
            .join(m.Transaction)
            .where(m.Transaction.ts.between(start, end))
            .group_by(m.Envelope.name)
            .order_by(m.Envelope.name)
        )
        return {
            name: balance or Decimal("0") for name, balance in self.db.execute(stmt)
        }

    def close_month(self, year: int, month: int) -> None:
        # Roll envelopes over to next month
        first = date(year, month, 1)
        last = date(year, month, monthrange(year, month=1)[1])
        balances = self.report(first, last)

        for env, bal in balances.items():
            if bal == 0:
                continue
            self.add_transaction(env, -bal, "rollover to next month")
            next_month = (last.replace(day=1) + timedelta(days=32)).replace(day=1)
            self.add_transaction(
                env,
                bal,
                "opening balance",
                ts=datetime.combine(next_month, datetime.min.time()),
            )

    # Helper for adding transactions
    def _get_or_create_envelope(self, name: str) -> m.Envelope:
        env = self.db.scalar(select(m.Envelope).where(m.Envelope.name == name).limit(1))
        if not env:
            env = m.Envelope(name=name, budget=Decimal("0"))
            self.db.add(env)
            self.db.flush()
        return env
