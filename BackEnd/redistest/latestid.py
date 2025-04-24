import redis

# Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Get all keys matching the pattern "video:*"
video_keys = redis_client.keys("video:*")

# Extract numeric IDs from keys and find the maximum
video_ids = [int(key.split(":")[1]) for key in video_keys if key.split(":")[1].isdigit()]

if video_ids:
    latest_id = max(video_ids)
    print(f"Latest Video ID: {latest_id}")
else:
    print("No video keys found.")

