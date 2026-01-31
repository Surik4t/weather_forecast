from fastapi import FastAPI
from contextlib import asynccontextmanager

from backend.forecast import forecast_router
from backend.cities import cities_router
from backend.database.init import init_db

from backend.database.config import create_db_and_tables


@asynccontextmanager
async def on_startup(app: FastAPI):
    create_db_and_tables()
    init_db()
    yield

app = FastAPI(lifespan=on_startup)


@app.get("/")
async def root():
    return {"message": "Hello World"}



app.include_router(forecast_router)
app.include_router(cities_router)
