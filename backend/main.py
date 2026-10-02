from fastapi import FastAPI, Form, Depends, HTTPException
from pydantic import BaseModel
from typing import Annotated
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.models import User
from backend.database import get_db


class UserDetails(BaseModel):
    model_config = {
        "extra": "forbid"
    }

    username: str
    email: str
    password: str


class UserDetailsResponse(BaseModel):
    id : int 
    username: str
    email: str
    created_at: datetime


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Calculator Backend Running"}


@app.post("/login")
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return {"username": username}


@app.post("/users", response_model=UserDetailsResponse)
async def users(
    user_details: UserDetails,
    db: Session = Depends(get_db)
    ):
    user = User()
    user.username = user_details.username
    user.email = user_details.email  
    user.password_hash = user_details.password #for now, will be changed later
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
