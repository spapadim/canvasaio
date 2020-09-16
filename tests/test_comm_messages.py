import unittest

from aioresponses import aioresponses

from canvasaio import Canvas
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestCommMessage(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            requires = {"comm_message": ["comm_messages"]}
            register_uris(requires, m)

            self.comm_message = await self.canvas.get_comm_messages(2)[0]

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.comm_message)
        self.assertIsInstance(string, str)
