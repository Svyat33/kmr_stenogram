import asyncio
import datetime
import json
import logging
import os
import sys

import aiohttp
import aioredis

from dotenv import load_dotenv, dotenv_values

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from web.loader import LoadDocuments


logging.basicConfig(level=logging.DEBUG, format='%(message)s')
logger = logging.getLogger(__name__)

load_dotenv(os.path.dirname(os.path.abspath(__file__)) + "/../.env")

async def main():
    redis = await aioredis.create_redis_pool(os.getenv("REDIS_URL"))
    # print(await redis.get("last_work"))
    val = datetime.datetime.now().strftime("%s")

    await redis.set("last_work", val)
    if True:
        async with aiohttp.ClientSession() as session:
            for doc in LoadDocuments(count=10):
                async with session.post(os.getenv('LNK'),
                                        json=doc.dict(),
                                        headers={'AUTHORIZATION': os.getenv('KEY')}) as resp:
                    if resp.ok:
                        await redis.lpush(os.getenv('LAST_DOC_KEY'), json.dumps(await resp.json()))
                        await redis.ltrim(os.getenv('LAST_DOC_KEY'), 0, int(os.getenv('LAST_DOC_COUNT')))

    dd = await redis.lrange(os.getenv('LAST_DOC_KEY'), 0, int(os.getenv('LAST_DOC_COUNT')))
    print(dd)
    redis.close()
    await redis.wait_closed()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
