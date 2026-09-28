from fastapi import FastAPI, Form
from pydantic import BaseModel
from enum import Enum
from fastapi.responses import RedirectResponse
from typing import Annotated

class UserDetails(BaseModel):
    model_config = {
        "extra": "forbid"
    }

    username: str
    email: str
    password: str

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Calculator Backend Running"}


@app.post("/login")
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return {"username": username}


@app.post("/users")
async def users(user_details: UserDetails):
    return user_details
