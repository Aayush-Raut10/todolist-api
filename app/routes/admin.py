from fastapi import APIRouter , Depends, HTTPException, status
from app.models import User
from app.core.security import get_current_user


router = APIRouter(prefix="/api/admin", tags=["Admin"])


def role_checker(user:User = Depends(get_current_user)):
        if user.role.lower() != "admin":
           raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        return user
    
    
@router.get("/api/admin")
def admin_page(user:User = Depends(role_checker)):
    return {"message":f"Welcome to the Admin page {user.username}"}

