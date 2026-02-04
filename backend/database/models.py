from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

# Cities
class Coords(SQLModel):
    latitude: float = Field(default=0, le=90, ge=-90)
    longitude: float = Field(default=0, le=180, ge=-180)


class City(Coords):
    name: str = Field(index=True, unique=True)


class CityInDB(City, table=True):
    id: int | None = Field(default=None, primary_key=True)
    forecast_hourly: Optional[List["Forecast"]] = Relationship(back_populates="city")
    forecast_updated_time: str | None


# Forecasts
class ForecastBase(SQLModel):
    city_name: str 
    time: str
    timezone: str
    temp: str
    humidity: str
    wind: str
    rain: str
    shower: str
    snow: str


class ForecastResponse(ForecastBase):
    class Config:
        from_attributes = True


class Forecast(ForecastBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    city_id: int = Field(default=None, foreign_key="cityindb.id")

    city: CityInDB = Relationship(back_populates="forecast_hourly")


class ForecastQuery(SQLModel):
    city_name: str
    time_hours: int = Field(default=12, ge=0, le=23)
    temp: bool = Field(default=True)
    humidity: bool = Field(default=True)
    wind: bool = Field(default=True)
    precipitation: bool = Field(default=True)


# Users 
class User(SQLModel):
    id: int | None = Field(default=None, primary_key=True) 
    username: str = Field(index=True, unique=True)
    disabled: bool | None = None


class NewUser(SQLModel):
    username: str
    password: str


class UserInDB(User, table=True):
    hashed_password: str


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    username: str | None = None
