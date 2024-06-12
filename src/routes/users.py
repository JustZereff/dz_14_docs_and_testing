import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, File, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_limiter.depends import RateLimiter

from src.repository import users as repository_users
from src.database.db import get_db
from src.schemas.user import UserDb
from src.entity.models import User
from src.services.auth import auth_service
from src.conf.config import config


router = APIRouter(prefix='/user', tags=['users'])


@router.get("/me/", response_model=UserDb, dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_users_me function returns the current user's information.
        ---
        get:
          tags: [users] # This is a tag that can be used to group operations by resources or any other qualifier.
          summary: Returns the current user's information.
          description: Returns the current user's information based on their JWT token in their request header.
          responses: # The possible responses this operation can return, along with descriptions and examples of each response type (if applicable).
            &quot;200&quot;:  # HTTP status code 200 indicates success! In this case, it means we successfully returned a User
    
    :param current_user: User: Get the current user
    :return: The current user object
    :doc-author: Trelent
    """
    return current_user

@router.patch('/avatar', response_model=UserDb, dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def update_avatar_user(file: UploadFile = File(), 
                             current_user: User = Depends(auth_service.get_current_user),
                             db: AsyncSession = Depends(get_db)
                             ):
    """
    The update_avatar_user function updates the avatar of a user.
        Args:
            file (UploadFile): The image to be uploaded.
            current_user (User): The user whose avatar is being updated. 
                                 This is obtained from the auth_service module's get_current_user function, which returns 
                                 an object containing information about the currently logged in user, including their email address and username.
    
    :param file: UploadFile: Get the file from the request body
    :param current_user: User: Get the current user from the database
    :param db: AsyncSession: Get the database session
    :return: A user object
    :doc-author: Trelent
    """
    cloudinary.config(
        cloud_name=config.CLD_NAME,
        api_key=config.CLD_API_KEY,
        api_secret=config.CLD_API_SECRET,
        secure=True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f'UsersApp/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'UsersApp/{current_user.username}')\
                        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user