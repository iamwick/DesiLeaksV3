from fastapi import FastAPI, Query
import redis.asyncio as redis
from redis.commands.search.query import Query

app = FastAPI()

# Connect to Redis
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

@app.get("/search")
async def search_videos(query: str):
    """Search for videos by title"""
    search_query = Query(f"@title:{query}*").paging(0, 10)  # Partial match
    result = await redis_client.ft("video_idx").search(search_query)

    videos = []
    for doc in result.docs:
        videos.append({
            "title": doc.title,
            "thumbnail": doc.thumbnail,
            "url": doc.url
        })

    return {"results": videos}


