import asyncio

from config import config
from utils.base import backoff, elastic_connection


@backoff()
async def ping_elastic():
    async with elastic_connection(hosts=[config.ELASTIC_PATH]) as elastic:
        return await elastic.ping()


if __name__ == "__main__":
    asyncio.run(ping_elastic())
