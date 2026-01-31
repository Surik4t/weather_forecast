from pydantic import BaseModel, Field

class Coords(BaseModel):
    latitude: float = Field(default=0, le=90, ge=-90)
    longitude: float = Field(default=0, le=180, ge=-180)