import unittest
import datetime
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Selectable

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.schemas.contact import ContactInput
from src.entity.models import Contact
from src.repository.contacts import (
    get_contacts,
    get_contact_by_id,
    get_contacts_by_first_name,
    get_contacts_by_last_name,
    get_contact_by_email,
    create_contact,
    update_contact,
    delete_contact,
    get_contacts_with_upcoming_birthdays
)

class TestContacts(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.mock_db = AsyncMock(spec=AsyncSession)
        self.mock_bind = MagicMock()
        self.mock_async_session = AsyncMock(spec=AsyncSession)
        self.mock_async_session.bind = self.mock_bind

    async def test_get_contacts(self):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            Contact(id=1, first_name="John", last_name="Doe", email="john.doe@example.com", phone_number="1234567890"),
            Contact(id=2, first_name="Jane", last_name="Smith", email="jane.smith@example.com", phone_number="1213123123")
        ]
        self.mock_db.execute.return_value = mock_result

        contacts = await get_contacts(limit=10, offset=0, db=self.mock_db)

        self.assertEqual(len(contacts), 2)
        self.assertEqual(contacts[0].first_name, "John")
        self.assertEqual(contacts[1].last_name, "Smith")
        self.mock_db.execute.assert_called_once()

    async def test_get_contact_by_id(self):
        mock_contact = Contact(id=1, first_name="John", last_name="Doe", email="john.doe@example.com")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_contact
        self.mock_db.execute.return_value = mock_result

        contact_id = 1
        contact = await get_contact_by_id(contact_id, db=self.mock_db)

        self.assertEqual(contact.id, 1)
        self.assertEqual(contact.first_name, "John")
        self.assertEqual(contact.last_name, "Doe")
        self.assertEqual(contact.email, "john.doe@example.com")
        self.mock_db.execute.assert_called_once()
        
    async def test_get_contacts_by_first_name(self):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            Contact(id=1, first_name="John", last_name="Doe", email="john.doe@example.com"),
            Contact(id=2, first_name="John", last_name="Smith", email="john.smith@example.com")
        ]
        self.mock_db.execute.return_value = mock_result

        first_name = "John"
        contacts = await get_contacts_by_first_name(first_name, db=self.mock_db)

        self.assertEqual(len(contacts), 2)
        self.assertEqual(contacts[0].last_name, "Doe")
        self.assertEqual(contacts[1].email, "john.smith@example.com")

        self.mock_db.execute.assert_called_once()
        call_args = self.mock_db.execute.call_args.args
        self.assertIsInstance(call_args[0], Selectable)

        expected_whereclause = select(Contact).filter(Contact.first_name == first_name).compile(dialect=self.mock_bind.dialect)
        actual_whereclause = call_args[0].whereclause.compile(dialect=self.mock_bind.dialect)
        self.assertEqual(actual_whereclause, expected_whereclause)

    async def test_get_contacts_by_last_name(self):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            Contact(id=1, first_name="John", last_name="Doe", email="john.doe@example.com"),
            Contact(id=2, first_name="Jane", last_name="Doe", email="jane.doe@example.com")
        ]
        self.mock_db.execute.return_value = mock_result

        last_name = "Doe"
        contacts = await get_contacts_by_last_name(last_name, db=self.mock_db)

        self.assertEqual(len(contacts), 2)
        self.assertEqual(contacts[0].first_name, "John")
        self.assertEqual(contacts[1].email, "jane.doe@example.com")

        self.mock_db.execute.assert_called_once()
        call_args = self.mock_db.execute.call_args.args
        self.assertIsInstance(call_args[0], Selectable)

        expected_whereclause = select(Contact).filter(Contact.last_name == last_name).compile(dialect=self.mock_bind.dialect)
        actual_whereclause = call_args[0].whereclause.compile(dialect=self.mock_bind.dialect)
        self.assertEqual(actual_whereclause, expected_whereclause)
    
    async def test_get_contact_by_email_found(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = Contact(
            id=1, first_name="John", last_name="Doe", email="john.doe@example.com"
        )
        self.mock_db.execute.return_value = mock_result

        email = "john.doe@example.com"
        contact = await get_contact_by_email(email, db=self.mock_db)

        self.assertIsNotNone(contact)
        self.assertEqual(contact.id, 1)
        self.assertEqual(contact.first_name, "John")
        self.assertEqual(contact.last_name, "Doe")

        self.mock_db.execute.assert_called_once()
        call_args = self.mock_db.execute.call_args.args
        self.assertIsInstance(call_args[0], Selectable)

        expected_whereclause = select(Contact).filter(Contact.email == email).compile(dialect=self.mock_bind.dialect)
        actual_whereclause = call_args[0].whereclause.compile(dialect=self.mock_bind.dialect)
        self.assertEqual(actual_whereclause, expected_whereclause)

    async def test_get_contact_by_email_not_found(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_db.execute.return_value = mock_result

        email = "nonexistent@example.com"
        contact = await get_contact_by_email(email, db=self.mock_db)

        self.assertIsNone(contact)

        self.mock_db.execute.assert_called_once()
        call_args = self.mock_db.execute.call_args.args
        self.assertIsInstance(call_args[0], Selectable)

        expected_whereclause = select(Contact).filter(Contact.email == email).compile(dialect=self.mock_bind.dialect)
        actual_whereclause = call_args[0].whereclause.compile(dialect=self.mock_bind.dialect)
        self.assertEqual(actual_whereclause, expected_whereclause)
    
    async def test_create_contact(self):
        contact_input = ContactInput(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="1234567890",
            birthday=datetime.date(1990, 1, 1)
        )
        user_id = 1
        
        created_contact = await create_contact(contact_input, user_id, self.mock_db)

        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once_with(created_contact)
        
        self.assertEqual(created_contact.first_name, "John")
        self.assertEqual(created_contact.last_name, "Doe")
        self.assertEqual(created_contact.email, "john.doe@example.com")
        self.assertEqual(created_contact.phone_number, "1234567890")
        self.assertEqual(created_contact.birthday, "1990-01-01")
        self.assertEqual(created_contact.user_id, user_id)

    async def test_update_contact(self):
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
        self.mock_db.execute.return_value = mock_result

        contact_update_input = ContactInput(
            first_name="John",
            last_name="Stethem",
            email="john.stethem@example.com",
            phone_number="380331115345",
            birthday=datetime.date(1990, 1, 1)
        )
        
        updated_contact = await update_contact(contact_id, contact_update_input, user_id, self.mock_db)

        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once_with(mock_contact)
        
        self.assertEqual(updated_contact.first_name, "John")
        self.assertEqual(updated_contact.last_name, "Stethem")
        self.assertEqual(updated_contact.email, "john.stethem@example.com")
        self.assertEqual(updated_contact.phone_number, "380331115345")
        self.assertEqual(updated_contact.birthday, "1990-01-01")
        self.assertEqual(updated_contact.user_id, user_id)

    async def test_delete_contact(self):
        mock_contact = Contact(id=1, first_name="John", last_name="Doe", email="john.doe@example.com")
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_contact
        self.mock_db.execute.return_value = mock_result
        
        contact_id = 1
        user_id = 1
        
        contact = await delete_contact(contact_id, user_id, self.mock_db)
        
        self.mock_db.delete.assert_called_once_with(mock_contact)
        self.mock_db.commit.assert_called_once()
        
        self.assertEqual(contact.id, 1)
        self.assertEqual(contact.first_name, "John")
        self.assertEqual(contact.last_name, "Doe")
        self.assertEqual(contact.email, "john.doe@example.com")

    async def test_get_contacts_with_upcoming_birthdays(self):
        today = datetime.date.today()
        upcoming_birthday = today + datetime.timedelta(days=7)
        user_id = 1

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            Contact(id=1, first_name="John", last_name="Doe", email="john.doe@example.com", phone_number="1234567890", birthday=upcoming_birthday, user_id=user_id)
        ]
        self.mock_db.execute.return_value = mock_result

        contacts = await get_contacts_with_upcoming_birthdays(self.mock_db)

        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0].first_name, "John")
        self.assertEqual(contacts[0].last_name, "Doe")
        self.assertEqual(contacts[0].email, "john.doe@example.com")
        self.assertEqual(contacts[0].phone_number, "1234567890")
        self.assertEqual(contacts[0].birthday, upcoming_birthday)
        self.assertEqual(contacts[0].user_id, user_id)

        self.mock_db.execute.assert_called_once()

if __name__ == '__main__':
    unittest.main()
