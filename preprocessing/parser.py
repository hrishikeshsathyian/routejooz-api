from collections import defaultdict
import csv
import pgeocode
from pydantic import ValidationError
from interfaces import LocationObject
from typing import List
import math


# Parse raw data from CSV file , converts postal code to lat, lng coordinaates and stores as a LocationObject
def parse_raw_data(filename: str = "preprocessing/data.csv") -> List[LocationObject]:
    nomi = pgeocode.Nominatim("SG")
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
            postal_code = row['postal_code']
            # HANDLE DUPLICATE QR CODES, keep count for logging purposes
            qr_code = str(row['qr_code'])
            if qr_code in seen_qr_codes:
                duplicate_qr += 1
                continue
            seen_qr_codes.add(qr_code)

             # HANDLE DUPLICATE POSTAL CODE, we treat them as one location but store the QR codes for future reference
        
            postal_to_qr_codes[int(postal_code)].append(qr_code)
            if postal_code in seen_postal_codes:
                duplicate_postal += 1
                continue 
            seen_postal_codes.add(postal_code)

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
            deduped_locations.append(data_object)
    print(f"Duplicate QR codes found: {duplicate_qr}")
    print(f"Duplicate Postal codes: {duplicate_postal}")
    print(f"Invalid postal codes: {invalid_count}")
    print(f"Total locations parsed: {len(deduped_locations)}")
    return deduped_locations, postal_to_qr_codes



    
    