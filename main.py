from fastapi import FastAPI
from db.queries import get_all_locations

app = FastAPI()

@app.get("/ping")
async def ping():
    return {"message": "Hello, World!"}

@app.get("/locations")
async def locations():
    locations = get_all_locations()
    return locations.data