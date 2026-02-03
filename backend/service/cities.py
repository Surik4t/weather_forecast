from fastapi import APIRouter

from sqlmodel import select

from datetime import datetime

from backend.database.config import SessionDep
from backend.database.models import City, CityInDB

from backend.service.open_meteo_api import get_current_weather, get_hourly_forecast


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
        forecast_updated_time=datetime.now().isoformat()
    )
    session.add(city_to_create)
    session.commit()
    return


@cities_router.post("/{city_name}")
async def forecast_for_city(city_name, session: SessionDep):
    try:        
        query = select(CityInDB).where(CityInDB.name == city_name.title())
        city = session.exec(query).first()
        forecast = await get_hourly_forecast(city.latitude, city.longitude)
        return forecast
    except Exception as e:
        raise e
    
