from pydantic import BaseSettings


class Config(BaseSettings):
    class Config:
        env_prefix = ""
        env_file = ".env"

    APP_PATH: str = "http://localhost:80"
    REDIS_PATH: str = "redis://localhost:6379/0"
    ELASTIC_PATH: str = "http://localhost:9200"

    ELASIC_INDEX_NAME_MOVIES: str = "movies"
    ELASIC_INDEX_NAME_PERSONS: str = "persons"
    ELASIC_INDEX_NAME_GENRES: str = "genres"


config = Config()
