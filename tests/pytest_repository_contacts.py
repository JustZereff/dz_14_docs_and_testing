import pytest
import datetime
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.schemas.contact import ContactInput
from src.entity.models import Contact
from src.repository.contacts import (
    get_contacts,
    get_contact_by_id,
    create_contact,
    update_contact
)

@pytest.fixture
def mock_db():
    return AsyncMock(spec=AsyncSession)

@pytest.mark.asyncio
async def test_get_contacts(mock_db):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        Contact(id=1, first_name="John", last_name="Doe", email="john.doe@example.com", phone_number="1234567890"),
        Contact(id=2, first_name="Jane", last_name="Smith", email="jane.smith@example.com", phone_number="1213123123")
    ]
    mock_db.execute.return_value = mock_result

    contacts = await get_contacts(limit=10, offset=0, db=mock_db)

    assert len(contacts) == 2
    assert contacts[0].first_name == "John"
    assert contacts[1].last_name == "Smith"
    mock_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_contact_by_id(mock_db):
    mock_contact = Contact(id=1, first_name="John", last_name="Doe", email="john.doe@example.com")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_contact
    mock_db.execute.return_value = mock_result

    contact_id = 1
    contact = await get_contact_by_id(contact_id, db=mock_db)

    assert contact.id == 1
    assert contact.first_name == "John"
    assert contact.last_name == "Doe"
    assert contact.email == "john.doe@example.com"
    mock_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_create_contact(mock_db):
    contact_input = ContactInput(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="1234567890",
        birthday=datetime.date(1990, 1, 1)
    )
    user_id = 1
    
    created_contact = await create_contact(contact_input, user_id, mock_db)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(created_contact)
    
    assert created_contact.first_name == "John"
    assert created_contact.last_name == "Doe"
    assert created_contact.email == "john.doe@example.com"
    assert created_contact.phone_number == "1234567890"
    assert created_contact.birthday == "1990-01-01"
    assert created_contact.user_id == user_id

@pytest.mark.asyncio
async def test_update_contact(mock_db):
    user_id = 1
    contact_id = 1

    mock_contact = Contact(
        id=contact_id, 
        first_name="John", 
        last_name="Doe", 
        email="john.doe@example.com",
        phone_number="1234567890", 
        birthday="1990-01-01", 
        user_id=user_id
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_contact
    mock_db.execute.return_value = mock_result

    contact_update_input = ContactInput(
        first_name="John",
        last_name="Stethem",
        email="john.stethem@example.com",
        phone_number="380331115345",
        birthday=datetime.date(1990, 1, 1)
    )
    
    updated_contact = await update_contact(contact_id, contact_update_input, user_id, mock_db)

    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_contact)
    
    assert updated_contact.first_name == "John"
    assert updated_contact.last_name == "Stethem"
    assert updated_contact.email == "john.stethem@example.com"
    assert updated_contact.phone_number == "380331115345"
    assert updated_contact.birthday == "1990-01-01"
    assert updated_contact.user_id == user_id
