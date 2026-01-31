from sqlmodel import Field, SQLModel


class City(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    latitude: int = Field(default=None, le=90, ge=-90)
    longitude: int = Field(default=None, le=180, ge=-180)