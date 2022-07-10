import logging

import aioredis
import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import films, genres, persons
from core.config import config
from core.logger import LOGGING
from db import cache, elastic

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url="/api/docs/swagger",
    redoc_url="/api/docs/redoc",
    openapi_url="/api/docs/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    cache.redis_client = aioredis.from_url(
        f"{config.REDIS_PATH}", encoding="utf-8", decode_responses=True
    )
    elastic.elastic_client = AsyncElasticsearch(hosts=[config.ELASTIC_PATH])


@app.on_event("shutdown")
async def shutdown():
    await cache.redis_client.close()
    await elastic.elastic_client.close()


app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=config.GUNICORN_RELOAD,
    )
