from fastapi import APIRouter, Query, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.repository import contacts as repositories_contact
from src.database.db import get_db
from src.schemas.contact import ContactInput, ContactOutput
from src.entity.models import User
from src.services.auth import auth_service
from fastapi_limiter.depends import RateLimiter

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(prefix='/contacts', tags=['contact'])

@router.get(path='/', response_model=list[ContactOutput], dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def get_contacts(limit: int = Query(default=10, ge=10, le=500), offset: int = Query(default=0), db: AsyncSession = Depends(get_db)):
    """
    The get_contacts function returns a list of contacts.
        The limit and offset parameters are used to paginate the results.
    
    
    :param limit: int: Set the limit of contacts to return
    :param ge: Specify that the limit must be greater than or equal to 10
    :param le: Limit the number of contacts returned
    :param offset: int: Specify the number of records to skip before returning results
    :param db: AsyncSession: Get the database session
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repositories_contact.get_contacts(limit, offset, db)
    return contacts

@router.get(path='/id/{contact_id}', response_model=ContactOutput, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def get_contacts_by_id(contact_id: int, db: AsyncSession = Depends(get_db)):
    """
    The get_contacts_by_id function returns a contact by its id.
    
    :param contact_id: int: Specify the contact id to be retrieved
    :param db: AsyncSession: Pass the database session to the function
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repositories_contact.get_contact_by_id(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found!')
    return contact

@router.get(path='/first_name/{first_name}', response_model=list[ContactOutput])
async def get_contacts_by_first_name(first_name: str, db: AsyncSession = Depends(get_db)):
    """
    The get_contacts_by_first_name function returns a list of contacts with the given first name.
        If no contact is found, an HTTP 404 error is raised.
    
    :param first_name: str: Get the first name from the url
    :param db: AsyncSession: Pass the database session into the function
    :return: A list of contacts, but the schema expects a single contact
    :doc-author: Trelent
    """
    contacts = await repositories_contact.get_contacts_by_first_name(first_name, db)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found!')
    return contacts

@router.get(path='/last_name/{last_name}', response_model=list[ContactOutput], dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def get_contacts_by_last_name(last_name: str, db: AsyncSession = Depends(get_db)):
    """
    The get_contacts_by_last_name function returns a list of contacts with the specified last name.
        If no contact is found, an HTTP 404 Not Found error is raised.
    
    :param last_name: str: Pass the last name of a contact to the function
    :param db: AsyncSession: Pass the database connection to the function
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repositories_contact.get_contacts_by_last_name(last_name, db)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found!')
    return contacts

@router.get(path='/email/{email}', response_model=ContactOutput, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def get_contacts_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """
    The get_contacts_by_email function returns a contact by email.
    
    :param email: str: Get the email from the url
    :param db: AsyncSession: Pass the database session to the function
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repositories_contact.get_contact_by_email(email, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found!')
    return contact

@router.post('/', response_model=ContactOutput, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def create_contact(body: ContactInput, db: AsyncSession = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    The create_contact function creates a new contact in the database.
        The function takes a ContactInput object as input, which is defined in the models/contact.py file.
        The function also takes an optional db parameter, which is used to connect to the database and create a new contact record.
    
    :param body: ContactInput: Validate the data sent in the request body
    :param db: AsyncSession: Pass the database session to the function
    :param current_user: User: Get the current user from the database
    :return: A contact object
    :doc-author: Trelent
    """
    try:
        contact = await repositories_contact.create_contact(body, current_user.id, db)
        logger.info("Creating contact")
        return contact
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not authorized!')
    finally:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not authorized!')

@router.put('/id/{contact_id}', response_model=ContactOutput)
async def update_contact(contact_id: int, body: ContactInput, db: AsyncSession = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    The update_contact function updates a contact in the database.
        Args:
            contact_id (int): The id of the contact to update.
            body (ContactInput): The updated information for the specified Contact.
        Returns:
            Contact: A dictionary containing all of the information for a specific Contact.
    
    :param contact_id: int: Get the contact id from the url
    :param body: ContactInput: Pass the data to the update_contact function
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user from the auth_service
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repositories_contact.update_contact(contact_id, body, current_user.id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found or not authorized!')
    return contact

@router.delete('/id/{contact_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    The delete_contact function deletes a contact from the database.
        Args:
            contact_id (int): The id of the contact to delete.
            db (AsyncSession, optional): An async session object for interacting with the database. Defaults to Depends(get_db).
            current_user (User, optional): A user object representing the currently logged in user. Defaults to Depends(auth_service.get_current_user).
    
    :param contact_id: int: Specify the id of the contact to be deleted
    :param db: AsyncSession: Get the database session from the dependency injection
    :param current_user: User: Get the current user information from the database
    :return: A dictionary with a detail key
    :doc-author: Trelent
    """
    contact = await repositories_contact.delete_contact(contact_id, current_user.id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found or not authorized!')
    return {"detail": "Contact deleted successfully"}

@router.get(path='/birthday/next_week', response_model=list[ContactOutput])
async def get_contacts_with_upcoming_birthdays(db: AsyncSession = Depends(get_db)):
    """
    The get_contacts_with_upcoming_birthdays function returns a list of contacts with upcoming birthdays.
        The function uses the get_contacts_with_upcoming_birthdays function from the repositories/contact.py file to query
        for contacts with upcoming birthdays and then returns those results.
    
    :param db: AsyncSession: Pass the database session into the function
    :return: A list of contacts with upcoming birthdays
    :doc-author: Trelent
    """
    contacts = await repositories_contact.get_contacts_with_upcoming_birthdays(db)
    return contacts
