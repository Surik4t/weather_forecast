from fastapi import FastAPI
from backend.forecast import forecast_router

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(forecast_router)
