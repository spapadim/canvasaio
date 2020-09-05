import unittest

from aioresponses import aioresponses

from canvasaio import Canvas
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestAuthenticationEvent(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            requires = {
                "account": ["get_by_id", "get_authentication_events"],
                "login": ["create_user_login", "get_authentication_events"],
                "user": ["get_by_id", "get_authentication_events"],
            }
            register_uris(requires, m)

            self.account = await self.canvas.get_account(1)
            self.login = await self.account.create_user_login(
                user={"id": 1}, login={"unique_id": "belieber@example.com"}
            )
            self.user = await self.canvas.get_user(1)

            self.authentication_event_account = (
                await self.account.get_authentication_events()[0]
            )
            self.authentication_event_login = await self.login.get_authentication_events()[0]
            self.authentication_event_user = await self.user.get_authentication_events()[0]

    async def asyncTearDown(self) -> None:
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.authentication_event_account)
        self.assertIsInstance(string, str)
