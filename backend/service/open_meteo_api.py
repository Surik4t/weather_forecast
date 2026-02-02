import requests, json, asyncio

BASE_URL = "https://api.open-meteo.com/"

async def get_current_weather(latitude: float, longitude: float) -> dict:
    try:
        response = requests.get(f"{BASE_URL}/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m,surface_pressure")
        
        data = json.loads(response.text)
        weather_data = {key: {"value": data["current"][key], "units": data["current_units"][key]} for key in data["current"].keys()}
        
        return weather_data
    
    except Exception as e:
        raise e
    

#asyncio.run(get_current_weather())