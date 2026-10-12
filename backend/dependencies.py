from typing import Annotated
from datetime import datetime

from fastapi import Depends, HTTPException, Cookie
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import UserSession


def get_current_user(
        session_id: Annotated[str | None, Cookie()] = None,
        db: Session = Depends(get_db)
):
    if session_id is None:
            raise HTTPException(status_code=401, detail="Unauthorized")
    
    stmt = select(UserSession).where(
        UserSession.session_id == session_id, 
        UserSession.expires_at > datetime.now())
    
    session = db.execute(stmt).scalar_one_or_none()
    
    if session is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
        
        
    return session.user
