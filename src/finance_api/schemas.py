from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field

from finance_api.models import ExpenseCategory, PaymentMethod, RecurrenceFrequency


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserRead(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ErrorResponse(BaseModel):
    detail: str


class ExpenseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    amount: float = Field(gt=0)
    category: ExpenseCategory = ExpenseCategory.other
    payment_method: PaymentMethod = PaymentMethod.other
    merchant: str | None = Field(default=None, max_length=120)
    spent_on: date
    note: str | None = Field(default=None, max_length=500)


class ExpenseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    amount: float | None = Field(default=None, gt=0)
    category: ExpenseCategory | None = None
    payment_method: PaymentMethod | None = None
    merchant: str | None = Field(default=None, max_length=120)
    spent_on: date | None = None
    note: str | None = Field(default=None, max_length=500)


class ExpenseRead(BaseModel):
    id: int
    title: str
    amount: float
    category: ExpenseCategory
    payment_method: PaymentMethod
    merchant: str | None
    spent_on: date
    note: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CategorySummary(BaseModel):
    category: ExpenseCategory
    total: float


class MonthlySummary(BaseModel):
    year: int
    month: int
    total: float
    categories: list[CategorySummary]


class MonthSummary(BaseModel):
    month: int
    total: float


class YearlySummary(BaseModel):
    year: int
    total: float
    months: list[MonthSummary]


class BudgetCreate(BaseModel):
    category: ExpenseCategory
    monthly_limit: float = Field(gt=0)


class BudgetUpdate(BaseModel):
    category: ExpenseCategory | None = None
    monthly_limit: float | None = Field(default=None, gt=0)


class BudgetRead(BaseModel):
    id: int
    category: ExpenseCategory
    monthly_limit: float
    created_at: datetime

    model_config = {"from_attributes": True}


class BudgetStatus(BaseModel):
    category: ExpenseCategory
    monthly_limit: float
    spent: float
    remaining: float
    over_limit: bool


class RecurringExpenseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    amount: float = Field(gt=0)
    category: ExpenseCategory = ExpenseCategory.other
    frequency: RecurrenceFrequency
    next_due_on: date
    note: str | None = Field(default=None, max_length=500)


class RecurringExpenseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    amount: float | None = Field(default=None, gt=0)
    category: ExpenseCategory | None = None
    frequency: RecurrenceFrequency | None = None
    next_due_on: date | None = None
    note: str | None = Field(default=None, max_length=500)


class RecurringExpenseRead(BaseModel):
    id: int
    title: str
    amount: float
    category: ExpenseCategory
    frequency: RecurrenceFrequency
    next_due_on: date
    note: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TopExpense(BaseModel):
    id: int
    title: str
    amount: float
    category: ExpenseCategory
    spent_on: date


class CategoryShare(BaseModel):
    category: ExpenseCategory
    total: float
    percentage: float


class SpendingInsights(BaseModel):
    expense_count: int
    total_spent: float
    average_expense: float
    largest_expense: float
    highest_category: ExpenseCategory | None


class SavingsGoalCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    target_amount: float = Field(gt=0)
    current_amount: float = Field(default=0, ge=0)
    target_date: date | None = None


class SavingsGoalUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    target_amount: float | None = Field(default=None, gt=0)
    current_amount: float | None = Field(default=None, ge=0)
    target_date: date | None = None


class SavingsGoalRead(BaseModel):
    id: int
    name: str
    target_amount: float
    current_amount: float
    target_date: date | None
    progress_percentage: float
    remaining_amount: float

    model_config = {"from_attributes": True}


class DashboardSummary(BaseModel):
    month_total: float
    expense_count: int
    active_budget_count: int
    savings_goal_count: int
    recurring_expense_count: int
