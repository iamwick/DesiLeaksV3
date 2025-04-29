from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Query  # This is FastAPI's Query
from pydantic import BaseModel
import redis.asyncio as redis
from redis.commands.search.query import Query as RedisQuery 
import gzip
import io
import json
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, Request
from typing import List, Dict
import asyncio
import re
import requests


app = FastAPI()

global_video_cache: List[Dict] = []
# Indexed cache by video ID
global_video_index_cache: Dict[str, Dict] = {}

# Allow frontend to access API (CORS policy)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ✅ Only allow your production frontend
    allow_credentials=True,
    allow_methods=["*"],  # ✅ Only the methods your frontend actually uses
    allow_headers=["*"],  # ✅ Common headers needed
)

# Hardcoded video list
videos = [

]

LIMIT_PAGES = 24

# Connect to Redis
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)


# Request model
class PageRequest(BaseModel):
    page: int = 1

async def refresh_video_cache():
    global  global_video_cache, global_video_index_cache
    while True:
        try:
            video_keys = await redis_client.keys("video:*")
            print("Refreshing video cache. Total keys:", len(video_keys))

            if video_keys:
                async with redis_client.pipeline() as pipe:
                    for key in video_keys:
                        pipe.hgetall(key)
                    videos = await pipe.execute()

                global_video_cache = videos  # Update general cache

                # Update the indexed cache
                global_video_index_cache = {video["id"]: video for video in videos}
                print("Video cache refreshed successfully.")

        except Exception as e:
            print(f"[Cache Refresh Error] {e}")

        await asyncio.sleep(2 * 60 * 60)  # Sleep for 2 hours



@app.on_event("startup")
async def startup_event():
    asyncio.create_task(refresh_video_cache())





# @app.post("/api/videos")
# async def get_videos(request: PageRequest):
#     page = request.page
#     start_idx = (page - 1) * LIMIT_PAGES
#     end_idx = start_idx + LIMIT_PAGES
#     video_keys = await redis_client.keys("video:*")  # Get all video keys

#     if not video_keys:
#         print("No videos found in Redis.")
#         return {"videos": [], "total": 0}

#     # Fetch all video hashes using pipelining
#     async with redis_client.pipeline() as pipe:
#         for key in video_keys:
#             pipe.hgetall(key)  # Queue HGETALL for each video key
#         videos = await pipe.execute()  # Execute all at once

#     # Create the response JSON
#     response_data = {
#         "videos": videos[start_idx:end_idx],
#         "total": len(videos),
#         "page": page
#     }

#     # Compress the JSON response using gzip
#     json_data = json.dumps(response_data).encode("utf-8")  # Convert JSON to bytes
#     compressed_data = gzip.compress(json_data)

#     # Create a StreamingResponse with the compressed data
#     return StreamingResponse(io.BytesIO(compressed_data), media_type="application/json", headers={"Content-Encoding": "gzip"})

@app.post("/api/videos")
async def get_videos(request: PageRequest):
    page = request.page
    start_idx = (page - 1) * LIMIT_PAGES
    end_idx = start_idx + LIMIT_PAGES

    global global_video_cache
    videos = global_video_cache[start_idx:end_idx]

    response_data = {
        "videos": videos,
        "total": len(global_video_cache),
        "page": page
    }

    json_data = json.dumps(response_data).encode("utf-8")
    compressed_data = gzip.compress(json_data)
    return StreamingResponse(io.BytesIO(compressed_data), media_type="application/json", headers={"Content-Encoding": "gzip"})



# Request model for searching
class SearchRequest(BaseModel):
    searchText: str
    page: int
    limit: int


# @app.post("/api/videos/search", response_model=dict)
# async def get_videos(search: SearchRequest):
#     try:
#         search_text = search.searchText.lower()
#         page = search.page  # ✅ Extract page number
#         limit = LIMIT_PAGES  # ✅ Extract limit per page
#         offset = (page - 1) * limit  # ✅ Calculate offset for pagination

#         print(f"Searching: {search_text}, Page: {page}, Limit: {limit}")

#         # Step 1: Get total count of matching videos (but don’t fetch records)
#         total_result = await redis_client.ft("video_idx").search(
#             RedisQuery(f"@title:{search_text}*").paging(0, 0)
#         )
#         total_count = total_result.total  # ✅ Correct total count

#         if total_count == 0:
#             return {"videos": [], "total": 0}  # No matches found

#         # Step 2: Fetch paginated results
#         result = await redis_client.ft("video_idx").search(
#             RedisQuery(f"@title:{search_text}*").paging(offset, limit)  # ✅ Paginated fetch
#         )



#         # Convert Redis docs to dict
#         all_videos = [await redis_client.hgetall(doc.id) for doc in result.docs]

#         sorted_videos = sorted(
#             all_videos, 
#             key=lambda x: int(x.get("viewCount", 0)),  # ✅ Convert to int for sorting
#             reverse=True  # ✅ Sort in descending order
#         )

#         response_data = {"videos": sorted_videos, "total": total_count}
#         # Compress the JSON response using gzip
#         json_data = json.dumps(response_data).encode("utf-8")  # Convert JSON to bytes
#         compressed_data = gzip.compress(json_data)

#         # Create a StreamingResponse with the compressed data
#         return StreamingResponse(io.BytesIO(compressed_data), media_type="application/json", headers={"Content-Encoding": "gzip"})
        

#     except Exception as e:
#         print(f"Error: {e}")
#         return {"error": str(e)}

