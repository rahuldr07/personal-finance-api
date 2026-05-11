from datetime import date

from fastapi.testclient import TestClient

from finance_api.database import Base, engine, init_db
from finance_api.main import app


Base.metadata.drop_all(bind=engine)
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
    assert response.json()["status"] == "ok"
    assert response.json()["version"] == "0.1.0"


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


def test_list_expense_categories():
    response = client.get("/expenses/meta/categories")
    assert response.status_code == 200
    assert "food" in response.json()


def test_filter_expenses_by_amount_range():
    headers = auth_headers("expense-filter@example.com")
    client.post(
        "/expenses",
        json={
            "title": "Large purchase",
            "amount": 250,
            "category": "shopping",
            "spent_on": "2026-05-17",
        },
        headers=headers,
    )

    response = client.get("/expenses?min_amount=200&max_amount=300", headers=headers)
    assert response.status_code == 200
    assert any(item["title"] == "Large purchase" for item in response.json())


def test_search_expenses_by_text():
    headers = auth_headers("expense-search@example.com")
    client.post(
        "/expenses",
        json={
            "title": "Gym membership",
            "amount": 45,
            "category": "health",
            "spent_on": "2026-05-17",
            "note": "monthly fitness plan",
        },
        headers=headers,
    )

    response = client.get("/expenses?search=fitness", headers=headers)
    assert response.status_code == 200
    assert any(item["title"] == "Gym membership" for item in response.json())


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


def test_top_expenses_report():
    headers = auth_headers("top-expenses@example.com")
    client.post(
        "/expenses",
        json={
            "title": "Laptop stand",
            "amount": 65,
            "category": "shopping",
            "spent_on": "2026-05-17",
        },
        headers=headers,
    )

    response = client.get("/reports/top-expenses?limit=1", headers=headers)
    assert response.status_code == 200
    assert response.json()[0]["title"] == "Laptop stand"


def test_category_share_report():
    headers = auth_headers("category-share@example.com")
    client.post(
        "/expenses",
        json={
            "title": "Groceries",
            "amount": 75,
            "category": "food",
            "spent_on": "2026-05-17",
        },
        headers=headers,
    )

    response = client.get("/reports/category-shares?year=2026&month=5", headers=headers)
    assert response.status_code == 200
    assert response.json()[0]["percentage"] == 100


def test_spending_insights_report():
    headers = auth_headers("insights@example.com")
    client.post(
        "/expenses",
        json={
            "title": "Shoes",
            "amount": 120,
            "category": "shopping",
            "spent_on": "2026-05-17",
        },
        headers=headers,
    )

    response = client.get("/reports/insights?year=2026&month=5", headers=headers)
    assert response.status_code == 200
    assert response.json()["expense_count"] == 1
    assert response.json()["largest_expense"] == 120


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


def test_update_budget():
    headers = auth_headers("budget-update@example.com")
    created = client.post(
        "/budgets",
        json={"category": "travel", "monthly_limit": 200},
        headers=headers,
    )
    budget_id = created.json()["id"]

    response = client.patch(f"/budgets/{budget_id}", json={"monthly_limit": 250}, headers=headers)
    assert response.status_code == 200
    assert response.json()["monthly_limit"] == 250


def test_delete_budget():
    headers = auth_headers("budget-delete@example.com")
    created = client.post(
        "/budgets",
        json={"category": "bills", "monthly_limit": 1000},
        headers=headers,
    )
    budget_id = created.json()["id"]

    deleted = client.delete(f"/budgets/{budget_id}", headers=headers)
    assert deleted.status_code == 204

    missing = client.get(f"/budgets/{budget_id}", headers=headers)
    assert missing.status_code == 404


def test_budget_status_marks_remaining_amount():
    headers = auth_headers("budget-status@example.com")
    client.post("/budgets", json={"category": "food", "monthly_limit": 100}, headers=headers)
    client.post(
        "/expenses",
        json={
            "title": "Dinner",
            "amount": 40,
            "category": "food",
            "spent_on": "2026-05-17",
        },
        headers=headers,
    )

    response = client.get("/budgets/status/monthly?year=2026&month=5", headers=headers)
    assert response.status_code == 200
    assert response.json()[0]["remaining"] == 60


def test_create_and_list_recurring_expenses():
    headers = auth_headers("recurring-list@example.com")
    created = client.post(
        "/recurring-expenses",
        json={
            "title": "Internet bill",
            "amount": 49.99,
            "category": "bills",
            "frequency": "monthly",
            "next_due_on": "2026-06-01",
        },
        headers=headers,
    )
    assert created.status_code == 201
    assert created.json()["frequency"] == "monthly"

    response = client.get("/recurring-expenses", headers=headers)
    assert response.status_code == 200
    assert any(item["title"] == "Internet bill" for item in response.json())


def test_update_and_delete_recurring_expense():
    headers = auth_headers("recurring-update@example.com")
    created = client.post(
        "/recurring-expenses",
        json={
            "title": "Streaming",
            "amount": 9.99,
            "category": "other",
            "frequency": "monthly",
            "next_due_on": "2026-06-10",
        },
        headers=headers,
    )
    recurring_id = created.json()["id"]

    updated = client.patch(
        f"/recurring-expenses/{recurring_id}",
        json={"amount": 12.99},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["amount"] == 12.99

    deleted = client.delete(f"/recurring-expenses/{recurring_id}", headers=headers)
    assert deleted.status_code == 204


def test_create_and_list_savings_goals():
    headers = auth_headers("savings-list@example.com")
    created = client.post(
        "/savings-goals",
        json={"name": "Emergency fund", "target_amount": 1000, "current_amount": 250},
        headers=headers,
    )
    assert created.status_code == 201
    assert created.json()["progress_percentage"] == 25

    response = client.get("/savings-goals", headers=headers)
    assert response.status_code == 200
    assert any(item["name"] == "Emergency fund" for item in response.json())
