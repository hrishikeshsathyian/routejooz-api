from fastapi import FastAPI, HTTPException
from db.queries import add_locations_to_db
from preprocessing.parser import parse_raw_data

app = FastAPI()

@app.get("/ping")
async def ping():
    return {"message": "Hello, World!"}

@app.put("/locations")
async def locations():
    locations, _ = parse_raw_data()
    response = add_locations_to_db(locations)
    return response
   