@app.post("/api/videos/search", response_model=dict)
async def get_videos(search: SearchRequest):
    try:
        print(f"Search request: {search}")
        global global_video_index_cache
        search_text = search.searchText.lower()
        page = search.page  # Extract page number
        limit = LIMIT_PAGES  # Extract limit per page
        offset = (page - 1) * limit  # Calculate offset for pagination

        print(f"Searching: {search_text}, Page: {page}, Limit: {limit}")

        # Step 2: Filter the videos based on the search term
        regex = re.compile(re.escape(search_text), re.IGNORECASE)  # Create a case-insensitive regex
        matching_videos = [
            video for video in global_video_index_cache.values()
            if regex.search(video['title'])  # Match title using regex
        ]


        total_count = len(matching_videos)
        print(f"Total matching videos: {total_count}")

        if total_count == 0:
            return {"videos": [], "total": 0}  # No matches found

        # Step 3: Apply pagination and sorting (by viewCount)
        sorted_videos = sorted(
            matching_videos, 
            key=lambda x: int(x.get("viewCount", 0)),  # Sort by viewCount (descending)
            reverse=True
        )

        paginated_videos = sorted_videos[offset:offset + limit]

        response_data = {"videos": paginated_videos, "total": total_count}

        # Compress the JSON response using gzip
        json_data = json.dumps(response_data).encode("utf-8")  # Convert JSON to bytes
        compressed_data = gzip.compress(json_data)

        # Create a StreamingResponse with the compressed data
        return StreamingResponse(io.BytesIO(compressed_data), media_type="application/json", headers={"Content-Encoding": "gzip"})

    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}

@app.get("/api/videos/{id}")
async def get_video_by_id(id: str):
    try:
        global global_video_index_cache
        main_video = global_video_index_cache.get(id)

        if "rexporn.sex" in main_video["url"]:
            actual_url = get_rexporn_acual_url(main_video)
            if actual_url:
                main_video["url"] = actual_url
            else:
                print("Failed to fetch actual URL for rexporn")
        print(main_video)

        regex = re.compile(re.escape(main_video["title"]), re.IGNORECASE)  # Create a case-insensitive regex
        
        matching_videos = [
            video for video in global_video_index_cache.values()
            if regex.search(main_video['title'])  # Match title using regex
        ]

        all_videos = [ main_video ]  # Start with the main video
        all_videos.extend(matching_videos)
        sorted_videos = sorted(
            all_videos, 
            key=lambda x: int(x.get("viewCount", 0)),  # ✅ Convert to int for sorting
            reverse=True  # ✅ Sort in descending order
        )

        

        response_data = {"videos": sorted_videos, "total": len(sorted_videos)}
        # Compress the JSON response using gzip
        json_data = json.dumps(response_data).encode("utf-8")  # Convert JSON to bytes
        compressed_data = gzip.compress(json_data)

        # Create a StreamingResponse with the compressed data
        return StreamingResponse(io.BytesIO(compressed_data), media_type="application/json", headers={"Content-Encoding": "gzip"})
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}
    

@app.get("/trending/videos")
async def get_trending_videos():
    try:
        print('request reached here')

        global global_video_index_cache

        # Sort videos by viewCount (descending)
        sorted_videos = sorted(
            global_video_index_cache.values(),
            key=lambda x: int(x.get("viewCount", 0)),
            reverse=True
        )

        # Take top 100
        trending_videos = sorted_videos[:100]

        response_data = {
            "videos": trending_videos,
            "total": len(trending_videos)
        }

        # Compress JSON response using gzip
        json_data = json.dumps(response_data).encode("utf-8")
        compressed_data = gzip.compress(json_data)

        return StreamingResponse(io.BytesIO(compressed_data), media_type="application/json", headers={"Content-Encoding": "gzip"})

    except Exception as e:
        print(f"[Trending Error] {e}")
        return {"error": str(e)}


import requests
from bs4 import BeautifulSoup

import requests
from bs4 import BeautifulSoup

def get_rexporn_acual_url(video_info):
    url = video_info.get("url", "")
    
    # Check if the domain matches
    if "rexporn.sex" in url:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Find the div containing the download options
            download_div = soup.find('div', {'id': 'download_v'})
            if download_div:
                # Loop through each child div inside 'download_v' that contains the 'data-c' attribute
                for video_quality_div in download_div.find_all('div', {'data-c': True}):
                    data_c_value = video_quality_div['data-c']
                    if video_quality_div.text.strip() == "HD 720p":
                        # Construct the video URL using the data-c value
                        video_url = construct_video_url(data_c_value)
                        print(f"Found HD 720p video URL: {video_url}")
                        return video_url

            print("Download options not found or missing data-c attributes.")
            return None

        except Exception as e:
            print(f"Error fetching video from rexporn.sex: {e}")
            return None
    else:
        # If the domain doesn't match, just return the original URL
        return video_info.get("url")


def construct_video_url(data_c_value):
    #bb6ce926341795770f1b8fd913abeed1;720p;441250;194;18171;1745476256;vkMZIS9BPx01sNqhrtJ2RA;d6;1
    #['bc555e722f8a6544c94715249aae0fc1', '720p', '715000', '196', '16658', '1745477205', 'LKOBhZ5WICjYQnK9fEQiEw', 'd8', '1']

    # Split the data_c_value by semicolon
    parts = data_c_value.split(';')
    print(parts)
    adjustValue = int(parts[4]) - int(parts[4])%1000
    url = f"https://{parts[7]}.vstor.top/whpvid/{parts[5]}/{parts[6]}/{adjustValue}/{parts[4]}/{parts[4]}.mp4"
    return url



