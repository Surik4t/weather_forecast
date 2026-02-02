from fastapi import APIRouter
from backend.database.models import Coords
from backend.service.open_meteo_api import get_current_weather

forecast_router = APIRouter(prefix="/forecast")

@forecast_router.post("/current")
async def current_forecast(coords: Coords):
    try:
        data = await get_current_weather(coords.latitude, coords.longitude)
        return data
    
    except Exception as e:
        raise e
    

