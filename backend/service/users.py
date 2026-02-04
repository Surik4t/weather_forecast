from fastapi import APIRouter

from backend.database.models import User
from backend.database.config import SessionDep
from sqlmodel import select


users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.get("/all")
async def get_list_of_users(session: SessionDep):
    try:
        users_in_db = session.exec(select(User)).all()
        users = [user.username for user in users_in_db]
        return users
    except Exception as e:
        raise e


def create_user(username, session: SessionDep):
    new_user = User(username=username)
    session.add(new_user)
    session.commit()


@users_router.put("/{username}")
async def get_user_id(username, session: SessionDep):
    try:
        query = select(User).where(User.username == username)
        user_in_db = session.exec(query).first()
        if not user_in_db:
            create_user(username, session)
            user_in_db = session.exec(query).first()
        
        return {"user id": user_in_db.id}
    
    except Exception as e:
        raise e

