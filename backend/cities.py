from fastapi import APIRouter

from sqlmodel import select
from backend.database.config import SessionDep
from backend.database.schemas import City as city_schema
from backend.models.models import Coords, City
from backend.open_meteo_api import get_current_weather

cities_router = APIRouter(prefix="/cities")

@cities_router.get("/all")
async def get_cities_list(session: SessionDep) -> list[City]:
    try:
        statement = select(city_schema)
        result = session.exec(statement)
        cities = result.all()
        return cities
    
    except Exception as e:
        raise e
    

