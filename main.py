# main.py
from fastapi import FastAPI
from core.middleware import setup_middleware
from core.dependencies import engine
from models.base import Base
from modules.soil.routes import router as soil_router

app = FastAPI(title="Agri-Tech Backend", version="1.0.0")

# Setup middleware```
setup_middleware(app)
app.include_router(soil_router, prefix="/api/soil")
# Create database tables on startup
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Agri-Tech Backend!"}
