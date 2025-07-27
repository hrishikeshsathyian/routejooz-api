from collections import defaultdict
import csv
import os
import requests
from pydantic import BaseModel, ValidationError
from typing import List
import math
import dotenv

class LocationObject(BaseModel):
    postal_code: int
    qr_code: str
    name: str
    latitude: float
    longitude: float

# Load environment variables from a .env file
dotenv.load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")  # set this in your environment

def geocode_postal_code(postal_code: str) -> dict:
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": postal_code,
        "region": "sg",  # restricts results to Singapore
        "key": GOOGLE_MAPS_API_KEY
    }
    response = requests.get(url, params=params)
    response.raise_for_status()  # raises HTTPError for bad status
    data = response.json()
    print
    if data["status"] != "OK":
        return None
    result = data["results"][0]
    location = result["geometry"]["location"]
    place_name = result.get("formatted_address", "")
    return {
        "postal_code": postal_code,
        "latitude": location["lat"],
        "longitude": location["lng"],
        "place_name": place_name,
    }

def parse_raw_data(filename: str = "preprocessing/data.csv") -> List[LocationObject]:
    deduped_locations: List[LocationObject] = []
    postal_to_qr_codes = defaultdict(list)
    seen_qr_codes = set()
    seen_postal_codes = set()
    invalid_count = 0
    duplicate_qr = 0
    duplicate_postal = 0

    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            postal_code = row['postal_code'].strip()
            qr_code = str(row['qr_code'])

            if qr_code in seen_qr_codes:
                duplicate_qr += 1
                continue
            seen_qr_codes.add(qr_code)

            postal_to_qr_codes[int(postal_code)].append(qr_code)
            if postal_code in seen_postal_codes:
                duplicate_postal += 1
                continue
            seen_postal_codes.add(postal_code)
            print(postal_code, qr_code)
            result = geocode_postal_code(postal_code)
            print(result)
            if result is None:
                invalid_count += 1
                continue

            data_object = LocationObject(
                qr_code=qr_code,
                postal_code=int(postal_code),
                name=result["place_name"],
                latitude=result["latitude"],
                longitude=result["longitude"],
            )
            deduped_locations.append(data_object)

    print(f"Duplicate QR codes found: {duplicate_qr}")
    print(f"Duplicate Postal codes: {duplicate_postal}")
    print(f"Invalid postal codes: {invalid_count}")
    print(f"Total locations parsed: {len(deduped_locations)}")
    return deduped_locations, postal_to_qr_codes

if __name__ == "__main__":
    try:
        locations, postal_to_qr_codes = parse_raw_data()
        print(f"Parsed {len(locations)} valid locations.")
        print(locations[:5])  # Print first 5 locations for verification
    except ValidationError as e:
        print(f"Validation error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")