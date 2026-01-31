from fastapi import APIRouter

forecast_router = APIRouter(prefix="/forecast")

@forecast_router.get("/current")
async def current_forecast(latitude: float, longitude: float):
    return