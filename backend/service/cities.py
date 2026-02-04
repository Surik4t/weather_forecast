from fastapi import APIRouter, HTTPException

from sqlmodel import select

from datetime import datetime, timedelta

from backend.database.config import SessionDep
from backend.database.models import City, CityInDB, Forecast, ForecastQuery, ForecastResponse

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
                    timezone=forecast["Timezone"],
                    temp=forecast["Temp"],
                    humidity=forecast["Humidity"],
                    wind=forecast["Wind"],
                    rain=forecast["Rain"],
                    shower=forecast["Shower"],
                    snow=forecast["Snow"],
                )
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
        db_query = select(CityInDB).where(CityInDB.name == forecast_query.city_name.title())
        city = session.exec(db_query).first()
        
        if city:
            if not city.forecast_updated_time or (
                datetime.fromisoformat(city.forecast_updated_time) + timedelta(minutes=1) < datetime.now()
            ): 
                await update_forecast(city)

            requested_forecast = [fc for fc in city.forecast_hourly if datetime.fromisoformat(fc.time).hour == forecast_query.time_hours].pop()
            forecast_response = ForecastResponse.model_validate(requested_forecast)
            
            filter_by_params(forecast_response)

            return forecast_response

        raise HTTPException(status_code=404, detail="City not found.")
    
    except Exception as e:
        raise e
    
