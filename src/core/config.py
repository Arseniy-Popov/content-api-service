import os
from enum import Enum
from logging import config as logging_config

from pydantic import BaseSettings

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class EnvTypes(str, Enum):
    DEV = "development"
    TEST = "testing"
    PROD = "production"


class Environment(BaseSettings):
    ENVIRONMENT: EnvTypes = EnvTypes.DEV


class Config(BaseSettings):
    class Config:
        env_prefix = ""
        env_file = ".env"

    PROJECT_NAME: str = "movies"

    UVICORN_RELOAD: bool = False

    REDIS_PATH: str = "redis:6379"

    ELASTIC_PATH: str = "elasticsearch:9200"

    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    FILMS_CACHE_EXPIRE = 60 * 5
    GENRES_CACHE_EXPIRE = 60 * 5
    PERSONS_CACHE_EXPIRE = 60 * 5


class DevConfig(Config):
    UVICORN_RELOAD = True


env_2_config = {
    EnvTypes.DEV: DevConfig,
    EnvTypes.PROD: Config,
}


environment = Environment().ENVIRONMENT
config = env_2_config[environment]()
