from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from app.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime

# user model model/user.py
class User(Base):
    
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")

    # One user can have many tasks : one to many relationship
    # tasks is a list of Task objects that belong to this user.
    tasks = relationship("Task", back_populates="owner") # back_populates="owner" will link to the owner field in Task.



# Task model model/task.py
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String, nullable=True)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign key linking to user
    user_id = Column(Integer, ForeignKey("users.id")) #user_id → stores the ID of the user this task belongs to.

    # Relationship
    owner = relationship("User", back_populates="tasks") # owner → lets you access task.owner.username, task.owner.email, etc.




class PasswordReset(Base):
    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True, index=True)
    token_hash = Column(String, unique=True, index=True)
    expires_at = Column(DateTime, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)