from typing import Annotated
from datetime import timedelta, datetime, timezone

from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from backend.database.models import User, NewUser, UserInDB, Token, TokenData
from backend.database.config import SessionDep
from sqlmodel import select

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash


users_router = APIRouter(prefix="/users", tags=["users"])


SECRET_KEY = "9bbf6d44b5ed3f6b6a7856df43fb3852"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 

password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hash.hash(password)


@users_router.get("/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}


def get_user(username: str, session: SessionDep) -> UserInDB:
    try:
        query = select(UserInDB).where(UserInDB.username == username)
        user = session.exec(query).first()
        return user
    except Exception as e:
        raise e



def authenticate_user(username: str, password: str, session: SessionDep):
    user = get_user(username, session)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username, session=session)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@users_router.post("/token")
async def login_for_access_token(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@users_router.get("/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@users_router.put("/register")
async def register_user(new_user: NewUser, session: SessionDep):
    username_taken = get_user(new_user.username, session)
    print(username_taken)
    if username_taken:
        raise HTTPException(status_code=409, detail="Username already taken.")
    user_to_create = UserInDB(
        username=new_user.username,
        disabled=False,
        hashed_password=get_password_hash(new_user.password),
    )
    try:
        session.add(user_to_create)
        session.commit()
        return JSONResponse(content={"data": "User created."}, status_code=200)
    except Exception as e:
        raise e


@users_router.get("/all")
async def get_users(session: SessionDep):
    return session.exec(select(UserInDB)).all()
