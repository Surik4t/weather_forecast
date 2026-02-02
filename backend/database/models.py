from sqlmodel import SQLModel, Field

# Cities
class Coords(SQLModel):
    latitude: float = Field(default=0, le=90, ge=-90)
    longitude: float = Field(default=0, le=180, ge=-180)


class City(Coords, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)


# Users 
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True) 
    username: str = Field(index=True, unique=True)
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str