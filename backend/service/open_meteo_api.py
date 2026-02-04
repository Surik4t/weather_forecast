import requests, json, asyncio
from backend.database.models import ForecastBase


BASE_URL = "https://api.open-meteo.com/v1/forecast"


async def get_current_weather(latitude: float, longitude: float) -> dict:
    try:
        params = "current=temperature_2m,wind_speed_10m,surface_pressure&timezone=auto"
        response = requests.get(f"{BASE_URL}?latitude={latitude}&longitude={longitude}&{params}")
        
        data = json.loads(response.text)
        
        current = data["current"]
        units = data["current_units"]

        weather_data = {
            "Time": f"{current["time"]} {data["timezone"]}",
            "Temp": f"{current["temperature_2m"]}{units["temperature_2m"]}",
            "Wind speed": f"{current["wind_speed_10m"]} {units["wind_speed_10m"]}",
            "Pressure": f"{current["surface_pressure"]} {units["surface_pressure"]}",
        }
        
        return weather_data
    
    except Exception as e:
        raise e
    

async def update_hourly_forecast(latitude: float, longitude: float) -> list[ForecastBase]:
    try:
        params = "hourly=temperature_2m,relative_humidity_2m,rain,showers,snowfall,wind_speed_10m&timezone=auto&forecast_days=1"
        response = requests.get(f"{BASE_URL}?latitude={latitude}&longitude={longitude}&{params}")
        
        data = json.loads(response.text)

        times = data["hourly"]["time"]
        temperatures = data["hourly"]["temperature_2m"]
        humidities = data["hourly"]["relative_humidity_2m"]
        wind_speeds = data["hourly"]["wind_speed_10m"]
        rains = data["hourly"]["rain"]
        showers = data["hourly"]["showers"]
        snows = data["hourly"]["snowfall"]

        units = data["hourly_units"]
        timezone = data["timezone"]

        weather_data = list()
        for time, temp, humidity, wind, rain, shower, snow in zip(times, temperatures, humidities, wind_speeds, rains, showers, snows):
            weather_data.append(
                ForecastBase(
                    time=f"{time}",
                    timezone=f"{timezone}",
                    temp=f"{temp}{units["temperature_2m"]}",
                    humidity=f"{humidity}{units["relative_humidity_2m"]}",
                    wind=f"{wind} {units["wind_speed_10m"]}",
                    rain=f"{rain} {units["rain"]}",
                    shower=f"{shower} {units["showers"]}",
                    snow=f"{snow} {units["snowfall"]}",
                )
            )

        return weather_data
    
    except Exception as e:
        raise e
