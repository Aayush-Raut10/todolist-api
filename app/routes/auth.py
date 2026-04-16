from fastapi import APIRouter , Depends, HTTPException, status, BackgroundTasks
from app.schemas import UserCreate, UserLogin, PwdResetRequest
from app.database import SessionLocal
from app.models import User, PasswordReset
from app.core.mail import send_email
import hashlib
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.utils import hash_password, verify_password, create_reset_token
from app.core.security import create_access_token, verify_access_token


router = APIRouter(prefix="/api", tags=["Auth"])


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.post("/register", status_code=status.HTTP_201_CREATED)
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


@router.post("/login")
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



@router.post("/auth/forgotpassword")
async def forgot_password(request:dict, background_tasks:BackgroundTasks, db:Session = Depends(get_db)):
    email = request.get("email")
    
    db_user = db.query(User).filter(User.email == email).first()

    if db_user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is not registered!")
    
    raw_token = create_reset_token()
    hashed_token = hashlib.sha256(raw_token.encode()).hexdigest()
    expires = datetime.utcnow() + timedelta(minutes=5)
  
    new_reset = PasswordReset(token_hash=hashed_token, expires_at=expires, user_id = db_user.id)

    db.add(new_reset)
    db.commit()
    
    # Send this via email in real app
    reset_url = f"http://127.0.0.1:5500/?token={raw_token}"
    
    html_content = f'<h1>Password Reset <h1> <p>click for reset <a href="{reset_url}">Reset Password</a></p>'

    background_tasks.add_task(
        send_email, 
        request.get("email"), 
        "Password Reset",
        body=html_content

        )


    return {"message":"Password reset link has been sent to your email"    }


@router.post("/auth/resetpassword", status_code=status.HTTP_201_CREATED)
async def reset_password(pwdresetrequest:PwdResetRequest, db:Session = Depends(get_db)):

    raw_token = pwdresetrequest.token
    new_password = pwdresetrequest.new_password
    hashed_token = hashlib.sha256(raw_token.encode()).hexdigest()
    
    db_token = db.query(PasswordReset).filter(PasswordReset.token_hash == hashed_token).first()

    if db_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="1Invalid or expired token!")

    if datetime.utcnow() > db_token.expires_at:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="2Invalid or expired token!")
    
    user_of_token = db.query(User).filter(User.id == db_token.user_id).first()
    
    if user_of_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="3Invalid or expired token")
    
    user_of_token.hashed_password = hash_password(new_password)

    db.delete(db_token)
    db.commit()

    return {"status":"success", "message":"Password successfully reset"}