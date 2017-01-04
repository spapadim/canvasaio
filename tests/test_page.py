import unittest

import requests_mock

from pycanvas.canvas import Canvas
from pycanvas.course import Course
from pycanvas.group import Group
from pycanvas.page import Page, PageRevision
from tests import settings
from tests.util import register_uris


@requests_mock.Mocker()
class TestPage(unittest.TestCase):

    @classmethod
    def setUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with requests_mock.Mocker() as m:
            requires = {
                'course': ['get_by_id'],
                'group': ['get_by_id', 'pages_get_page'],
                'page': ['get_page']
            }
            register_uris(requires, m)

            self.course = self.canvas.get_course(1)
            self.group = self.canvas.get_group(1)
            self.page_course = self.course.get_page('my-url')
            self.page_group = self.group.get_page('my-url')

    # __str__()
    def test__str__(self, m):
        string = str(self.page_course)
        assert isinstance(string, str)

    def test_edit(self, m):
        register_uris({'page': ['edit']}, m)

        new_title = "New Page"
        self.page_course.edit(page={'title': new_title})

        assert isinstance(self.page_course, Page)
        assert hasattr(self.page_course, 'title')
        assert self.page_course.title == new_title

    def test_delete(self, m):
        register_uris({'page': ['delete_page']}, m)

        page = self.page_course
        deleted_page = page.delete()

        assert isinstance(deleted_page, Page)

    def test_list_revisions(self, m):
        register_uris({'page': ['list_revisions', 'list_revisions2']}, m)

        revisions = self.page_course.list_revisions()
        rev_list = [rev for rev in revisions]

        assert len(rev_list) == 4
        assert isinstance(rev_list[0], PageRevision)

    def test_show_latest_revision(self, m):
        register_uris({'page': ['latest_revision']}, m)

        revision = self.page_course.show_latest_revision()

        assert isinstance(revision, PageRevision)

    def test_get_revision_by_id_course(self, m):
        register_uris({'page': ['get_latest_rev_by_id']}, m)

        revision = self.page_course.get_revision_by_id(2)

        assert isinstance(revision, PageRevision)

    def test_get_revision_by_id_group(self, m):
        register_uris({'page': ['get_latest_rev_by_id_group']}, m)

        revision = self.page_group.get_revision_by_id(2)

        assert isinstance(revision, PageRevision)

    def test_revert_to_revision_course(self, m):
        register_uris({'page': ['revert_to_revision']}, m)

        revision = self.page_course.revert_to_revision(3)

        assert isinstance(revision, PageRevision)

    def test_revert_to_revision_group(self, m):
        register_uris({'page': ['revert_to_revision_group']}, m)

        revision = self.page_group.revert_to_revision(3)

        assert isinstance(revision, PageRevision)

    # parent_id
    def test_parent_id_course(self, m):
        assert self.page_course.parent_id == 1

    def test_parent_id_group(self, m):
        assert self.page_group.parent_id == 1

    def test_parent_id_no_id(self, m):
        page = Page(self.canvas._Canvas__requester, {'url': 'my-url'})
        with self.assertRaises(ValueError):
            page.parent_id

    # parent_type
    def test_parent_type_course(self, m):
        assert self.page_course.parent_type == 'course'

    def test_parent_type_group(self, m):
        assert self.page_group.parent_type == 'group'

    def test_parent_type_no_id(self, m):
        page = Page(self.canvas._Canvas__requester, {'url': 'my-url'})
        with self.assertRaises(ValueError):
            page.parent_type

    # get_parent()
    def test_get_parent_course(self, m):
        register_uris({'course': ['get_by_id']}, m)

        assert isinstance(self.page_course.get_parent(), Course)

    def test_get_parent_group(self, m):
        register_uris({'group': ['get_by_id']}, m)

        assert isinstance(self.page_group.get_parent(), Group)


@requests_mock.Mocker()
class TestPageRevision(unittest.TestCase):

    @classmethod
    def setUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with requests_mock.Mocker() as m:
            requires = {
                'course': ['get_by_id', 'get_page'],
                'group': ['get_by_id', 'pages_get_page'],
                'page': ['get_latest_rev_by_id', 'get_latest_rev_by_id_group']
            }
            register_uris(requires, m)

            self.course = self.canvas.get_course(1)
            self.group = self.canvas.get_group(1)
            self.page_course = self.course.get_page('my-url')
            self.page_group = self.group.get_page('my-url')
            self.revision = self.page_course.get_revision_by_id(2)
            self.group_revision = self.page_group.get_revision_by_id(2)

    # __str__()
    def test__str__(self, m):
        string = str(self.revision)
        assert isinstance(string, str)

    # parent_id
    def test_parent_id_course(self, m):
        assert self.revision.parent_id == 1

    def test_parent_id_no_id(self, m):
        page = PageRevision(self.canvas._Canvas__requester, {'url': 'my-url'})
        with self.assertRaises(ValueError):
            page.parent_id

    # parent_type
    def test_parent_type_course(self, m):
        assert self.page_course.parent_type == 'course'

    def test_parent_type_group(self, m):
        assert self.page_group.parent_type == 'group'

    def test_parent_type_no_id(self, m):
        page = PageRevision(self.canvas._Canvas__requester, {'url': 'my-url'})
        with self.assertRaises(ValueError):
            page.parent_type

    # get_parent()
    def test_get_parent_course(self, m):
        register_uris({'course': ['get_by_id']}, m)

        assert isinstance(self.revision.get_parent(), Course)

    def test_get_parent_group(self, m):
        register_uris({'group': ['get_by_id']}, m)

        assert isinstance(self.group_revision.get_parent(), Group)