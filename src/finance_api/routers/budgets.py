from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from finance_api import models, schemas, services
from finance_api.database import get_db
from finance_api.dependencies import get_current_user

router = APIRouter(
    prefix="/budgets",
    tags=["budgets"],
    responses={401: {"model": schemas.ErrorResponse}},
)


@router.post("", response_model=schemas.BudgetRead, status_code=status.HTTP_201_CREATED)
def create_budget(
    payload: schemas.BudgetCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[models.User, Depends(get_current_user)],
):
    return services.create_budget(db, user, payload)


@router.get("", response_model=list[schemas.BudgetRead])
def list_budgets(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[models.User, Depends(get_current_user)],
):
    return services.list_budgets(db, user)

