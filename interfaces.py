from pydantic import BaseModel

class LocationObject(BaseModel):
    qr_code: str
    name: str
    latitude: float
    longitude: float
