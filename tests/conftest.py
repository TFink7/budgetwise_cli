import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from typing import Generator

from budgetwise_cli.domain.models import Base
from budgetwise_cli.services.budget_service import BudgetService


@pytest.fixture
def db() -> Generator[Session, None, None]:
    # Create in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
        session.rollback()


@pytest.fixture
def budget_service(db: Session) -> BudgetService:
    # Provide a BudgetService instance for tests
    return BudgetService(db)
