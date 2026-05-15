from datetime import date

from finance_api import schemas, services
from finance_api.database import SessionLocal, init_db


def main() -> None:
    init_db()
    with SessionLocal() as db:
        user = services.get_user_by_email(db, "demo@example.com")
        if user is None:
            user = services.create_user(
                db,
                schemas.UserCreate(email="demo@example.com", password="password123"),
            )
        services.create_expense(
            db,
            user,
            schemas.ExpenseCreate(
                title="Demo lunch",
                amount=14.5,
                category="food",
                payment_method="debit_card",
                merchant="Demo Cafe",
                spent_on=date.today(),
                note="Seeded example",
            ),
        )
    print("Seeded demo user and expense")


if __name__ == "__main__":
    main()
