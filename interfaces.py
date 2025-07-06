from pydantic import BaseModel

class LocationObject(BaseModel):
    postal_code: int
    qr_code: str
    name: str
    latitude: float
    longitude: float
