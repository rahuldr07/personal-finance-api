from calendar import monthrange
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from finance_api import exporting, models, schemas, services
from finance_api.database import get_db
from finance_api.dependencies import get_current_user

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    responses={401: {"model": schemas.ErrorResponse}},
)


@router.get("/monthly", response_model=schemas.MonthlySummary)
def get_monthly_summary(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[models.User, Depends(get_current_user)],
    year: int = Query(ge=2000, le=2100),
    month: int = Query(ge=1, le=12),
):
    return services.monthly_summary(db, user, year, month)


@router.get("/yearly", response_model=schemas.YearlySummary)
def get_yearly_summary(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[models.User, Depends(get_current_user)],
    year: int = Query(ge=2000, le=2100),
):
    return services.yearly_summary(db, user, year)


@router.get("/export.csv", response_class=Response)
def export_expenses_csv(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[models.User, Depends(get_current_user)],
    year: int | None = Query(default=None, ge=2000, le=2100),
    month: int | None = Query(default=None, ge=1, le=12),
):
    start_date = None
    end_date = None
    if year and month:
        start_date = date(year, month, 1)
        end_date = date(year, month, monthrange(year, month)[1])
    expenses = services.list_expenses(db, user, start_date=start_date, end_date=end_date, limit=200)
    return Response(
        content=exporting.expenses_to_csv(expenses),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=expenses.csv"},
    )
