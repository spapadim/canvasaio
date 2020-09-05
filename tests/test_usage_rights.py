import unittest

from aioresponses import aioresponses

from canvasaio import Canvas
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestUsageRights(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            requires = {"user": ["get_by_id", "set_usage_rights"]}

            register_uris(requires, m)

            self.user = await self.canvas.get_user(1)
            self.usage_rights = await self.user.set_usage_rights(
                file_ids=[1, 2], usage_rights={"use_justification": "fair_use"}
            )

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.usage_rights)
        self.assertIsInstance(string, str)
