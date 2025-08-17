# main.py
from fastapi import FastAPI
from core.middleware import setup_middleware
from core.dependencies import engine
from models.base import Base
from modules.soil.routes import router as soil_router
from modules.crop.routes import router as crop_router
from modules.nutrient.routes import router as nutrient_router
from modules.nitrate.routes import router as nitrate_router
from modules.irrigation.routes import router as irrigation_router
from modules.auth.routes import router as auth_router

app = FastAPI(title="Agri-Tech Backend", version="1.0.0")

# Setup middleware```
setup_middleware(app)
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"]) # New router
app.include_router(soil_router, prefix="/api/soil")
app.include_router(crop_router, prefix="/api/crop")
app.include_router(nutrient_router, prefix="/api/nutrient")
app.include_router(nitrate_router, prefix="/api/nitrate")
app.include_router(irrigation_router, prefix="/api/irrigation")
# Create database tables on startup
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Agri-Tech Backend!"}
