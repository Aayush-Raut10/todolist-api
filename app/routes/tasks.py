from fastapi import APIRouter , Depends, HTTPException, status
from app.schemas import TaskCreate, TaskUpdateRequest, SingleTaskResponse
from app.database import SessionLocal
from app.models import User, Task
from sqlalchemy.orm import Session
from app.core.security import get_current_user

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_task(task: TaskCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):

    new_task = Task(
        title=task.title, 
        description=task.description,
        user_id = user.id,
        is_completed = task.is_completed
        )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task



@router.delete("/{task_id}")
def delete_task(task_id: int, user:User = Depends(get_current_user), db:Session = Depends(get_db)):
    
    db_task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()

    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not Found")
    
    db.delete(db_task)
    db.commit()

    return {"status":"success", "message":"Task deleted successfully"}


@router.patch("/{task_id}", response_model=SingleTaskResponse)
def update_task(task_id:int, task:TaskUpdateRequest, user:User = Depends(get_current_user), db:Session = Depends(get_db)):

    db_task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()

    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found!")
    
    if task.title is not None:
        db_task.title = task.title
    
    if task.description is not None:
        db_task.description = task.description
    
    if task.is_completed is not None:
        db_task.is_completed = task.is_completed

    db.commit()
    db.refresh(db_task)


    return {
        "status":True, 
        "message":"Task updated successfully",
        "data":db_task
        }