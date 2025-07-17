from fastapi import FastAPI, HTTPException
from db.queries import add_locations_to_db
from preprocessing.parser import parse_raw_data
from preprocessing.solver import solve

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
async def ping():
    return {"data": "pong!"}

@app.put("/locations")
async def locations():
    locations, _ = parse_raw_data()
    response = add_locations_to_db(locations)
    return response

@app.get("/solve")
async def solver(num_vehicles: int = 3): 
    coords_res = solve(num_vehicles)
    return {"data": coords_res}