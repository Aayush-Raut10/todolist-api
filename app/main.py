from fastapi import FastAPI
from app.database import Base, engine
from app.routes import auth, dashboard, tasks
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Task Management API")

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(tasks.router)


origins = [

    "https://todolist-frontend-dun.vercel.app",
    
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







