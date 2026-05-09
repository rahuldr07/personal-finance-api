from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from finance_api import models, schemas, services
from finance_api.database import get_db
from finance_api.dependencies import get_current_user

router = APIRouter(
    prefix="/savings-goals",
    tags=["savings goals"],
    responses={401: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse}},
)


@router.post("", response_model=schemas.SavingsGoalRead, status_code=status.HTTP_201_CREATED)
def create_savings_goal(
    payload: schemas.SavingsGoalCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[models.User, Depends(get_current_user)],
):
    return services.create_savings_goal(db, user, payload)


@router.get("", response_model=list[schemas.SavingsGoalRead])
def list_savings_goals(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[models.User, Depends(get_current_user)],
):
    return services.list_savings_goals(db, user)


@router.get("/{goal_id}", response_model=schemas.SavingsGoalRead)
def get_savings_goal(
    goal_id: int,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[models.User, Depends(get_current_user)],
):
    goal = services.get_savings_goal(db, user, goal_id)
    if goal is None:
        raise HTTPException(status_code=404, detail="Savings goal not found")
    return services.serialize_savings_goal(goal)


@router.patch("/{goal_id}", response_model=schemas.SavingsGoalRead)
def update_savings_goal(
    goal_id: int,
    payload: schemas.SavingsGoalUpdate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[models.User, Depends(get_current_user)],
):
    goal = services.get_savings_goal(db, user, goal_id)
    if goal is None:
        raise HTTPException(status_code=404, detail="Savings goal not found")
    return services.update_savings_goal(db, goal, payload)


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_savings_goal(
    goal_id: int,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[models.User, Depends(get_current_user)],
):
    goal = services.get_savings_goal(db, user, goal_id)
    if goal is None:
        raise HTTPException(status_code=404, detail="Savings goal not found")
    services.delete_savings_goal(db, goal)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
