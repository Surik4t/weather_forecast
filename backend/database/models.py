from sqlmodel import SQLModel, Field


class Coords(SQLModel):
    latitude: float = Field(default=0, le=90, ge=-90)
    longitude: float = Field(default=0, le=180, ge=-180)


class City(Coords, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    