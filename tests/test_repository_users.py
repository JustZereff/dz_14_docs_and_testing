import unittest
import datetime
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Selectable

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.schemas.user import TokenSchema, UserModel, UserDb, UserResponse, RequestEmail
from src.entity.models import User
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    verification_email,
    update_avatar,
)

from pydantic import RootModel

class AnyObject(RootModel):
    root: object

    def __eq__(self, other):
        return True

class TestUsers(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.mock_db = AsyncMock(spec=AsyncSession)
        self.mock_bind = MagicMock()
        self.mock_async_session = AsyncMock(spec=AsyncSession)
        self.mock_async_session.bind = self.mock_bind

    async def test_get_user_by_email_found(self):
        today = datetime.datetime.now()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = User(
            id=1,
            username="qwerty",
            email="qwerty@bk.ua",
            password="$2b$12$CfVMCPjurea16J.NCE2VdO2ep8XoyG8cfoy7442NElqKy8mQ27KGe",
            avatar="https://res.cloudinary.com/dcysgyad7/image/upload/c_fill,h_250,w_250/v1718066657/UsersApp/qwerty",
            verification=True,
            refresh_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJxd2VydHlAYmsudWEiLCJpYXQiOjE3MTgwNjY2MTYsImV4cCI6MTcxODY3MTQxNiwic2NvcGUiOiJyZWZyZXNoX3Rva2VuIn0.fJV2kXIlEc_g83jaL2R6FlEMivI8nCvaHKutSbIxlWM",
            created_at=today,
            updated_at=today
        )
        self.mock_db.execute.return_value = mock_result

        email = "qwerty@bk.ua"
        user = await get_user_by_email(email, db=self.mock_db)

        self.assertIsNotNone(user)
        self.assertEqual(user.id, 1)
        self.assertEqual(user.username, "qwerty")
        self.assertEqual(user.email, "qwerty@bk.ua")
        self.assertEqual(user.password, '$2b$12$CfVMCPjurea16J.NCE2VdO2ep8XoyG8cfoy7442NElqKy8mQ27KGe')
        self.assertEqual(user.avatar, "https://res.cloudinary.com/dcysgyad7/image/upload/c_fill,h_250,w_250/v1718066657/UsersApp/qwerty")
        self.assertEqual(user.verification, True)
        self.assertEqual(user.refresh_token, "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJxd2VydHlAYmsudWEiLCJpYXQiOjE3MTgwNjY2MTYsImV4cCI6MTcxODY3MTQxNiwic2NvcGUiOiJyZWZyZXNoX3Rva2VuIn0.fJV2kXIlEc_g83jaL2R6FlEMivI8nCvaHKutSbIxlWM")
        self.assertEqual(user.created_at, today)
        self.assertEqual(user.updated_at, today)

        self.mock_db.execute.assert_called_once()
        call_args = self.mock_db.execute.call_args.args
        self.assertIsInstance(call_args[0], Selectable)

        expected_whereclause = select(User).filter(User.email == email).compile(dialect=self.mock_bind.dialect)
        actual_whereclause = call_args[0].whereclause.compile(dialect=self.mock_bind.dialect)
        self.assertEqual(actual_whereclause, expected_whereclause)

    async def test_get_user_by_email_not_found(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_db.execute.return_value = mock_result

        email = "nonexistent@example.com"
        user = await get_user_by_email(email, db=self.mock_db)

        self.assertIsNone(user)

        self.mock_db.execute.assert_called_once()
        call_args = self.mock_db.execute.call_args.args
        self.assertIsInstance(call_args[0], Selectable)

        expected_whereclause = select(User).filter(User.email == email).compile(dialect=self.mock_bind.dialect)
        actual_whereclause = call_args[0].whereclause.compile(dialect=self.mock_bind.dialect)
        self.assertEqual(actual_whereclause, expected_whereclause)

    async def test_create_user(self):
        # Создаем экземпляр данных пользователя
        # user_input = {
        #     "username": "Artem",
        #     "email": "artem.denysenko1445@gmail.com",
        #     "password": "qweqwe123"
        # }

        # response = await create_user(user_input, self.mock_db)

        # self.assertIn("user", response)
        # self.assertIn("detail", response)

        # # Проверяем данные пользователя
        # created_user = response["user"]
        # self.assertEqual(created_user["username"], "Artem")
        # self.assertEqual(created_user["email"], "artem.denysenko1445@gmail.com")
        # self.assertEqual(created_user["verification"], False)  # Проверьте соответствующее поле
        # self.assertIsInstance(created_user["id"], int)
        # self.assertIsInstance(created_user["created_at"], str)
        # self.assertEqual(created_user["avatar"], "https://www.gravatar.com/avatar/46ed56cde9cd2573a63ddce0c676df1e")

        # # Проверяем детальное сообщение
        # self.assertEqual(response["detail"], "User successfully created")

        # self.mock_db.add.assert_called_once()
        # self.mock_db.commit.assert_called_once()
        # self.mock_db.refresh.assert_called_once_with(AnyObject(root=object))
        pass

    async def test_update_token(self):
        today = datetime.datetime.now()
        mock_user = User(
            id=1,
            username="qwerty",
            email="qwerty@bk.ua",
            password="$2b$12$CfVMCPjurea16J.NCE2VdO2ep8XoyG8cfoy7442NElqKy8mQ27KGe",
            avatar="https://res.cloudinary.com/dcysgyad7/image/upload/c_fill,h_250,w_250/v1718066657/UsersApp/qwerty",
            verification=True,
            refresh_token="old_token",
            created_at=today,
            updated_at=today
        )

        token = "new_token"
        await update_token(mock_user, token, self.mock_db)

        self.assertEqual(mock_user.refresh_token, token)
        self.mock_db.commit.assert_called_once()

    async def test_verification_email(self):
        today = datetime.datetime.now()
        mock_user = User(
            id=1,
            username="qwerty",
            email="qwerty@bk.ua",
            password="$2b$12$CfVMCPjurea16J.NCE2VdO2ep8XoyG8cfoy7442NElqKy8mQ27KGe",
            avatar="https://res.cloudinary.com/dcysgyad7/image/upload/c_fill,h_250,w_250/v1718066657/UsersApp/qwerty",
            verification=False,
            refresh_token="old_token",
            created_at=today,
            updated_at=today
        )
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        self.mock_db.execute.return_value = mock_result

        email = "qwerty@bk.ua"
        await verification_email(email, self.mock_db)

        self.assertTrue(mock_user.verification)
        self.mock_db.commit.assert_called_once()

    async def test_update_avatar(self):
        today = datetime.datetime.now()
        mock_user = User(
            id=1,
            username="qwerty",
            email="qwerty@bk.ua",
            password="$2b$12$CfVMCPjurea16J.NCE2VdO2ep8XoyG8cfoy7442NElqKy8mQ27KGe",
            avatar="old_avatar",
            verification=True,
            refresh_token="old_token",
            created_at=today,
            updated_at=today
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        self.mock_db.execute.return_value = mock_result

        new_avatar_url = "https://new.avatar.url"
        updated_user = await update_avatar(mock_user.email, new_avatar_url, self.mock_db)

        self.assertEqual(updated_user.avatar, new_avatar_url)
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once_with(mock_user)

if __name__ == '__main__':
    unittest.main()
