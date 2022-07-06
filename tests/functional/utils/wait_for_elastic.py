import asyncio

from config import config
from utils.utils import elastic_connection


async def wait_for_elastic():
    async with elastic_connection(hosts=[config.ELASTIC_PATH]) as elastic:
        while True:
            if await elastic.ping():
                return True
            print("waiting for elastic")
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(wait_for_elastic())
