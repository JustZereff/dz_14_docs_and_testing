from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.sql import func
from src.schemas.contact import ContactInput
from src.entity.models import Contact
from datetime import date, datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_contacts(limit: int, offset: int, db: AsyncSession):
    """
    The get_contacts function returns a list of contacts from the database.
    
    :param limit: int: Limit the number of contacts returned
    :param offset: int: Determine where to start the query from
    :param db: AsyncSession: Pass the database connection to the function
    :return: A list of contact objects
    :doc-author: Trelent
    """
    stmt = select(Contact).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()

async def get_contact_by_id(contact_id: int, db: AsyncSession):
    """
    The get_contact_by_id function returns a contact object from the database.
    
    :param contact_id: int: Specify the id of the contact we want to retrieve
    :param db: AsyncSession: Pass in the database session
    :return: A contact object that has all the data from the database
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()

async def get_contacts_by_first_name(first_name: str, db: AsyncSession):
    """
    The get_contacts_by_first_name function returns a list of contacts with the given first name.
    
    :param first_name: str: Specify the first name of the contact that we want to retrieve from our database
    :param db: AsyncSession: Pass in the database session
    :return: A list of contact objects
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(first_name=first_name)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()

async def get_contacts_by_last_name(last_name: str, db: AsyncSession):
    """
    The get_contacts_by_last_name function returns a list of contacts with the given last name.
    
    :param last_name: str: Filter the contacts by last name
    :param db: AsyncSession: Pass in the database session
    :return: A list of contact objects
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(last_name=last_name)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()

async def get_contact_by_email(email: str, db: AsyncSession):
    """
    The get_contact_by_email function returns a contact object from the database.
        Args:
            email (str): The email address of the contact to be retrieved.
            db (AsyncSession): An async session for interacting with the database.
        Returns:
            Contact: A single contact object matching the provided email address, or None if no match is found.
    
    :param email: str: Filter the results by email
    :param db: AsyncSession: Pass the database session to the function
    :return: A single contact
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(email=email)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactInput, user_id: int, db: AsyncSession):
    """
    The create_contact function creates a new contact in the database.
    
    :param body: ContactInput: Get the data from the request body
    :param user_id: int: Specify the user who created the contact
    :param db: AsyncSession: Pass the database session to the function
    :return: A contact object
    :doc-author: Trelent
    """
    contact_data = body.model_dump(exclude_unset=True)
    
    # Преобразование даты в строку, если поле birthday существует
    if 'birthday' in contact_data and isinstance(contact_data['birthday'], date):
        contact_data['birthday'] = contact_data['birthday'].strftime('%Y-%m-%d')
        
    contact = Contact(**contact_data, user_id=user_id)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact



async def update_contact(contact_id: int, body: ContactInput, user_id: int, db: AsyncSession):
    """
    The update_contact function updates a contact in the database.

    :param contact_id: int: Identify the contact to be updated
    :param body: ContactInput: Get the data from the request body
    :param user_id: int: Ensure that the user is only able to update their own contacts
    :param db: AsyncSession: Pass the database session to the function
    :return: The updated contact or None if not found
    :doc-author: Trelent
    """
    contact_data = body.model_dump(exclude_unset=True)

    # Преобразование даты в строку, если поле birthday существует
    if 'birthday' in contact_data and isinstance(contact_data['birthday'], date):
        contact_data['birthday'] = contact_data['birthday'].strftime('%Y-%m-%d')

    stmt = select(Contact).filter_by(id=contact_id, user_id=user_id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if not contact:
        return None
    for key, value in contact_data.items():
        setattr(contact, key, value)
    await db.commit()
    await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, user_id: int, db: AsyncSession):
    """
    The delete_contact function deletes a contact from the database.
    
    :param contact_id: int: Specify the id of the contact to delete
    :param user_id: int: Ensure that the user is only deleting their own contacts
    :param db: AsyncSession: Pass in the database connection
    :return: A contact object
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id, user_id=user_id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if not contact:
        return None
    await db.delete(contact)
    await db.commit()
    return contact

async def get_contacts_with_upcoming_birthdays(db: AsyncSession):
    """
    The get_contacts_with_upcoming_birthdays function returns a list of contacts with birthdays in the next 7 days.
    
    :param db: AsyncSession: Pass the database connection to the function
    :return: A list of contacts with upcoming birthdays
    :doc-author: Trelent
    """
    current_date = datetime.now().date()
    one_week_later = current_date + timedelta(days=7)
    
    # Получаем всех контактов
    stmt = select(Contact).filter(Contact.birthday != None)
    result = await db.execute(stmt)
    contacts = result.scalars().all()

    upcoming_birthdays = []
    for contact in contacts:
        if isinstance(contact.birthday, str):
            birthday = datetime.strptime(contact.birthday, '%Y-%m-%d').date()
        else:
            birthday = contact.birthday
        birthday_this_year = birthday.replace(year=current_date.year)
        days_until_birthday = (birthday_this_year - current_date).days
        if 0 <= days_until_birthday <= 7:
            upcoming_birthdays.append(contact)

    return upcoming_birthdays
