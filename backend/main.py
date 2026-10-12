from typing import Annotated
from datetime import datetime, timedelta
import secrets

from fastapi import FastAPI, Depends, HTTPException, Response, Cookie
from pydantic import BaseModel
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from backend.database.models import User, UserSession
from backend.database.database import get_db
from backend.security import hash_password, verify_password
from backend.dependencies import get_current_user


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
    response: Response,
    db: Session = Depends(get_db),
    ):
    stmt = select(User).where(User.username == login_details.username)
    user = db.execute(stmt).scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not verify_password(login_details.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Unauthorized")

    session_id = secrets.token_urlsafe(32)

    user_session = UserSession()
    user_session.session_id = session_id
    user_session.user_id = user.id
    user_session.created_at = user.created_at
    user_session.expires_at = datetime.now() + timedelta(days=7)

    db.add(user_session)
    try:
        db.commit()

        response.set_cookie(
                            key="session_id", 
                            value=session_id, 
                            httponly=True, 
                            samesite="lax", 
                            max_age=604800,
                            secure=False    # For local development secure=False, in production secure=True
                            )
    
    except IntegrityError as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=500, detail="Could not create session")

    return {
        "username": login_details.username,
        "session_created": True
        }


@app.post("/logout")
async def logout(
    response: Response,
    session_id: Annotated[str | None, Cookie()] = None,
    db: Session = Depends(get_db)
):

    if session_id is None:
        return {"message": "Successfully logged out"}
    
    stmt = delete(UserSession).where(UserSession.session_id == session_id)
    result = db.execute(stmt)

    try:
        db.commit()
        response.delete_cookie(
            key="session_id",
            httponly=True,
            samesite="lax",
            secure=False    # For local development secure=False, in production secure=True
            )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Please try again later")

    return {"message": "Successfully logged out"}


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


@app.get("/me")
async def me(
    current_user: User = Depends(get_current_user)
    ):
    
    return {
        "username" : current_user.username,
        "message" : "Session is valid"
    }


@app.get("/protected")      # Temporary Endpoint
async def protected(
    current_user: User = Depends(get_current_user)
):
    return {
        "message": "You have access",
        "user_id": current_user.id,
        "username": current_user.username
    }