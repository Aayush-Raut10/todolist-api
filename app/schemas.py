from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    username:str
    email:EmailStr
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

    class Config:
        from_attributes = True



class SingleTaskResponse(BaseModel):
    status:bool 
    message:str
    data:TaskResponse
    

class TaskListResponse(BaseModel):
    success:bool
    data:List[TaskResponse]


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TaskUpdateRequest(BaseModel):
    title:Optional[str] = None
    description:Optional[str] = None
    is_completed:Optional[bool] = None

