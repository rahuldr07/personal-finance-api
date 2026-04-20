from datetime import date

from fastapi.testclient import TestClient

from finance_api.database import init_db
from finance_api.main import app


init_db()
client = TestClient(app)


def auth_headers(email: str = "dev@example.com") -> dict[str, str]:
    client.post("/auth/register", json={"email": email, "password": "password123"})
    response = client.post("/auth/login", data={"username": email, "password": "password123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_and_login_user():
    email = "login@example.com"
    response = client.post("/auth/register", json={"email": email, "password": "password123"})
    assert response.status_code in {201, 409}

    login = client.post("/auth/login", data={"username": email, "password": "password123"})
    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"


def test_create_and_list_expense():
    headers = auth_headers("expense-list@example.com")
    payload = {
        "title": "Lunch",
        "amount": 12.5,
        "category": "food",
        "spent_on": str(date.today()),
        "note": "Team lunch",
    }
    created = client.post("/expenses", json=payload, headers=headers)
    assert created.status_code == 201
    assert created.json()["title"] == "Lunch"

    listed = client.get("/expenses", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) >= 1


def test_get_single_expense():
    headers = auth_headers("expense-detail@example.com")
    created = client.post(
        "/expenses",
        json={
            "title": "Coffee",
            "amount": 5.25,
            "category": "food",
            "spent_on": "2026-05-17",
        },
        headers=headers,
    )
    expense_id = created.json()["id"]

    response = client.get(f"/expenses/{expense_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Coffee"


def test_update_and_delete_expense():
    headers = auth_headers("expense-update@example.com")
    created = client.post(
        "/expenses",
        json={
            "title": "Bus",
            "amount": 3.0,
            "category": "travel",
            "spent_on": "2026-05-17",
        },
        headers=headers,
    )
    expense_id = created.json()["id"]

    updated = client.patch(f"/expenses/{expense_id}", json={"amount": 4.0}, headers=headers)
    assert updated.status_code == 200
    assert updated.json()["amount"] == 4.0

    deleted = client.delete(f"/expenses/{expense_id}", headers=headers)
    assert deleted.status_code == 204


def test_monthly_summary():
    headers = auth_headers("summary@example.com")
    client.post(
        "/expenses",
        json={
            "title": "Books",
            "amount": 30,
            "category": "education",
            "spent_on": "2026-05-17",
        },
        headers=headers,
    )
    response = client.get("/reports/monthly?year=2026&month=5", headers=headers)
    assert response.status_code == 200
    assert response.json()["total"] >= 30


def test_yearly_summary():
    headers = auth_headers("yearly@example.com")
    client.post(
        "/expenses",
        json={
            "title": "Course",
            "amount": 99,
            "category": "education",
            "spent_on": "2026-01-20",
        },
        headers=headers,
    )

    response = client.get("/reports/yearly?year=2026", headers=headers)
    assert response.status_code == 200
    assert response.json()["total"] >= 99


def test_csv_export():
    headers = auth_headers("export@example.com")
    client.post(
        "/expenses",
        json={
            "title": "Notebook",
            "amount": 8.5,
            "category": "education",
            "spent_on": "2026-05-17",
        },
        headers=headers,
    )

    response = client.get("/reports/export.csv?year=2026&month=5", headers=headers)
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "Notebook" in response.text


def test_create_and_list_budgets():
    headers = auth_headers("budget@example.com")
    created = client.post(
        "/budgets",
        json={"category": "food", "monthly_limit": 500},
        headers=headers,
    )
    assert created.status_code == 201
    assert created.json()["category"] == "food"

    response = client.get("/budgets", headers=headers)
    assert response.status_code == 200
    assert any(item["category"] == "food" for item in response.json())
