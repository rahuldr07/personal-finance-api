from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from finance_api import models, schemas, services
from finance_api.database import get_db
from finance_api.dependencies import get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/monthly", response_model=schemas.MonthlySummary)
def get_monthly_summary(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[models.User, Depends(get_current_user)],
    year: int = Query(ge=2000, le=2100),
    month: int = Query(ge=1, le=12),
):
    return services.monthly_summary(db, user, year, month)

