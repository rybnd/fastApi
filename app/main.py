from fastapi import FastAPI, HTTPException
import redis.asyncio as redis
import os

app = FastAPI(title="Production FastAPI Service", version="1.0.0")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = None

@app.on_event("startup")
async def startup():
    global redis_client
    redis_client = redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

@app.on_event("shutdown")
async def shutdown():
    await redis_client.close()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "fastapi-backend"}

@app.get("/data/{item_id}")
async def get_data(item_id: str):
    cached = await redis_client.get(item_id)
    if cached:
        return {"source": "cache", "data": cached}
    data = f"Processed-Data-{item_id}"
    await redis_client.setex(item_id, 60, data)
    return {"source": "database", "data": data}