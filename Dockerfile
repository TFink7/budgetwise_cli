FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY budgetwise_cli /app/budgetwise_cli

ENTRYPOINT ["python", "-m", "budgetwise_cli.cli.app"]