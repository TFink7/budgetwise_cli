from __future__ import annotations

import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# ---------------------------------------------------------------------------
# Base class for SQLAlchemy models
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Enum for transaction types
# ---------------------------------------------------------------------------


class TransactionType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"
    MOVE = "move"


# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------


class Envelope(Base):
    __tablename__ = "envelopes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    budget: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    created_at: Mapped[date] = mapped_column(Date, default=date.today)

    transactions: Mapped[list["Transaction"]] = relationship(back_populates="envelope")


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    env_id: Mapped[int] = mapped_column(ForeignKey("envelopes.id"))
    type: Mapped[TransactionType] = mapped_column(Enum(TransactionType))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    note: Mapped[str | None] = mapped_column(String(128))
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    envelope: Mapped["Envelope"] = relationship(back_populates="transactions")


class ClosedMonth(Base):
    __tablename__ = "closed_months"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)

    __table_args__ = (UniqueConstraint("year", "month", name="uq_closed_month"),)
