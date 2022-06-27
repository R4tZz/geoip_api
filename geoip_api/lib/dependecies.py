from fastapi.routing import Request
from fastapi import Depends, HTTPException, status
from requests import Session
from jose import jwt, JWTError
from geoip_api.lib.security import (
    get_algorithm,
    get_secret_key,
    oauth2_scheme,
    verify_password,
)
from geoip_api.model.user.user_model import TokenData
from geoip_api.model.database.database_model import GeoAPIUsers


def get_geoip_db(request: Request):
    """Gets the database engine"""
    return request.state.db


async def get_current_user(
    geoip_db: Session = Depends(get_geoip_db), token: str = Depends(oauth2_scheme)
):
    """With a given token validates if it is a valid user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, get_secret_key(), algorithms=[get_algorithm()])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username, db_engine=geoip_db)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: GeoAPIUsers = Depends(get_current_user),
):
    """Gets the current active user and validates if the token being used is still valid."""
    if current_user.Disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_user(username: str, db_engine):
    """With a given username return the user from the database"""
    return db_engine.query(GeoAPIUsers).filter(GeoAPIUsers.Username == username).first()


def authenticate_user(username: str, password: str, db_engine: Session):
    """Method responsible to authenticate the user"""
    user = get_user(username, db_engine)
    if not user:
        return False
    if not verify_password(password, user.Password):
        return False
    return user
