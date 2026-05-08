from calendar import monthrange
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
    search: str | None = None,
    payment_method: models.PaymentMethod | None = None,
    merchant: str | None = None,
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
    if search:
        pattern = f"%{search.strip()}%"
        query = query.where(
            models.Expense.title.ilike(pattern) | models.Expense.note.ilike(pattern)
        )
    if payment_method:
        query = query.where(models.Expense.payment_method == payment_method)
    if merchant:
        query = query.where(models.Expense.merchant.ilike(f"%{merchant.strip()}%"))
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


def get_budget(db: Session, owner: models.User, budget_id: int) -> models.Budget | None:
    return db.scalar(
        select(models.Budget).where(
            models.Budget.id == budget_id,
            models.Budget.owner_id == owner.id,
        )
    )


def update_budget(
    db: Session,
    budget: models.Budget,
    payload: schemas.BudgetUpdate,
) -> models.Budget:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(budget, field, value)
    db.commit()
    db.refresh(budget)
    return budget


def delete_budget(db: Session, budget: models.Budget) -> None:
    db.delete(budget)
    db.commit()


def budget_status(
    db: Session,
    owner: models.User,
    year: int,
    month: int,
) -> list[schemas.BudgetStatus]:
    budgets = list_budgets(db, owner)
    statuses: list[schemas.BudgetStatus] = []
    for budget in budgets:
        spent = db.scalar(
            select(func.sum(models.Expense.amount)).where(
                models.Expense.owner_id == owner.id,
                models.Expense.category == budget.category,
                extract("year", models.Expense.spent_on) == year,
                extract("month", models.Expense.spent_on) == month,
            )
        )
        spent_total = round(float(spent or 0), 2)
        remaining = round(budget.monthly_limit - spent_total, 2)
        statuses.append(
            schemas.BudgetStatus(
                category=budget.category,
                monthly_limit=budget.monthly_limit,
                spent=spent_total,
                remaining=remaining,
                over_limit=remaining < 0,
            )
        )
    return statuses


def create_recurring_expense(
    db: Session,
    owner: models.User,
    payload: schemas.RecurringExpenseCreate,
) -> models.RecurringExpense:
    recurring = models.RecurringExpense(owner_id=owner.id, **payload.model_dump())
    db.add(recurring)
    db.commit()
    db.refresh(recurring)
    return recurring


def list_recurring_expenses(db: Session, owner: models.User) -> list[models.RecurringExpense]:
    query = (
        select(models.RecurringExpense)
        .where(models.RecurringExpense.owner_id == owner.id)
        .order_by(models.RecurringExpense.next_due_on.asc(), models.RecurringExpense.id.asc())
    )
    return list(db.scalars(query))


def get_recurring_expense(
    db: Session,
    owner: models.User,
    recurring_id: int,
) -> models.RecurringExpense | None:
    return db.scalar(
        select(models.RecurringExpense).where(
            models.RecurringExpense.id == recurring_id,
            models.RecurringExpense.owner_id == owner.id,
        )
    )


def update_recurring_expense(
    db: Session,
    recurring: models.RecurringExpense,
    payload: schemas.RecurringExpenseUpdate,
) -> models.RecurringExpense:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(recurring, field, value)
    db.commit()
    db.refresh(recurring)
    return recurring


def delete_recurring_expense(db: Session, recurring: models.RecurringExpense) -> None:
    db.delete(recurring)
    db.commit()


def top_expenses(db: Session, owner: models.User, limit: int = 5) -> list[schemas.TopExpense]:
    query = (
        select(models.Expense)
        .where(models.Expense.owner_id == owner.id)
        .order_by(models.Expense.amount.desc(), models.Expense.spent_on.desc())
        .limit(limit)
    )
    return [
        schemas.TopExpense(
            id=expense.id,
            title=expense.title,
            amount=expense.amount,
            category=expense.category,
            spent_on=expense.spent_on,
        )
        for expense in db.scalars(query)
    ]


def category_shares(db: Session, owner: models.User, year: int, month: int) -> list[schemas.CategoryShare]:
    summary = monthly_summary(db, owner, year, month)
    if summary.total == 0:
        return []
    return [
        schemas.CategoryShare(
            category=item.category,
            total=item.total,
            percentage=round((item.total / summary.total) * 100, 2),
        )
        for item in summary.categories
    ]


def spending_insights(db: Session, owner: models.User, year: int, month: int) -> schemas.SpendingInsights:
    expenses = list_expenses(
        db,
        owner,
        start_date=date(year, month, 1),
        end_date=date(year, month, monthrange(year, month)[1]),
        limit=500,
    )
    total = round(sum(expense.amount for expense in expenses), 2)
    average = round(total / len(expenses), 2) if expenses else 0
    largest = round(max((expense.amount for expense in expenses), default=0), 2)
    shares = category_shares(db, owner, year, month)
    highest = max(shares, key=lambda item: item.total).category if shares else None
    return schemas.SpendingInsights(
        expense_count=len(expenses),
        total_spent=total,
        average_expense=average,
        largest_expense=largest,
        highest_category=highest,
    )


def serialize_savings_goal(goal: models.SavingsGoal) -> schemas.SavingsGoalRead:
    progress = round((goal.current_amount / goal.target_amount) * 100, 2)
    return schemas.SavingsGoalRead(
        id=goal.id,
        name=goal.name,
        target_amount=goal.target_amount,
        current_amount=goal.current_amount,
        target_date=goal.target_date,
        progress_percentage=progress,
        remaining_amount=round(max(goal.target_amount - goal.current_amount, 0), 2),
    )
