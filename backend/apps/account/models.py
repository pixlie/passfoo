from enum import Enum as PyEnum
from sqlalchemy import Column, String, DateTime, Enum, text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import INET

from base.models import SystemModel, BaseModel


class AuthType(PyEnum):
    EMAIL = 1
    PHONE = 2
    TWITTER = 3
    FACEBOOK = 4


class User(SystemModel):
    """
    This model is used to store the user information of those who will use
    the system. A user is uniquely registered once and can be part of
    multiple tenants.
    """

    __tablename__ = "user"

    username = Column(String(30), unique=True, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=text("(now() at time zone 'utc')"))
    created_from = Column(INET, nullable=False)


class UserAuth(BaseModel):
    """
    This model is used to store the authentication mechanism for any user.
    The default authentication mechanism is user email/code based.
    The meta may not be required in all authentication mechanisms, but the
    token is required by any authentication provider.
    """

    __tablename__ = "user_auth"

    auth_type = Column(Enum(AuthType), nullable=False, default=AuthType.EMAIL)
    token = Column(String(250), nullable=False)
    meta = Column(String(250), nullable=True)
