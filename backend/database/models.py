from sqlmodel import SQLModel, Field


class Coords(SQLModel):
    latitude: float = Field(default=0, le=90, ge=-90)
    longitude: float = Field(default=0, le=180, ge=-180)


class City(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    latitude: float = Field(default=None, le=90, ge=-90)
    longitude: float = Field(default=None, le=180, ge=-180)