from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
import uuid

# Cities
class Coords(SQLModel):
    latitude: float = Field(default=0, le=90, ge=-90)
    longitude: float = Field(default=0, le=180, ge=-180)


class City(Coords):
    name: str = Field(default="City Name", index=True)
    user_id: uuid.UUID = Field(default="User ID")


class CityInDB(City, table=True):
    id: int | None = Field(default=None, primary_key=True)
    forecast_hourly: Optional[List["Forecast"]] = Relationship(back_populates="city")
    forecast_updated_time: str | None

    user_id: uuid.UUID = Field(foreign_key="user.id")

    user: "User" = Relationship(back_populates="cities")


# Forecasts
class ForecastBase(SQLModel):
    time: str
    timezone: str
    temp: str
    humidity: str
    wind: str
    rain: str
    shower: str
    snow: str


class ForecastResponse(ForecastBase):
    city_name: str = Field(default="City Name")
    
    class Config:
        from_attributes = True


class Forecast(ForecastBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    city_id: int = Field(default=None, foreign_key="cityindb.id")
    city_name: str = Field(default="City Name")

    city: CityInDB = Relationship(back_populates="forecast_hourly")


class ForecastQuery(SQLModel):
    user_id: uuid.UUID = Field(default="User ID")
    city_name: str = Field(default="City Name")
    time_hours: int = Field(default=12, ge=0, le=23)
    temp: bool = Field(default=True)
    humidity: bool = Field(default=True)
    wind: bool = Field(default=True)
    precipitation: bool = Field(default=True)


# Users 
class User(SQLModel, table=True):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True, 
        index=True
    )
    username: str = Field(index=True, unique=True)

    cities: List["CityInDB"] = Relationship(back_populates="user")
