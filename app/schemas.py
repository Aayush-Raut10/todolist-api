from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    username:str
    email:str
    password:str
    confirm_password:str


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