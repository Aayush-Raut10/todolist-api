from fastapi import FastAPI, Depends, HTTPException, status
from app.schemas import UserCreate, UserLogin, TaskCreate, TaskUpdateRequest, SingleTaskResponse
from app.database import Base, engine, SessionLocal
from app.models import User, Task
from sqlalchemy.orm import Session
from app.utils import hash_password, verify_password
from app.auth import create_access_token, verify_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()



origins = [

    "http://127.0.0.1:5500",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Create all tables
Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

security = HTTPBearer()

@app.post("/api/register", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db:Session = Depends(get_db)):
     
    existing_user = db.query(User).filter(User.email == user.email).first() 
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already registered with this email")
    
    password = hash_password(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"msg": "User registered successfully"}


@app.post("/api/login")
def user_login(user: UserLogin, db:Session = Depends(get_db)):
    
    # check if user exists
    is_user_exists = db.query(User).filter(User.email == user.email).first()
    if not is_user_exists:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    if not verify_password(user.password, is_user_exists.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    # create JWT token
    token_data = {
        "user_id":is_user_exists.id, 
        "username":is_user_exists.username, 
        "email":is_user_exists.email,
        "role":is_user_exists.role

        }
    access_token = create_access_token(token_data)
    
    return {"access_token":access_token, "token_type":"Bearer"}



def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db:Session = Depends(get_db)):
    
    token = credentials.credentials
    
    payload = verify_access_token(jwt_token=token)

    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    current_user = db.query(User).filter(User.id == user_id).first()
   

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return current_user


def role_checker(user:User = Depends(get_current_user)):
        if user.role.lower() != "admin":
           raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        return user
    
    
@app.get("/api/admin")
def admin_page(user:User = Depends(role_checker)):
    return {"message":f"Welcome to the Admin page {user.username}"}




@app.post("/api/tasks")
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



@app.get("/api/dashboard")
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

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int, user:User = Depends(get_current_user), db:Session = Depends(get_db)):
    
    db_task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()

    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not Found")
    
    db.delete(db_task)
    db.commit()

    return {"status":"success", "message":"Task deleted successfully"}


@app.patch("/api/tasks/{task_id}", response_model=SingleTaskResponse)
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