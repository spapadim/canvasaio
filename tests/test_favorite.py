import unittest

from aioresponses import aioresponses

from canvasaio import Canvas
from canvasaio.favorite import Favorite
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestFavorite(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            requires = {
                "current_user": [
                    "add_favorite_course",
                    "add_favorite_group",
                    "get_by_id",
                ]
            }
            register_uris(requires, m)

            self.user = await self.canvas.get_current_user()
            self.favorite_course = await self.user.add_favorite_course(1)
            self.favorite_group = await self.user.add_favorite_group(1)

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.favorite_course)
        self.assertIsInstance(string, str)

        string = str(self.favorite_group)
        self.assertIsInstance(string, str)

    # remove()
    async def test_remove_favorite_course(self, m):
        register_uris({"current_user": ["remove_favorite_course"]}, m)

        evnt = await self.favorite_course.remove()
        self.assertIsInstance(evnt, Favorite)
        self.assertEqual(evnt.context_type, "course")
        self.assertEqual(evnt.context_id, 1)

    async def test_remove_favorite_group(self, m):
        register_uris({"current_user": ["remove_favorite_group"]}, m)

        evnt = await self.favorite_group.remove()
        self.assertIsInstance(evnt, Favorite)
        self.assertEqual(evnt.context_type, "group")
        self.assertEqual(evnt.context_id, 1)
