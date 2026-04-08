from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    username:str
    email:str
    password:str
    confirm_password:str

    # validator to check if password match
    @field_validator("confirm_password")
    def passwords_match(cls, v, values):
        if "password" in values.data and v != values.data["password"]:
            raise ValueError("Passwords do not match")
        return v



class TaskCreate(BaseModel):
    title:str
    description:Optional[str] = None
    is_completed:Optional[bool] = False
    

class TaskResponse(BaseModel):
    id:int
    title:str
    description:Optional[str]
    is_completed:bool
    created_at: datetime
    updated_at:datetime



class SingleTaskResponse(BaseModel):
    success:bool
    data:TaskResponse

class TaskListResponse(BaseModel):
    success:bool
    data:List[TaskResponse]