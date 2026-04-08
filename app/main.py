from fastapi import FastAPI, Depends, HTTPException, status
from app.schemas import UserCreate
from app.database import Base, engine, SessionLocal
from app.models import User
from sqlalchemy.orm import Session
from app.utils import hash_password, verify_password


app = FastAPI()


# Create all tables
Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.post("/api/register", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db:Session = Depends(get_db)):
     
    existing_user = db.query(User).filter(User.email == user.email).first() 
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already registerd with this email")
    
    password = hash_password(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"msg": "User registered successfully"}

    
