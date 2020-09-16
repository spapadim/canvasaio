import unittest

from aioresponses import aioresponses

from canvasaio import Canvas
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestContentExport(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            requires = {
                "course": ["get_by_id", "single_content_export"],
                "group": ["get_by_id", "single_content_export"],
                "user": ["get_by_id", "single_content_export"],
            }
            register_uris(requires, m)

            self.course = await self.canvas.get_course(1)
            self.group = await self.canvas.get_group(1)
            self.user = await self.canvas.get_user(1)

            self.content_export_course = await self.course.get_content_export(11)
            self.content_export_group = await self.group.get_content_export(11)
            self.content_export_user = await self.user.get_content_export(11)

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.content_export_course)
        self.assertIsInstance(string, str)
