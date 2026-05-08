from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from finance_api import models, schemas, services
from finance_api.database import get_db
from finance_api.dependencies import get_current_user

router = APIRouter(
    prefix="/expenses",
    tags=["expenses"],
    responses={401: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse}},
)


@router.get("/meta/categories", response_model=list[str])
def list_categories():
    return [category.value for category in models.ExpenseCategory]


@router.get("/meta/payment-methods", response_model=list[str])
def list_payment_methods():
    return [method.value for method in models.PaymentMethod]


@router.post("", response_model=schemas.ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(
    payload: schemas.ExpenseCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[models.User, Depends(get_current_user)],
):
    return services.create_expense(db, user, payload)


@router.get("", response_model=list[schemas.ExpenseRead])
def list_expenses(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[models.User, Depends(get_current_user)],
    category: models.ExpenseCategory | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    min_amount: float | None = Query(default=None, ge=0),
    max_amount: float | None = Query(default=None, ge=0),
    search: str | None = Query(default=None, min_length=1, max_length=80),
    payment_method: models.PaymentMethod | None = None,
    merchant: str | None = Query(default=None, min_length=1, max_length=120),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
):
    return services.list_expenses(
        db,
        user,
        category,
        start_date,
        end_date,
        min_amount,
        max_amount,
        search,
        payment_method,
        merchant,
        skip,
        limit,
    )


@router.get("/{expense_id}", response_model=schemas.ExpenseRead)
def get_expense(
    expense_id: int,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[models.User, Depends(get_current_user)],
):
    expense = services.get_expense(db, user, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.patch("/{expense_id}", response_model=schemas.ExpenseRead)
def update_expense(
    expense_id: int,
    payload: schemas.ExpenseUpdate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[models.User, Depends(get_current_user)],
):
    expense = services.get_expense(db, user, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return services.update_expense(db, expense, payload)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[models.User, Depends(get_current_user)],
):
    expense = services.get_expense(db, user, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    services.delete_expense(db, expense)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
