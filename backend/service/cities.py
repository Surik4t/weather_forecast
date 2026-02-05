from fastapi import APIRouter, HTTPException
import uuid

from sqlmodel import select

from datetime import datetime, timedelta

from backend.database.config import SessionDep
from backend.database.models import (
    User,
    City, 
    CityInDB, 
    Forecast, 
    ForecastQuery, 
    ForecastResponse,
)

from backend.service.open_meteo_api import get_current_weather, update_hourly_forecast


cities_router = APIRouter(prefix="/cities", tags=["cities"])


@cities_router.get("/all/{user_id}")
async def get_cities_list(user_id: uuid.UUID, session: SessionDep):
    try:
        query = select(User).where(User.id == user_id)
        user = session.exec(query).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        
        return user.cities
    
    except Exception as e:
        raise e


@cities_router.put("/add_city", status_code=201)
async def add_city(new_city: City, session: SessionDep):
    try:
        user = session.exec(select(User).where(User.id==new_city.user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        
        query = select(CityInDB).where((CityInDB.user_id == new_city.user_id) & (CityInDB.name == new_city.name))
        city_exists = session.exec(query).first()
        print(city_exists)
        if city_exists:
            raise HTTPException(status_code=409, detail=f"City with name '{new_city.name}' already exists.")

        city_to_create = CityInDB(
            name=new_city.name.title(),
            user_id=new_city.user_id,
            latitude=new_city.latitude,
            longitude=new_city.longitude,
            forecast_updated_time=None,
        )

        session.add(city_to_create)
        session.commit()

        return {"message": f"City '{city_to_create.name}' created."}
    
    except Exception as e:
        raise e


@cities_router.post("/city_forecast")
async def forecast_for_city(forecast_query: ForecastQuery, session: SessionDep):
    
    async def update_forecast(city: CityInDB):
            delete_query = select(Forecast).where(Forecast.city_id == city.id)
            old_forecasts = session.exec(delete_query).all()
            for forecast in old_forecasts:
                session.delete(forecast)

            hourly_forecasts = await update_hourly_forecast(city.latitude, city.longitude)
            for forecast in hourly_forecasts:
                forecast_data = forecast.model_dump()
                forecast_data["city_id"] = city.id
                forecast_data["city_name"] = city.name
                forecast_to_save = Forecast.model_validate(forecast_data)
                session.add(forecast_to_save)

            city.forecast_updated_time = datetime.now().isoformat()
            session.commit()


    def filter_by_params(forecast: ForecastResponse):
        if not forecast_query.temp:
            del(forecast.temp)
        if not forecast_query.humidity:
            del(forecast.humidity)
        if not forecast_query.wind:
            del(forecast.wind)
        if not forecast_query.precipitation:
            del(forecast.rain)
            del(forecast.shower)
            del(forecast.snow)


    try: 
        user = session.exec(select(User).where(User.id == forecast_query.user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        city = [c for c in user.cities if c.name == forecast_query.city_name].pop()

        if city:
            if not city.forecast_updated_time or (
                datetime.fromisoformat(city.forecast_updated_time) + timedelta(minutes=15) < datetime.now()
            ): 
                await update_forecast(city)

            requested_forecast = [fc for fc in city.forecast_hourly if datetime.fromisoformat(fc.time).hour == forecast_query.time_hours].pop()
            forecast_response = ForecastResponse.model_validate(requested_forecast)
            
            filter_by_params(forecast_response)

            return forecast_response

        raise HTTPException(status_code=404, detail="City not found.")
    
    except Exception as e:
        raise e
    
