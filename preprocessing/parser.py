import csv
import pgeocode
from pydantic import ValidationError
from interfaces import LocationObject
from typing import List
import math


# Parse raw data from CSV file , converts postal code to lat, lng coordinaates and stores as a LocationObject
def parse_raw_data(filename: str = "preprocessing/data.csv") -> List[LocationObject]:
    nomi = pgeocode.Nominatim("SG")
    data: List[LocationObject] = []
    seen_qr_codes = set()
    invalid_count = 0
    duplicate_qr = 0
    with open(filename, newline='') as csvfile:
        
        reader = csv.DictReader(csvfile)

        for row in reader:
            postal_code = row['postal_code']
            # just to safely check if there any duplicates in the csv files
            qr_code = str(row['qr_code'])
            if qr_code in seen_qr_codes:
                duplicate_qr += 1
                continue
            seen_qr_codes.add(qr_code)

            result = nomi.query_postal_code(postal_code)
            if math.isnan(result.latitude) or math.isnan(result.longitude):
                invalid_count += 1
                continue 
            data_object = LocationObject(
                qr_code=str(row['qr_code']),
                postal_code=int(result.postal_code),
                name=result.place_name,
                latitude=float(result.latitude),
                longitude=float(result.longitude),
            )
            data.append(data_object)
    print(f"Duplicate QR codes found: {duplicate_qr}")
    print(f"Invalid postal codes: {invalid_count}")
    print(f"Total locations parsed: {len(data)}")
    return data



    
    