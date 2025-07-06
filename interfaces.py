from dataclasses import dataclass


@dataclass 
class LocationObject: 
    qr_code: str
    name: str
    latitude: float
    longitude: float
