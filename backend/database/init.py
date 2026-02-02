import csv

from sqlmodel import select

from backend.database.models import City
from backend.database.config import get_session 


def init_db():
    session = next(get_session())
    try:
        with open("backend/database/world_cities_geoname.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            
            for line in reader:
                if not line["name_en"]:
                    continue
                
                name = line["name_en"].strip()
                latitude = float(line["latitude"])
                longitude = float(line["longitude"])

                statement = select(City).where(City.name == name)
                city_in_database = session.exec(statement).first()

                if not city_in_database:
                    session.add(
                        City(
                            name=name, 
                            latitude=latitude, 
                            longitude=longitude
                        ) 
                    )

            session.commit()

    except Exception as e:
        raise e