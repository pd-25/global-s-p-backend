from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
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
        "https://global-s-p.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],       # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],       # Allow all headers
)
    include_router(app)
    # Mount static files so /jute_images/*, /uploads/*, etc. are served
    app.mount("/", StaticFiles(directory="app/static"), name="static")
    # create_tables()
    return app

app = start_application()

@app.get("/")
def hello():
    return {"msg": "Welcome to WirePy and gretings from Pradipta Bhuin, the FastAPI boilerplate for building APIs with Python."}