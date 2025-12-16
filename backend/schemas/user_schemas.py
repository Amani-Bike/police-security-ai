from pydantic import BaseModel

class UpdateLocationSchema(BaseModel):
    latitude: float
    longitude: float
