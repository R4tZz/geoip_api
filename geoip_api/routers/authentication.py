from datetime import timedelta
from fastapi import APIRouter
from fastapi import Depends, HTTPException, status
from geoip_api.model.user.user_model import (
    CustomOAuth2PasswordRequestForm,
    UserRegister,
)
from geoip_api.model.database.database_model import GeoAPIUsers
from sqlalchemy.orm import Session
from geoip_api.lib import security
from sqlalchemy import or_

from geoip_api.lib.dependecies import get_geoip_db, authenticate_user

router = APIRouter(prefix="/auth", tags=["AUTHENTIFICATION"])


@router.post("/login")
async def login_for_access_token(
    geoip_db: Session = Depends(get_geoip_db),
    form_data: CustomOAuth2PasswordRequestForm = Depends(),
):
    """Method responsible to login into the api and return the JWT Token"""
    user = authenticate_user(
        form_data.username, form_data.password.get_secret_value(), db_engine=geoip_db
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=security.get_access_token_expire_minutes())
    access_token = security.create_access_token(
        data={"sub": user.Username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_new_user(
    user_registration: UserRegister, geoip_db: Session = Depends(get_geoip_db)
):
    """Adds a new user to the api."""
    user_email_exists = geoip_db.query(GeoAPIUsers).filter(
        or_(
            GeoAPIUsers.Username == user_registration.username,
            GeoAPIUsers.Email == user_registration.email,
        )
    )
    if geoip_db.query(user_email_exists.exists()).scalar():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or Email already exist!",
        )
    try:
        user = GeoAPIUsers(
            Username=user_registration.username,
            Email=user_registration.email,
            Password=security.get_password_hash(
                user_registration.password.get_secret_value()
            ),
        )
        geoip_db.add(user)
        geoip_db.commit()
        geoip_db.refresh(user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Something went wrong while creating the new user!",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"Success": "User added to the database!"}
