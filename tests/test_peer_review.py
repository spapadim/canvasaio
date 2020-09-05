import unittest

from aioresponses import aioresponses

from canvasaio.canvas import Canvas
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestPeerReview(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            requires = {
                "course": ["get_by_id", "get_assignment_by_id"],
                "assignment": ["list_peer_reviews"],
            }

            register_uris(requires, m)

            self.course = await self.canvas.get_course(1)
            self.assignment = await self.course.get_assignment(1)
            self.peer_reviews = [
                peer_review async for peer_review in self.assignment.get_peer_reviews()
            ]

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.peer_reviews[0])
        self.assertIsInstance(string, str)
