from fastapi import APIRouter, Depends, HTTPException, Security, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from src.repository import users as repository_users
from src.database.db import get_db
from src.schemas.user import UserModel, UserResponse, TokenSchema, RequestEmail
from src.services.auth import auth_service
from src.services.verification import send_email
import logging

router = APIRouter(prefix='/auth', tags=['auth'])

logger = logging.getLogger(__name__)

@router.post(path="/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, bt: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    """
    The signup function creates a new user in the database.
    
    :param body: UserModel: Get the data from the request body
    :param bt: BackgroundTasks: Send an email in the background
    :param request: Request: Get the base_url of the request
    :param db: AsyncSession: Get the database connection
    :return: A dictionary with the user and a detail message
    :doc-author: Trelent
    """
    logger.info("Checking if user exists")
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        logger.info("User already exists")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    logger.info("Creating new user")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    logger.info("New user created, sending email")
    # Send email
    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    logger.info("Email sent")
    return {"user": new_user, "detail": "User successfully created"}

@router.post("/login", response_model=TokenSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    The login function is used to authenticate a user.
    
    :param body: OAuth2PasswordRequestForm: Get the username and password from the request body
    :param db: AsyncSession: Get the database session
    :return: A dictionary with access_token, refresh_token and token_type
    :doc-author: Trelent
    """
    logger.info("Logging in user")
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        logger.info("Invalid email")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.verification:
        logger.info("Email not verified")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not verification")
    if not auth_service.verify_password(body.password, user.password):
        logger.info("Invalid password")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    logger.info("User logged in")
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get('/refresh_token', response_model=TokenSchema)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(), db: AsyncSession = Depends(get_db)):
    """
    The refresh_token function is used to refresh the access token.
    
    :param credentials: HTTPAuthorizationCredentials: Get the token from the request header
    :param db: AsyncSession: Get the database session
    :return: A dictionary with the access_token, refresh_token and token type
    :doc-author: Trelent
    """
    logger.info("Refreshing token")
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        logger.info("Invalid refresh token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    logger.info("Token refreshed")
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    The confirmed_email function is used to confirm a user's email address.
        It takes the token from the URL and uses it to get the user's email address.
        Then, it checks if that user exists in our database, and if they do exist, 
        then we check whether or not their verification status is True (meaning they have already confirmed their email).
         If so, we return a message saying that their email has already been confirmed. Otherwise, 
         we call our repository_users function called verification_email which sets the value of &quot;verification&quot; for this particular user to True.
    
    :param token: str: Get the token from the url
    :param db: AsyncSession: Pass the database session to the function
    :return: A dictionary with the message key and a string value
    :doc-author: Trelent
    """
    logger.info("Confirming email")
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        logger.info("Verification error: user not found")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.verification:
        logger.info("Email already confirmed")
        return {"message": "Your email is already confirmed"}
    await repository_users.verification_email(email, db)
    logger.info("Email confirmed")
    return {"message": "Email confirmed"}

@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)):
    """
    The request_email function is used to send an email to the user with a link that will verify their account.
        The function takes in a RequestEmail object, which contains the email of the user who wants to verify their account.
        It then checks if they are already verified and returns an error message if so. If not, it sends them an email with 
        a link that will allow them to verify their account.
    
    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base_url of the server
    :param db: AsyncSession: Get the database session
    :return: A dictionary with a message
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user.verification:
        return {"message": "Your email is already verification"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}