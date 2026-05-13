from pathlib import Path
from typing import Annotated
import os

import httpx
import typer

app = typer.Typer(help="CLI client for the Personal Finance API.")
STATE_FILE = Path.home() / ".finance-cli-token"
DEFAULT_API_URL = "http://127.0.0.1:8000"


def api_url() -> str:
    return os.getenv("FINANCE_API_URL", DEFAULT_API_URL).rstrip("/")


def auth_headers() -> dict[str, str]:
    if not STATE_FILE.exists():
        raise typer.BadParameter("Run `finance-cli login` first.")
    return {"Authorization": f"Bearer {STATE_FILE.read_text().strip()}"}


@app.command()
def register(email: str, password: str) -> None:
    response = httpx.post(
        f"{api_url()}/auth/register",
        json={"email": email, "password": password},
        timeout=10,
    )
    response.raise_for_status()
    typer.echo(f"Registered {response.json()['email']}")


@app.command()
def login(email: str, password: str) -> None:
    response = httpx.post(
        f"{api_url()}/auth/login",
        data={"username": email, "password": password},
        timeout=10,
    )
    response.raise_for_status()
    STATE_FILE.write_text(response.json()["access_token"])
    typer.echo("Logged in")


@app.command("add")
def add_expense(
    title: str,
    amount: float,
    category: str,
    spent_on: str,
    note: str = "",
    payment_method: str = "other",
    merchant: str = "",
) -> None:
    response = httpx.post(
        f"{api_url()}/expenses",
        headers=auth_headers(),
        json={
            "title": title,
            "amount": amount,
            "category": category,
            "spent_on": spent_on,
            "note": note or None,
            "payment_method": payment_method,
            "merchant": merchant or None,
        },
        timeout=10,
    )
    response.raise_for_status()
    typer.echo(f"Created expense #{response.json()['id']}")


@app.command("list")
def list_expenses(category: str | None = None, search: str | None = None) -> None:
    params = {"category": category, "search": search}
    response = httpx.get(
        f"{api_url()}/expenses",
        headers=auth_headers(),
        params={key: value for key, value in params.items() if value},
        timeout=10,
    )
    response.raise_for_status()
    for item in response.json():
        typer.echo(f"{item['id']}: {item['spent_on']} {item['category']} {item['amount']} - {item['title']}")


@app.command()
def summary(year: int, month: int) -> None:
    response = httpx.get(
        f"{api_url()}/reports/monthly",
        headers=auth_headers(),
        params={"year": year, "month": month},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    typer.echo(f"Total: {data['total']}")
    for row in data["categories"]:
        typer.echo(f"{row['category']}: {row['total']}")


@app.command("export")
def export_csv(output: Annotated[Path, typer.Option("--output", "-o")] = Path("expenses.csv")) -> None:
    response = httpx.get(f"{api_url()}/reports/export.csv", headers=auth_headers(), timeout=10)
    response.raise_for_status()
    output.write_text(response.text)
    typer.echo(f"Wrote {output}")


@app.command("budget-add")
def add_budget(category: str, monthly_limit: float) -> None:
    response = httpx.post(
        f"{api_url()}/budgets",
        headers=auth_headers(),
        json={"category": category, "monthly_limit": monthly_limit},
        timeout=10,
    )
    response.raise_for_status()
    typer.echo(f"Created budget #{response.json()['id']}")


@app.command("budget-list")
def list_budgets() -> None:
    response = httpx.get(f"{api_url()}/budgets", headers=auth_headers(), timeout=10)
    response.raise_for_status()
    for item in response.json():
        typer.echo(f"{item['id']}: {item['category']} limit {item['monthly_limit']}")


@app.command("budget-status")
def budget_status(year: int, month: int) -> None:
    response = httpx.get(
        f"{api_url()}/budgets/status/monthly",
        headers=auth_headers(),
        params={"year": year, "month": month},
        timeout=10,
    )
    response.raise_for_status()
    for item in response.json():
        typer.echo(
            f"{item['category']}: spent {item['spent']} / {item['monthly_limit']}, "
            f"remaining {item['remaining']}"
        )


@app.command("recurring-add")
def add_recurring(title: str, amount: float, category: str, frequency: str, next_due_on: str) -> None:
    response = httpx.post(
        f"{api_url()}/recurring-expenses",
        headers=auth_headers(),
        json={
            "title": title,
            "amount": amount,
            "category": category,
            "frequency": frequency,
            "next_due_on": next_due_on,
        },
        timeout=10,
    )
    response.raise_for_status()
    typer.echo(f"Created recurring expense #{response.json()['id']}")


@app.command("recurring-list")
def list_recurring() -> None:
    response = httpx.get(f"{api_url()}/recurring-expenses", headers=auth_headers(), timeout=10)
    response.raise_for_status()
    for item in response.json():
        typer.echo(
            f"{item['id']}: {item['next_due_on']} {item['frequency']} "
            f"{item['category']} {item['amount']} - {item['title']}"
        )


@app.command("insights")
def insights(year: int, month: int) -> None:
    response = httpx.get(
        f"{api_url()}/reports/insights",
        headers=auth_headers(),
        params={"year": year, "month": month},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    typer.echo(f"Total spent: {data['total_spent']}")
    typer.echo(f"Average expense: {data['average_expense']}")
    typer.echo(f"Largest expense: {data['largest_expense']}")


@app.command("dashboard")
def dashboard(year: int, month: int) -> None:
    response = httpx.get(
        f"{api_url()}/reports/dashboard",
        headers=auth_headers(),
        params={"year": year, "month": month},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    typer.echo(f"Monthly total: {data['month_total']}")
    typer.echo(f"Expenses: {data['expense_count']}")
    typer.echo(f"Budgets: {data['active_budget_count']}")
    typer.echo(f"Savings goals: {data['savings_goal_count']}")


@app.command("goal-add")
def add_goal(name: str, target_amount: float, current_amount: float = 0) -> None:
    response = httpx.post(
        f"{api_url()}/savings-goals",
        headers=auth_headers(),
        json={
            "name": name,
            "target_amount": target_amount,
            "current_amount": current_amount,
        },
        timeout=10,
    )
    response.raise_for_status()
    typer.echo(f"Created savings goal #{response.json()['id']}")


@app.command("goal-list")
def list_goals() -> None:
    response = httpx.get(f"{api_url()}/savings-goals", headers=auth_headers(), timeout=10)
    response.raise_for_status()
    for item in response.json():
        typer.echo(
            f"{item['id']}: {item['name']} {item['current_amount']}/"
            f"{item['target_amount']} ({item['progress_percentage']}%)"
        )
