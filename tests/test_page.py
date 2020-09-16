import unittest

from aioresponses import aioresponses

from canvasaio.canvas import Canvas
from canvasaio.course import Course
from canvasaio.group import Group
from canvasaio.page import Page, PageRevision
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestPage(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):

        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            requires = {
                "course": ["get_by_id"],
                "group": ["get_by_id", "pages_get_page"],
                "page": ["get_page"],
            }
            register_uris(requires, m)

            self.course = await self.canvas.get_course(1)
            self.group = await self.canvas.get_group(1)
            self.page_course = await self.course.get_page("my-url")
            self.page_group = await self.group.get_page("my-url")

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.page_course)
        self.assertIsInstance(string, str)

    async def test_edit(self, m):
        register_uris({"page": ["edit"]}, m)

        new_title = "New Page"
        await self.page_course.edit(page={"title": new_title})

        self.assertIsInstance(self.page_course, Page)
        self.assertTrue(hasattr(self.page_course, "title"))
        self.assertEqual(self.page_course.title, new_title)

    async def test_delete(self, m):
        register_uris({"page": ["delete_page"]}, m)

        page = self.page_course
        deleted_page = await page.delete()

        self.assertIsInstance(deleted_page, Page)

    # get_revisions()
    async def test_get_revisions(self, m):
        register_uris({"page": ["list_revisions", "list_revisions2"]}, m)

        revisions = self.page_course.get_revisions()
        rev_list = [rev async for rev in revisions]

        self.assertEqual(len(rev_list), 4)
        self.assertIsInstance(rev_list[0], PageRevision)

    async def test_show_latest_revision(self, m):
        register_uris({"page": ["latest_revision"]}, m)

        revision = await self.page_course.show_latest_revision()

        self.assertIsInstance(revision, PageRevision)

    async def test_get_revision_by_id_course(self, m):
        register_uris({"page": ["get_latest_rev_by_id"]}, m)

        revision_by_id = await self.page_course.get_revision_by_id(2)
        self.assertIsInstance(revision_by_id, PageRevision)

        revision_by_obj = await self.page_course.get_revision_by_id(revision_by_id)
        self.assertIsInstance(revision_by_obj, PageRevision)

    async def test_get_revision_by_id_group(self, m):
        register_uris({"page": ["get_latest_rev_by_id_group"]}, m)

        revision_by_id = await self.page_group.get_revision_by_id(2)
        self.assertIsInstance(revision_by_id, PageRevision)

        revision_by_obj = await self.page_group.get_revision_by_id(revision_by_id)
        self.assertIsInstance(revision_by_obj, PageRevision)

    async def test_revert_to_revision_course(self, m):
        register_uris({"page": ["revert_to_revision"]}, m)

        revision = await self.page_course.revert_to_revision(3)

        self.assertIsInstance(revision, PageRevision)

    async def test_revert_to_revision_group(self, m):
        register_uris({"page": ["revert_to_revision_group"]}, m)

        revision = await self.page_group.revert_to_revision(3)

        self.assertIsInstance(revision, PageRevision)

    # parent_id
    def test_parent_id_course(self, m):
        self.assertEqual(self.page_course.parent_id, 1)

    def test_parent_id_group(self, m):
        self.assertEqual(self.page_group.parent_id, 1)

    def test_parent_id_no_id(self, m):
        page = Page(self.canvas._Canvas__requester, {"url": "my-url"})
        with self.assertRaises(ValueError):
            page.parent_id

    # parent_type
    def test_parent_type_course(self, m):
        self.assertEqual(self.page_course.parent_type, "course")

    def test_parent_type_group(self, m):
        self.assertEqual(self.page_group.parent_type, "group")

    def test_parent_type_no_id(self, m):
        page = Page(self.canvas._Canvas__requester, {"url": "my-url"})
        with self.assertRaises(ValueError):
            page.parent_type

    # get_parent()
    async def test_get_parent_course(self, m):
        register_uris({"course": ["get_by_id"]}, m)

        self.assertIsInstance(await self.page_course.get_parent(), Course)

    async def test_get_parent_group(self, m):
        register_uris({"group": ["get_by_id"]}, m)

        self.assertIsInstance(await self.page_group.get_parent(), Group)


@aioresponse_mock
class TestPageRevision(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            requires = {
                "course": ["get_by_id", "get_page"],
                "group": ["get_by_id", "pages_get_page"],
                "page": ["get_latest_rev_by_id", "get_latest_rev_by_id_group"],
            }
            register_uris(requires, m)

            self.course = await self.canvas.get_course(1)
            self.group = await self.canvas.get_group(1)
            self.page_course = await self.course.get_page("my-url")
            self.page_group = await self.group.get_page("my-url")
            self.revision = await self.page_course.get_revision_by_id(2)
            self.group_revision = await self.page_group.get_revision_by_id(2)

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.revision)
        self.assertIsInstance(string, str)

    # parent_id
    def test_parent_id_course(self, m):
        self.assertEqual(self.revision.parent_id, 1)

    def test_parent_id_no_id(self, m):
        page = PageRevision(self.canvas._Canvas__requester, {"url": "my-url"})
        with self.assertRaises(ValueError):
            page.parent_id

    # parent_type
    def test_parent_type_course(self, m):
        self.assertEqual(self.page_course.parent_type, "course")

    def test_parent_type_group(self, m):
        self.assertEqual(self.page_group.parent_type, "group")

    def test_parent_type_no_id(self, m):
        page = PageRevision(self.canvas._Canvas__requester, {"url": "my-url"})
        with self.assertRaises(ValueError):
            page.parent_type

    # get_parent()
    async def test_get_parent_course(self, m):
        register_uris({"course": ["get_by_id"]}, m)

        self.assertIsInstance(await self.revision.get_parent(), Course)

    async def test_get_parent_group(self, m):
        register_uris({"group": ["get_by_id"]}, m)

        self.assertIsInstance(await self.group_revision.get_parent(), Group)
