from fastapi import APIRouter, HTTPException

from sqlmodel import select

from datetime import datetime

from backend.database.config import SessionDep
from backend.database.models import City, CityInDB, Forecast, ForecastQuery

from backend.service.open_meteo_api import get_current_weather, update_hourly_forecast


cities_router = APIRouter(prefix="/cities", tags=["cities"])


@cities_router.get("/all")
async def get_cities_list(session: SessionDep) -> list[CityInDB]:
    try:
        query = select(CityInDB)
        result = session.exec(query)
        cities = result.all()
        return cities
    
    except Exception as e:
        raise e


@cities_router.put("/")
async def add_city(new_city: City, session: SessionDep):
    city_to_create = CityInDB(
        name=new_city.name.title(),
        latitude=new_city.latitude,
        longitude=new_city.longitude,
        forecast=None,
        forecast_updated_time=datetime(year=2000, month=1, day=1, hour=0, minute=0).isoformat()
    )
    session.add(city_to_create)
    session.commit()
    return


@cities_router.post("/city_forecast")
async def forecast_for_city(forecast_query: ForecastQuery, session: SessionDep):

    try:        
        db_query = select(CityInDB).where(CityInDB.name == forecast_query.city_name.title())
        city = session.exec(db_query).first()
        if city:
            hourly_forecast = await update_hourly_forecast(city.latitude, city.longitude)
            return hourly_forecast
        raise HTTPException(status_code=404, detail="City not found.")
    
    except Exception as e:
        raise e
    
