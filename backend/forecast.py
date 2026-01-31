from fastapi import APIRouter
from backend.models.models import Coords
from backend.open_meteo_api import get_current_weather

forecast_router = APIRouter(prefix="/forecast")

@forecast_router.post("/current")
async def current_forecast(coords: Coords):
    try:
        data = await get_current_weather(coords.latitude, coords.longitude)
        return data
    except Exception as e:
        raise e