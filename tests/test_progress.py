import unittest

from aioresponses import aioresponses

from canvasaio.canvas import Canvas
from canvasaio.progress import Progress
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestProgress(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            requires = {
                "course": ["get_by_id", "create_group_category"],
                "group": ["category_assign_members_false"],
            }

            register_uris(requires, m)

            self.course = await self.canvas.get_course(1)
            self.group_category = await self.course.create_group_category("Test String")
            self.progress = await self.group_category.assign_members()

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.progress)
        self.assertIsInstance(string, str)

    # query()
    async def test_query(self, m):
        register_uris({"progress": ["progress_query"]}, m)

        response = await self.progress.query()
        self.assertIsInstance(response, Progress)
