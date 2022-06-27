import os
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt


SECURITY_FOLDER_PATH = os.path.dirname(os.path.realpath(__file__))
SECURITY_CONF = "geoip_api.conf"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_algorithm():
    """Get algorithm variable."""
    try:
        algorithm = os.getenv("ALGORITHM")
    except:
        raise KeyError(
            "Environment variable is invalid! Please define the algorithm variable."
        )
    return algorithm


def get_secret_key():
    """Get secret key variable."""
    try:
        secret_key = os.getenv("SECRET_KEY")
    except:
        raise KeyError("Secret variable is not configured!")
    return secret_key


def get_access_token_expire_minutes():
    """Get access token expire minutes variable."""
    try:
        token_expiration_value = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    except:
        raise KeyError(
            "Environment variable is invalid! Please define the access token expire minutes variable."
        )
    return token_expiration_value


def verify_password(plain_password, hashed_password):
    """Verifies a given password with bcrypt"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Gets the hash password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Creates the access jwt token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, get_secret_key(), algorithm=get_algorithm())
    return encoded_jwt
