from interfaces import LocationObject
from .client import supabase
from typing import List 
from fastapi import HTTPException

LOCATIONS_TABLE_NAME = "locations"


def add_locations_to_db(locations: List[LocationObject]):
    # wipe the table before repopulating data
    supabase.table(LOCATIONS_TABLE_NAME).delete().neq("postal_code", 0).execute()
    records = []
    for location in locations: 
        records.append(location.model_dump())
    try:
        response = supabase.table(LOCATIONS_TABLE_NAME).insert(records).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inserting data: {str(e)}")
    return {"status": "success", "message": "Locations inserted successfully", "inserted_count": len(records)}


