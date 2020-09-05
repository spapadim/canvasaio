import unittest

from aioresponses import aioresponses

from canvasaio import Canvas
from canvasaio.authentication_provider import AuthenticationProvider
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestAuthenticationProvider(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            register_uris({"account": ["get_by_id", "add_authentication_providers"]}, m)

            self.account = await self.canvas.get_account(1)
            self.authentication_providers = await self.account.add_authentication_providers(
                authentication_providers={"auth_type": "Authentication Providers"}
            )

    async def asyncTearDown(self) -> None:
        await self.canvas.close()

    # update()
    async def test_update_authentication_providers(self, m):
        register_uris(
            {"authentication_providers": ["update_authentication_providers"]}, m
        )

        new_auth_type = "New Authentication Providers"

        await self.authentication_providers.update(
            authentication_providers={"auth_type": new_auth_type}
        )
        self.assertEqual(self.authentication_providers.auth_type, new_auth_type)

    # delete()
    async def test_delete_authentication_providers(self, m):
        register_uris(
            {"authentication_providers": ["delete_authentication_providers"]}, m
        )

        deleted_authentication_providers = await self.authentication_providers.delete()

        self.assertIsInstance(deleted_authentication_providers, AuthenticationProvider)
        self.assertTrue(hasattr(deleted_authentication_providers, "auth_type"))
        self.assertEqual(
            deleted_authentication_providers.auth_type, "Authentication Providers"
        )

    # __str__()
    def test_str__(self, m):
        string = str(self.authentication_providers)
        self.assertIsInstance(string, str)
