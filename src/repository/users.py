from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from libgravatar import Gravatar
from src.database.db import get_db
from src.entity.models import User
from src.schemas.user import UserModel, UserDb
import logging

logger = logging.getLogger(__name__)

async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """
    The get_user_by_email function returns a user object from the database based on the email address provided.
        If no user is found, None is returned.
    
    :param email: str: Pass the email of the user to be retrieved
    :param db: AsyncSession: Pass in the database session
    :return: A single user object
    :doc-author: Trelent
    """
    stmt = select(User).filter_by(email=email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    return user

async def create_user(body: UserDb, db: AsyncSession = Depends(get_db)):
    """
    The create_user function creates a new user in the database.
    
    :param body: UserDb: Create a new user
    :param db: AsyncSession: Pass in the database session
    :return: A user object
    :doc-author: Trelent
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        logger.error(f"Error getting avatar: {err}")
    
    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
    
async def update_token(user: User, token: str, db: AsyncSession):
    """
    The update_token function updates the refresh token for a user.
    
    :param user: User: Specify the user that will be updated
    :param token: str: Update the user's refresh_token in the database
    :param db: AsyncSession: Pass the database connection to the function
    :return: A coroutine object that is not awaited
    :doc-author: Trelent
    """
    user.refresh_token = token
    await db.commit()
    
async def verification_email(email: str, db: AsyncSession) -> None:
    """
    The verification_email function is used to verify a user's email address.
        Args:
            email (str): The user's email address.
            db (AsyncSession): An async database session object.
    
    :param email: str: Get the email of a user
    :param db: AsyncSession: Pass the database session to the function
    :return: None
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.verification = True
    await db.commit()

async def update_avatar(email, url: str, db: AsyncSession) -> User:
    """
    The update_avatar function updates the avatar of a user.
    
    
    :param email: Get the user from the database
    :param url: str: Specify the type of data that is being passed into the function
    :param db: AsyncSession: Pass in the database session to be used
    :return: A user object, which is the same as what get_user_by_email returns
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user