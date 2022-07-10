import multiprocessing
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


class ProdConfig(BaseSettings):
    class Config:
        env_prefix = ""
        env_file = ".env"

    ENVIRONMENT: EnvTypes = EnvTypes.DEV

    PROJECT_NAME: str = "movies"

    GUNICORN_RELOAD: bool = False
    GUNICORN_WORKERS: int = multiprocessing.cpu_count() * 2 + 1

    REDIS_PATH: str = "redis://redis:6379/0"
    ELASTIC_PATH: str = "http://elasticsearch:9200"

    FILMS_CACHE_EXPIRE: int = 60 * 5
    GENRES_CACHE_EXPIRE: int = 60 * 5
    PERSONS_CACHE_EXPIRE: int = 60 * 5


class DevConfig(ProdConfig):
    REDIS_PATH: str = "redis://127.0.0.1:6379/0"
    ELASTIC_PATH: str = "http://127.0.0.1:9200"

    GUNICORN_RELOAD = True
    GUNICORN_WORKERS = 1


class TestConfig(ProdConfig):
    GUNICORN_RELOAD = True
    GUNICORN_WORKERS = 1


env_2_config = {
    EnvTypes.DEV: DevConfig,
    EnvTypes.PROD: ProdConfig,
    EnvTypes.TEST: TestConfig,
}

environment = Environment().ENVIRONMENT
config = env_2_config[environment]()
