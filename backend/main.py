from fastapi import FastAPI, Form, Depends, HTTPException
from pydantic import BaseModel
from typing import Annotated
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.models import User
from backend.database import get_db
from backend.security import hash_password, verify_password


class UserDetails(BaseModel):
    model_config = {
        "extra": "forbid"
    }

    username: str
    email: str
    password: str


class UserDetailsResponse(BaseModel):
    id: int 
    username: str
    email: str
    created_at: datetime


class LoginRequest(BaseModel):
    username: str
    password: str


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Calculator Backend Running"}


@app.post("/login")
async def login(
    login_details: LoginRequest,
    db: Session = Depends(get_db)
    ):
    stmt = select(User.password_hash).where(User.username == login_details.username)
    password_hash = db.execute(stmt).scalar_one_or_none()

    if password_hash is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if verify_password(login_details.password, password_hash):
        return {"username": login_details.username}

    raise HTTPException(status_code=401, detail="Unauthorized")


@app.post("/users", response_model=UserDetailsResponse)
async def users(
    user_details: UserDetails,
    db: Session = Depends(get_db)
    ):
    user = User()
    user.username = user_details.username
    user.email = user_details.email  
    user.password_hash = hash_password(user_details.password)
    user.created_at = datetime.now()

    db.add(user)

    try:
        db.commit()
        db.refresh(user)

    except IntegrityError as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=409, detail="Username Already exists")

    return user
