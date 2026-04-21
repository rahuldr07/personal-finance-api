from datetime import date

from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from finance_api import models, schemas
from finance_api.security import hash_password, verify_password


def create_user(db: Session, payload: schemas.UserCreate) -> models.User:
    user = models.User(email=payload.email.lower(), hashed_password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> models.User | None:
    user = db.scalar(select(models.User).where(models.User.email == email.lower()))
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user


def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.scalar(select(models.User).where(models.User.email == email.lower()))


def create_expense(
    db: Session,
    owner: models.User,
    payload: schemas.ExpenseCreate,
) -> models.Expense:
    expense = models.Expense(owner_id=owner.id, **payload.model_dump())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def list_expenses(
    db: Session,
    owner: models.User,
    category: models.ExpenseCategory | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    min_amount: float | None = None,
    max_amount: float | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[models.Expense]:
    query = select(models.Expense).where(models.Expense.owner_id == owner.id)
    if category:
        query = query.where(models.Expense.category == category)
    if start_date:
        query = query.where(models.Expense.spent_on >= start_date)
    if end_date:
        query = query.where(models.Expense.spent_on <= end_date)
    if min_amount is not None:
        query = query.where(models.Expense.amount >= min_amount)
    if max_amount is not None:
        query = query.where(models.Expense.amount <= max_amount)
    query = query.order_by(models.Expense.spent_on.desc(), models.Expense.id.desc()).offset(skip).limit(limit)
    return list(db.scalars(query))


def get_expense(db: Session, owner: models.User, expense_id: int) -> models.Expense | None:
    return db.scalar(
        select(models.Expense).where(
            models.Expense.id == expense_id,
            models.Expense.owner_id == owner.id,
        )
    )


def update_expense(
    db: Session,
    expense: models.Expense,
    payload: schemas.ExpenseUpdate,
) -> models.Expense:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(expense, field, value)
    db.commit()
    db.refresh(expense)
    return expense


def delete_expense(db: Session, expense: models.Expense) -> None:
    db.delete(expense)
    db.commit()


def monthly_summary(db: Session, owner: models.User, year: int, month: int) -> schemas.MonthlySummary:
    rows = db.execute(
        select(models.Expense.category, func.sum(models.Expense.amount))
        .where(
            models.Expense.owner_id == owner.id,
            extract("year", models.Expense.spent_on) == year,
            extract("month", models.Expense.spent_on) == month,
        )
        .group_by(models.Expense.category)
    ).all()
    categories = [
        schemas.CategorySummary(category=category, total=round(float(total or 0), 2))
        for category, total in rows
    ]
    return schemas.MonthlySummary(
        year=year,
        month=month,
        total=round(sum(item.total for item in categories), 2),
        categories=categories,
    )


def yearly_summary(db: Session, owner: models.User, year: int) -> schemas.YearlySummary:
    rows = db.execute(
        select(extract("month", models.Expense.spent_on), func.sum(models.Expense.amount))
        .where(
            models.Expense.owner_id == owner.id,
            extract("year", models.Expense.spent_on) == year,
        )
        .group_by(extract("month", models.Expense.spent_on))
        .order_by(extract("month", models.Expense.spent_on))
    ).all()
    months = [
        schemas.MonthSummary(month=int(month), total=round(float(total or 0), 2))
        for month, total in rows
    ]
    return schemas.YearlySummary(
        year=year,
        total=round(sum(item.total for item in months), 2),
        months=months,
    )


def create_budget(db: Session, owner: models.User, payload: schemas.BudgetCreate) -> models.Budget:
    budget = models.Budget(owner_id=owner.id, **payload.model_dump())
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


def list_budgets(db: Session, owner: models.User) -> list[models.Budget]:
    query = select(models.Budget).where(models.Budget.owner_id == owner.id).order_by(models.Budget.category)
    return list(db.scalars(query))
