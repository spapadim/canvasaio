import unittest

from aioresponses import aioresponses

from canvasaio import Canvas
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestExternalFeed(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            register_uris({"course": ["get_by_id", "list_external_feeds"]}, m)

            self.course = await self.canvas.get_course(1)
            self.external_feed = await self.course.get_external_feeds()[0]

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.external_feed)
        self.assertIsInstance(string, str)
