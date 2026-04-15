from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from finance_api import schemas, services
from finance_api.database import get_db
from finance_api.security import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse}},
)


@router.post("/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def register_user(payload: schemas.UserCreate, db: Annotated[Session, Depends(get_db)]):
    try:
        return services.create_user(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email is already registered") from exc


@router.post("/login", response_model=schemas.Token)
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
):
    user = services.authenticate_user(db, form.username, form.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return schemas.Token(access_token=create_access_token(user.email))
