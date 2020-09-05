import unittest

from aioresponses import aioresponses

from canvasaio import Canvas
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestPageView(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            register_uris({"user": ["get_by_id", "page_views", "page_views_p2"]}, m)

            self.user = await self.canvas.get_user(1)
            pageviews = self.user.get_page_views()
            self.pageview = await pageviews[0]

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.pageview)
        self.assertIsInstance(string, str)
