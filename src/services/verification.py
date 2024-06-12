from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.conf.config import config


conf = ConnectionConfig(
    MAIL_USERNAME=config.mail_username,
    MAIL_PASSWORD=config.mail_password,
    MAIL_FROM=config.mail_from,
    MAIL_PORT=config.mail_port,
    MAIL_SERVER=config.mail_server,
    MAIL_FROM_NAME="Address compani",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)

async def send_email(email: EmailStr, username: str, host: str):
    """
    The send_email function sends an email to the user with a link to verify their account.
        Args:
            email (str): The user's email address.
            username (str): The username of the new account being created.
            host (str): The hostname of the server where this function is running.
    
    :param email: EmailStr: Validate the email address
    :param username: str: Pass the username to the template
    :param host: str: Pass the host name of the server to the template
    :return: A coroutine object
    :doc-author: Trelent
    """
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="varify_email.html")
    except ConnectionErrors as err:
        print(err)