import os
import sys
from pathlib import Path

SQLITE_PREFIX = "sqlite:///" if sys.platform.startswith("win") else "sqlite:////"
BASE_DIR = Path(__file__).resolve().parent.parent


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = SQLITE_PREFIX + str(BASE_DIR / "data.db")


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = SQLITE_PREFIX + str(BASE_DIR / "test.db")


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = SQLITE_PREFIX + str(BASE_DIR / "data.db")


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
