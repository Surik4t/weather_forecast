from fastapi import FastAPI
from contextlib import asynccontextmanager

from backend.service.forecast import forecast_router
from backend.service.cities import cities_router
from backend.service.users import users_router
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
app.include_router(users_router)
