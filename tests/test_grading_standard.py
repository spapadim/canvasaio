import unittest

from aioresponses import aioresponses

from canvasaio import Canvas
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestGradingStandard(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            register_uris({"course": ["get_by_id", "get_single_grading_standard"]}, m)

            self.course = await self.canvas.get_course(1)
            self.grading_standard = await self.course.get_single_grading_standard(1)

    async def asyncTearDown(self):
        await self.canvas.close()

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.grading_standard)
        self.assertIsInstance(string, str)
