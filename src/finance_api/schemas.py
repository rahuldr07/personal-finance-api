from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field

from finance_api.models import ExpenseCategory


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
    spent_on: date
    note: str | None = Field(default=None, max_length=500)


class ExpenseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    amount: float | None = Field(default=None, gt=0)
    category: ExpenseCategory | None = None
    spent_on: date | None = None
    note: str | None = Field(default=None, max_length=500)


class ExpenseRead(BaseModel):
    id: int
    title: str
    amount: float
    category: ExpenseCategory
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
