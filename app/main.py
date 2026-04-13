from fastapi import FastAPI
from app.database import Base, engine
from app.routes import auth, dashboard, tasks
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(tasks.router)


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







