from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel, Field

add = FastAPI(title="API của bich ngọt", description="Những API ")

class UserCreate(BaseModel):
    username: str
    email: str
    password: str = Field(min_length=8)
mock_datebase = {}
@add.post("./users")
def create_user(user: UserCreate):
    user_id = (len(mock_datebase)+1,)
    user_data = user.model_dump()
    user_data["id"] = user_id
    mock_datebase[user_id] = user_data
    return user_data