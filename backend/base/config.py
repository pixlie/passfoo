import os
from decouple import config

from base.singleton import Singleton


class Settings(metaclass=Singleton):
    _instance = None

    # Statement for enabling development environment.
    # Keep DEBUG = False for production environment
    DEBUG = config("DEBUG", cast=bool, default=True)

    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    # Datebase configurations
    DATABASES = {
        "default": config("DB_DEFAULT", cast=str),
        "test": config("DB_TEST", cast=str, default="postgresql+psycopg2://postgres@localhost/passfoo"),
    }

    # Settings for running the server on localhost with port number
    DAEMON = {
        "host": config("DAEMON_HOST", cast=str, default="127.0.0.1"),
        "port": config("DAEMON_PORT", cast=int, default=4000)
    }

    SERVER_PROTOCOL = config("SERVER_PROTOCOL", cast=str, default="https://")
    SERVER_DOMAIN = config("SERVER_DOMAIN", cast=str, default="")

    MANDRILL_API_KEY = config("MANDRILL_API_KEY", cast=str, default="")
    DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", cast=str, default="")
    DEFAULT_FROM_NAME = config("DEFAULT_FROM_NAME", cast=str, default="")
    DEFAULT_SUBJECT_PREFIX = config("DEFAULT_SUBJECT_PREFIX", cast=str, default="")

    SECRET_KEY = config("SECRET_KEY", cast=str)

    APPS = (
        'account',
        'password'
    )


settings = Settings()
