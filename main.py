from fastapi import FastAPI
from app.core.config import settings
# from db.session import engine
# from db.base import Base
from app.routes.base import api_router
from fastapi.middleware.cors import CORSMiddleware

def include_router(app):
    app.include_router(api_router)
    
    
def start_application():
    app = FastAPI(title=settings.PROJECT_TITLE, version=settings.PROJECT_VERSION)
    app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
    ],
    allow_credentials=True,
    allow_methods=["*"],       # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],       # Allow all headers
)
    include_router(app)
    # create_tables()
    return app

app = start_application()

@app.get("/")
def hello():
    return {"msg": "Welcome to WirePy and gretings from Pradipta Bhuin, the FastAPI boilerplate for building APIs with Python."}