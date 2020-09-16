import unittest

from aioresponses import aioresponses

from canvasaio import Canvas
from canvasaio.course_epub_export import CourseEpubExport
from tests import settings
from tests.util import aioresponse_mock


@aioresponse_mock
class TestCourseEpubExport(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        self.course_epub_export = CourseEpubExport(
            self.canvas._Canvas__requester,
            {
                "name": "course1",
                "id": 1,
                "epub_export": {
                    "id": 1,
                    "created_at": "2019-01-01T00:00:00Z",
                    "progress_url": "https://dummyurl.com/api/v1/progress/4",
                    "user_id": 4,
                    "workflow_state": "exported",
                },
            },
        )

    async def asyncTearDown(self):
        await self.canvas.close()

    def test_str(self, m):
        test_str = str(self.course_epub_export)
        self.assertIsInstance(test_str, str)
