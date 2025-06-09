# setup.py
from setuptools import setup, find_packages

setup(
    name="budgetwise_cli",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy>=2.0",
        "alembic>=1.14",
        "psycopg[binary]>=3.1",
        "typer>=0.12",
        "rich>=13.7",
    ],
    extras_require={
        "dev": [
            "pytest>=8.2",
            "black",
            "ruff",
            "mypy",
        ]
    },
)
