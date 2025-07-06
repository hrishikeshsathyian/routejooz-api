import csv
import pgeocode
from interfaces import LocationObject
from typing import List

nomi = pgeocode.Nominatim("SG")
data: List[LocationObject] = []


with open('data.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        postal_code = row['postal_code']
        result = nomi.query_postal_code(postal_code)
        data_object = LocationObject(
            qr_code=row['qr_code'],
            name=result['place_name'],
            latitude=result['latitude'],
            longitude=result['longitude'],
        )
        data.append(data_object)




    
    