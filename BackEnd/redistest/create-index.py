import redis
from redis.commands.search.field import TextField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType

# Connect to Redis
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

def create_video_index():
    """Creates an index for fast searching"""
    try:
        index_name = "video_idx"

        # Define the index schema
        schema = (
            TextField("title", weight=5.0),  # Higher weight for relevance
            TextField("url"),
            TextField("thumbnail"), 
            TextField("viewCount")
        )

        # Create index if it doesn’t exist
        redis_client.ft(index_name).create_index(
            schema,
            definition=IndexDefinition(prefix=["video:"], index_type=IndexType.HASH),
        )
        print("✅ Search index created successfully")

    except redis.exceptions.ResponseError:
        print("⚠️ Index already exists. Skipping creation.")

if __name__ == "__main__":
    create_video_index()

