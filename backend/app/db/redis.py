import redis.asyncio as aioredis
from backend.app.core.settings import settings

redis_client = None

async def connect_redis():
    global redis_client
    redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

async def close_redis():
    if redis_client:
        await redis_client.close()

def get_redis():
    return redis_client
