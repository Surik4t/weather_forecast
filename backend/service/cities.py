from fastapi import APIRouter

from sqlmodel import select
from backend.database.config import SessionDep
from backend.database.models import City
from backend.database.models import Coords
from backend.service.open_meteo_api import get_current_weather

cities_router = APIRouter(prefix="/cities")

@cities_router.get("/all")
async def get_cities_list(session: SessionDep) -> list[City]:
    try:
        query = select(City)
        result = session.exec(query)
        cities = result.all()
        return cities
    
    except Exception as e:
        raise e


@cities_router.post("/{city_name}")
async def forecast_for_city(city_name, session: SessionDep):
    try:        
        query = select(City).where(City.name == city_name.title())
        city = session.exec(query).first()
        forecast = await get_current_weather(city.latitude, city.longitude)
        return forecast
    except Exception as e:
        raise e
    
