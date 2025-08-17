from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from modules.auth.schemas import UserSignup, UserLogin, Token, UserResponse
from modules.auth.services import create_user_and_farm, get_password_hash, create_access_token, verify_password
from modules.auth.models import User
from core.dependencies import get_db

router = APIRouter()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup_user(user_data: UserSignup, db: Session = Depends(get_db)):
    """
    Registers a new user and creates an associated farm.
    """
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    new_user = create_user_and_farm(
        db,
        email=user_data.email,
        password=user_data.password,
        farm_name=user_data.farm_name,
        latitude=user_data.latitude,
        longitude=user_data.longitude,
        location_name=user_data.location_name
    )

    return new_user


@router.post("/signin", response_model=Token)
def signin_user(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticates a user and returns a JWT token.
    """
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if not db_user or not verify_password(user_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}