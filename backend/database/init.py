import csv

from backend.database.schemas import City
from backend.database.config import get_session 


def init_db():
    session = next(get_session())
    try:
        with open("backend/database/world_cities_geoname.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            
            for line in reader:
                if not line["name_en"]:
                    continue

                session.add(
                    City(
                        name=line["name_en"], 
                        latitude=float(line["latitude"]), 
                        longitude=float(line["longitude"])
                    ) 
                )

            session.commit()

    except Exception as e:
        raise e