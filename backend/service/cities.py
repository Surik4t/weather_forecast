from fastapi import APIRouter, HTTPException

from sqlmodel import select

from datetime import datetime, timedelta

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
    try:
        city_to_create = CityInDB(
            name=new_city.name.title(),
            latitude=new_city.latitude,
            longitude=new_city.longitude,
            forecast_updated_time=None,
        )
        session.add(city_to_create)
        session.commit()
        return
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error.")


@cities_router.post("/city_forecast")
async def forecast_for_city(forecast_query: ForecastQuery, session: SessionDep):
    
    async def update_forecast(city: CityInDB):
            delete_query = select(Forecast).where(Forecast.city_id == city.id)
            old_forecasts = session.exec(delete_query).all()
            for forecast in old_forecasts:
                session.delete(forecast)

            hourly_forecasts = await update_hourly_forecast(city.latitude, city.longitude)
            for forecast in hourly_forecasts:
                forecast_to_save = Forecast(
                    city_id=city.id,
                    city_name=city.name,
                    time=forecast["Time"],
                    temp=forecast["Temp"],
                    wind=forecast["Wind"],
                    rain=forecast["Rain"],
                    shower=forecast["Shower"],
                    snow=forecast["Snow"],
                )
                session.add(forecast_to_save)

            city.forecast_updated_time = datetime.now().isoformat()
            session.commit()

            return hourly_forecasts

    try:        
        db_query = select(CityInDB).where(CityInDB.name == forecast_query.city_name.title())
        city = session.exec(db_query).first()
        if city:
            if not city.forecast_updated_time or (
                datetime.fromisoformat(city.forecast_updated_time) + timedelta(minutes=15) < datetime.now()
            ): 
                return await update_forecast(city)
            return city.forecast_hourly

        raise HTTPException(status_code=404, detail="City not found.")
    
    except Exception as e:
        raise e
    
