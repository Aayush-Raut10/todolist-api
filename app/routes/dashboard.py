from fastapi import APIRouter , Depends, HTTPException, status
from app.database import SessionLocal
from app.models import User, Task
from sqlalchemy.orm import Session
from app.core.security import get_current_user


router = APIRouter(prefix="/api", tags=["Dashbaord"])


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/dashboard")
def dashboard(user:User = Depends(get_current_user), db:Session = Depends(get_db)):
        
        # Fetch user tasks
        tasks = db.query(Task).filter(Task.user_id == user.id).all()

        # prepare statistics
        total_tasks = len(tasks)
        completed_task = sum(1 for task in tasks if task.is_completed)
        pending_tasks = total_tasks - completed_task

        
        return {
            "user":{
                "id":user.id,
                "username":user.username,
                "email":user.email,
                "role":user.role
            }, 

            "tasks":[
                
                {

                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "is_completed": t.is_completed,
                    "created_at": t.created_at,
                    "updated_at": t.updated_at

            }   for t in tasks
            ],
        
            "stats":{
                "total_tasks":total_tasks,
                "completed_tasks":completed_task,
                "pending_tasks":pending_tasks
            }
        }