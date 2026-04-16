from passlib.context import CryptContext
from secrets import token_urlsafe

# Create a password context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash a password
def hash_password(password: str):
    return pwd_context.hash(password)

# Verify a password
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)



# create a secret token for password reset
def create_reset_token():
    
    t = token_urlsafe(64)
    
    return t


    