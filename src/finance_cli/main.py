from pathlib import Path

import httpx
import typer

app = typer.Typer(help="CLI client for the Personal Finance API.")
STATE_FILE = Path.home() / ".finance-cli-token"
API_URL = "http://127.0.0.1:8000"


def auth_headers() -> dict[str, str]:
    if not STATE_FILE.exists():
        raise typer.BadParameter("Run `finance-cli login` first.")
    return {"Authorization": f"Bearer {STATE_FILE.read_text().strip()}"}


@app.command()
def login(email: str, password: str) -> None:
    response = httpx.post(
        f"{API_URL}/auth/login",
        data={"username": email, "password": password},
        timeout=10,
    )
    response.raise_for_status()
    STATE_FILE.write_text(response.json()["access_token"])
    typer.echo("Logged in")


@app.command("add")
def add_expense(title: str, amount: float, category: str, spent_on: str, note: str = "") -> None:
    response = httpx.post(
        f"{API_URL}/expenses",
        headers=auth_headers(),
        json={
            "title": title,
            "amount": amount,
            "category": category,
            "spent_on": spent_on,
            "note": note or None,
        },
        timeout=10,
    )
    response.raise_for_status()
    typer.echo(f"Created expense #{response.json()['id']}")


@app.command("list")
def list_expenses() -> None:
    response = httpx.get(f"{API_URL}/expenses", headers=auth_headers(), timeout=10)
    response.raise_for_status()
    for item in response.json():
        typer.echo(f"{item['id']}: {item['spent_on']} {item['category']} {item['amount']} - {item['title']}")


@app.command()
def summary(year: int, month: int) -> None:
    response = httpx.get(
        f"{API_URL}/reports/monthly",
        headers=auth_headers(),
        params={"year": year, "month": month},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    typer.echo(f"Total: {data['total']}")
    for row in data["categories"]:
        typer.echo(f"{row['category']}: {row['total']}")

