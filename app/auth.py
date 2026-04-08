import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from jose import jwt, JWTError

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))  # default 15 if not set

def create_access_token(data:dict):
    
    to_encode = data.copy()
    expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"expires":expires})

    encoded_jwt = jwt.encode(to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(jwt_token:str):
    """
    Verifies a JWT token and returns payload if valid
    """

    try:
      payload = jwt.decode(token=jwt_token, key=SECRET_KEY, algorithms=[ALGORITHM])
      print(payload)
      print(type(payload))
      return payload

    except JWTError:
       return None
    
    