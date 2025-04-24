from fastapi import FastAPI, Query
import redis.asyncio as redis
from redis.commands.search.query import Query

app = FastAPI()

# Connect to Redis
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)


@app.get("/test-redis")
async def test_redis():
    try:
        pong = redis_client.ping()
        return {"status": "connected"} if pong else {"status": "not connected"}
    except Exception as e:
        return {"error": str(e)}
