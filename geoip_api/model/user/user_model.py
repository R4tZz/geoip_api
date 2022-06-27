from typing import Optional
from geoip_api.model.geoip_model_base import InternalBaseModel
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.param_functions import Form
from pydantic import SecretStr, validator


class Token(InternalBaseModel):
    access_token: str
    token_type: str


class TokenData(InternalBaseModel):
    username: str | None = None


class CustomOAuth2PasswordRequestForm(OAuth2PasswordRequestForm):
    def __init__(
        self,
        grant_type: str = Form(default=None, regex="password"),
        username: str = Form(),
        password: SecretStr = Form(),
        scope: str = Form(default=""),
        client_id: Optional[str] = Form(default=None),
        client_secret: Optional[str] = Form(default=None),
    ):
        super().__init__(
            grant_type=grant_type,
            username=username,
            password=password,
            scope=scope,
            client_id=client_id,
            client_secret=client_secret,
        )


class UserRegister(InternalBaseModel):
    username: str
    email: str
    password: SecretStr
    confirm_password: SecretStr

    @validator("username")
    def username_alphanumeric(cls, v):
        assert v.isalnum(), "User name must contain alphanumeric characters only!"
        return v

    @validator("username")
    def pass_rules(cls, v):
        if len(v) < 3:
            raise ValueError("Username must contain at least 3 characters!")
        elif len(v) > 10:
            raise ValueError("Username must not contain more than 10 characters!")
        return v

    @validator("confirm_password")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match!")
        return v
