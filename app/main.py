from fastapi import FastAPI, Depends, HTTPException, status
from app.schemas import UserCreate, UserLogin
from app.database import Base, engine, SessionLocal
from app.models import User
from sqlalchemy.orm import Session
from app.utils import hash_password, verify_password
from app.auth import create_access_token, verify_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


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

security = HTTPBearer()

@app.post("/api/register", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db:Session = Depends(get_db)):
     
    existing_user = db.query(User).filter(User.email == user.email).first() 
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already registered with this email")
    
    password = hash_password(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=password, role=user.role)

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
        if user.role  not in ["admin", "ADMIN", "Admin"]:
           raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        return user
    
    



@app.get("/api/admin")
def admin_page(user:User = Depends(role_checker)):
    return {"message":f"Welcome to the Admin page {user.username}"}


@app.get("/api/dashboard")
def dashboard(user:User = Depends(get_current_user)):
 
        return {"message": f"Hi {user.username}, Welcome to the Todo List Web app!"}