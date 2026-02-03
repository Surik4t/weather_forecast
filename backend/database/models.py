from sqlmodel import SQLModel, Field

# Cities
class Coords(SQLModel):
    latitude: float = Field(default=0, le=90, ge=-90)
    longitude: float = Field(default=0, le=180, ge=-180)


class City(Coords):
    name: str = Field(index=True)


class CityInDB(City, table=True):
    id: int | None = Field(default=None, primary_key=True)
    forecast: str | None
    forecast_updated_time: str | None


# Users 
class User(SQLModel):
    id: int | None = Field(default=None, primary_key=True) 
    username: str = Field(index=True, unique=True)
    disabled: bool | None = None


class NewUser(SQLModel):
    username: str
    password: str


class UserInDB(User, table=True):
    hashed_password: str


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    username: str | None = None
