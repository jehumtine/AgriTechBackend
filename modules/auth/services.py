# app/modules/auth/services.py
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
import jwt

from core.config import settings
from modules.auth.models import User
from modules.farm.models import Farm

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Creates a new JWT token using PyJWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password, hashed_password):
    """Checks if a plain-text password matches a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Hashes a plain-text password."""
    return pwd_context.hash(password)


def create_user_and_farm(db, email: str, password: str, farm_name: str, latitude: float, longitude: float, location_name: str):
    """Creates a new user and an associated farm."""
    hashed_password = get_password_hash(password)
    db_user = User(email=email, hashed_password=hashed_password)
    db.add(db_user)
    db.flush()

    db_farm = Farm(
        name=farm_name,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        owner_id=db_user.id
    )
    db.add(db_farm)
    db.commit()
    db.refresh(db_user)
    return db_user