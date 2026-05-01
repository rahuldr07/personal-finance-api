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

