import unittest

from aioresponses import aioresponses

from canvasaio import Canvas
from canvasaio.authentication_event import AuthenticationEvent
from canvasaio.login import Login
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestLogin(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            register_uris({"account": ["get_by_id"], "login": ["create_user_login"]}, m)

            self.account = await self.canvas.get_account(1)
            self.login = await self.account.create_user_login(
                user={"id": 1}, login={"unique_id": "belieber@example.com"}
            )

    async def asyncTearDown(self) -> None:
        await self.canvas.close()

    # delete()
    async def test_delete_user_login(self, m):
        register_uris({"login": ["delete_user_login"]}, m)

        deleted_user_login = await self.login.delete()

        self.assertIsInstance(deleted_user_login, Login)
        self.assertTrue(hasattr(deleted_user_login, "unique_id"))
        self.assertEqual(deleted_user_login.unique_id, "belieber@example.com")

    # edit()
    async def test_edit_user_login(self, m):
        register_uris({"login": ["edit_user_login"]}, m)

        unique_id = "newemail@example.com"
        edited_user_login = await self.login.edit(
            user={"id": 1}, login={"unique_id": unique_id}
        )

        self.assertIsInstance(edited_user_login, Login)
        self.assertTrue(hasattr(edited_user_login, "unique_id"))
        self.assertEqual(edited_user_login.unique_id, unique_id)

    # __str__()
    def test__str__(self, m):
        string = str(self.login)
        self.assertIsInstance(string, str)

    # get_authentication_events()
    async def test_get_authentication_events(self, m):
        register_uris({"login": ["get_authentication_events"]}, m)

        authentication_event = self.login.get_authentication_events()
        event_list = [event async for event in authentication_event]

        self.assertEqual(len(event_list), 2)

        self.assertIsInstance(event_list[0], AuthenticationEvent)
        self.assertEqual(event_list[0].event_type, "login")
        self.assertEqual(event_list[0].pseudonym_id, 9478)

        self.assertIsInstance(event_list[1], AuthenticationEvent)
        self.assertEqual(event_list[1].created_at, "2012-07-20T15:00:00-06:00")
        self.assertEqual(event_list[1].event_type, "logout")
