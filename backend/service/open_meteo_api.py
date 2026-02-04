import requests, json, asyncio


BASE_URL = "https://api.open-meteo.com/"


async def get_current_weather(latitude: float, longitude: float) -> dict:
    try:
        response = requests.get(f"{BASE_URL}/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m,surface_pressure")
        
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
    

async def update_hourly_forecast(latitude: float, longitude: float) -> list[dict]:
    try:
        response = requests.get(f"{BASE_URL}/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,rain,showers,snowfall,wind_speed_10m&forecast_days=1")
        
        data = json.loads(response.text)

        times = data["hourly"]["time"]
        temperatures = data["hourly"]["temperature_2m"]
        wind_speeds = data["hourly"]["wind_speed_10m"]
        rains = data["hourly"]["rain"]
        showers = data["hourly"]["showers"]
        snows = data["hourly"]["snowfall"]

        units = data["hourly_units"]
        timezone = data["timezone"]

        weather_data = list()
        for time, temp, wind, rain, shower, snow in zip(times, temperatures, wind_speeds, rains, showers, snows):
            weather_data.append({
                "Time": f"{time}",
                "Timezone": f"{timezone}",
                "Temp": f"{temp}{units["temperature_2m"]}",
                "Wind": f"{wind} {units["wind_speed_10m"]}",
                "Rain": f"{rain} {units["rain"]}",
                "Shower": f"{shower} {units["showers"]}",
                "Snow": f"{snow} {units["snowfall"]}",
            })

        return weather_data
    
    except Exception as e:
        raise e
