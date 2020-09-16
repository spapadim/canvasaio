import unittest

from aioresponses import aioresponses

from canvasaio import Canvas
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestLicenses(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            requires = {"user": ["get_by_id", "get_licenses"]}

            register_uris(requires, m)

            self.user = await self.canvas.get_user(1)
            self.licenses = [lic async for lic in self.user.get_licenses()]

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.licenses[0])
        self.assertIsInstance(string, str)
