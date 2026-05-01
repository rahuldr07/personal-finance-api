from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from finance_api import models, schemas, services
from finance_api.database import get_db
from finance_api.dependencies import get_current_user

router = APIRouter(
    prefix="/recurring-expenses",
    tags=["recurring expenses"],
    responses={401: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse}},
)


@router.post("", response_model=schemas.RecurringExpenseRead, status_code=status.HTTP_201_CREATED)
def create_recurring_expense(
    payload: schemas.RecurringExpenseCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[models.User, Depends(get_current_user)],
):
    return services.create_recurring_expense(db, user, payload)


@router.get("", response_model=list[schemas.RecurringExpenseRead])
def list_recurring_expenses(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[models.User, Depends(get_current_user)],
):
    return services.list_recurring_expenses(db, user)


@router.get("/{recurring_id}", response_model=schemas.RecurringExpenseRead)
def get_recurring_expense(
    recurring_id: int,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[models.User, Depends(get_current_user)],
):
    recurring = services.get_recurring_expense(db, user, recurring_id)
    if recurring is None:
        raise HTTPException(status_code=404, detail="Recurring expense not found")
    return recurring


@router.patch("/{recurring_id}", response_model=schemas.RecurringExpenseRead)
def update_recurring_expense(
    recurring_id: int,
    payload: schemas.RecurringExpenseUpdate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[models.User, Depends(get_current_user)],
):
    recurring = services.get_recurring_expense(db, user, recurring_id)
    if recurring is None:
        raise HTTPException(status_code=404, detail="Recurring expense not found")
    return services.update_recurring_expense(db, recurring, payload)


@router.delete("/{recurring_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recurring_expense(
    recurring_id: int,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[models.User, Depends(get_current_user)],
):
    recurring = services.get_recurring_expense(db, user, recurring_id)
    if recurring is None:
        raise HTTPException(status_code=404, detail="Recurring expense not found")
    services.delete_recurring_expense(db, recurring)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
