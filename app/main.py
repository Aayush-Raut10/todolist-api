from fastapi import FastAPI, Depends, HTTPException, status
from app.schemas import UserCreate, UserLogin
from app.database import Base, engine, SessionLocal
from app.models import User
from sqlalchemy.orm import Session
from app.utils import hash_password, verify_password
from app.auth import create_access_token, verify_access_token


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


@app.post("/api/login")
def user_login(user: UserLogin, db:Session = Depends(get_db)):
    
    # check if user exists
    is_user_exists = db.query(User).filter(User.email == user.email).first()
    if not is_user_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")
    
    if not verify_password(user.password, is_user_exists.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")
    
    # create JWT token
    token_data = {"user_id":is_user_exists.id, "username":is_user_exists.username, "email":is_user_exists.email}
    access_token = create_access_token(token_data)
    
    return {"access_token":access_token, "token_type":"Bearer"}
