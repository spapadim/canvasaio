import unittest

from aioresponses import aioresponses

from canvasaio import Canvas
from canvasaio.bookmark import Bookmark
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestBookmark(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            register_uris(
                {"bookmark": ["get_bookmark"], "current_user": ["get_by_id"]}, m
            )

            self.user = await self.canvas.get_current_user()
            self.bookmark = await self.user.get_bookmark(45)

    async def asyncTearDown(self):
        await self.canvas.close()

    # delete()
    async def test_delete_bookmark(self, m):
        register_uris({"bookmark": ["delete_bookmark"]}, m)

        deleted_bookmark = await self.bookmark.delete()

        self.assertIsInstance(deleted_bookmark, Bookmark)
        self.assertTrue(hasattr(deleted_bookmark, "name"))
        self.assertEqual(deleted_bookmark.name, "Test Bookmark 3")

    # edit()
    async def test_edit_bookmark(self, m):
        register_uris({"bookmark": ["edit_bookmark"]}, m)

        name = "New Name"
        url = "http//happy-place.com"
        edited_bookmark = await self.bookmark.edit(name=name, url=url)

        self.assertIsInstance(edited_bookmark, Bookmark)
        self.assertTrue(hasattr(edited_bookmark, "name"))
        self.assertEqual(edited_bookmark.name, name)

    # __str__()
    def test__str__(self, m):
        string = str(self.bookmark)
        self.assertIsInstance(string, str)
