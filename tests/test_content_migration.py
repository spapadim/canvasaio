import unittest

from aioresponses import aioresponses

from canvasaio import Canvas
from canvasaio.account import Account
from canvasaio.content_migration import ContentMigration, MigrationIssue
from canvasaio.course import Course
from canvasaio.group import Group
from canvasaio.progress import Progress
from canvasaio.user import User
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestContentMigration(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            requires = {
                "course": ["get_by_id", "get_content_migration_single"],
                "group": ["get_by_id", "get_content_migration_single"],
                "account": ["get_by_id", "get_content_migration_single"],
                "user": ["get_by_id", "get_content_migration_single"],
            }
            register_uris(requires, m)

            self.account = await self.canvas.get_account(1)
            self.course = await self.canvas.get_course(1)
            self.group = await self.canvas.get_group(1)
            self.user = await self.canvas.get_user(1)

            self.content_migration = await self.account.get_content_migration(1)
            self.content_migration_course = await self.course.get_content_migration(1)
            self.content_migration_group = await self.group.get_content_migration(1)
            self.content_migration_user = await self.user.get_content_migration(1)

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.content_migration)
        self.assertIsInstance(string, str)

    # _parent_type
    def test_parent_type_account(self, m):
        self.assertEqual(self.content_migration._parent_type, "account")

    def test_parent_type_course(self, m):
        self.assertEqual(self.content_migration_course._parent_type, "course")

    def test_parent_type_group(self, m):
        self.assertEqual(self.content_migration_group._parent_type, "group")

    def test_parent_type_user(self, m):
        self.assertEqual(self.content_migration_user._parent_type, "user")

    def test_parent_type_no_type(self, m):
        migration = ContentMigration(self.canvas._Canvas__requester, {"id": 1})
        with self.assertRaises(ValueError):
            migration._parent_type

    # _parent_id
    def test_parent_id_account(self, m):
        self.assertEqual(self.content_migration._parent_id, 1)

    def test_parent_id_course(self, m):
        self.assertEqual(self.content_migration_course._parent_id, 1)

    def test_parent_id_group(self, m):
        self.assertEqual(self.content_migration_group._parent_id, 1)

    def test_parent_id_user(self, m):
        self.assertEqual(self.content_migration_user._parent_id, 1)

    def test_parent_id_no_id(self, m):
        migration = ContentMigration(self.canvas._Canvas__requester, {"id": 1})
        with self.assertRaises(ValueError):
            migration._parent_id

    # get_migration_issue()
    async def test_get_migration_issue(self, m):
        register_uris({"content_migration": ["get_migration_issue_single"]}, m)

        issue = await self.content_migration.get_migration_issue(1)
        self.assertIsInstance(issue, MigrationIssue)
        self.assertTrue(hasattr(issue, "id"))
        self.assertEqual(issue.id, 1)

    # get_migration_issues()
    async def test_get_migration_issues(self, m):
        register_uris({"content_migration": ["get_migration_issue_multiple"]}, m)

        response = self.content_migration.get_migration_issues()
        issues = [iss async for iss in response]

        self.assertEqual(len(issues), 2)

        self.assertIsInstance(issues[0], MigrationIssue)
        self.assertTrue(hasattr(issues[0], "id"))
        self.assertEqual(issues[0].id, 1)
        self.assertIsInstance(issues[1], MigrationIssue)
        self.assertTrue(hasattr(issues[1], "id"))
        self.assertEqual(issues[1].id, 2)

    # get_parent()
    async def test_get_parent_account(self, m):
        register_uris({"content_migration": ["get_parent_account"]}, m)

        account = await self.content_migration.get_parent()
        self.assertIsInstance(account, Account)
        self.assertTrue(hasattr(account, "id"))
        self.assertEqual(account.id, 1)

    async def test_get_parent_course(self, m):
        register_uris({"content_migration": ["get_parent_course"]}, m)

        course = await self.content_migration_course.get_parent()
        self.assertIsInstance(course, Course)
        self.assertTrue(hasattr(course, "id"))
        self.assertEqual(course.id, 1)

    async def test_get_parent_group(self, m):
        register_uris({"content_migration": ["get_parent_group"]}, m)

        group = await self.content_migration_group.get_parent()
        self.assertIsInstance(group, Group)
        self.assertTrue(hasattr(group, "id"))
        self.assertEqual(group.id, 1)

    async def test_get_parent_user(self, m):
        register_uris({"content_migration": ["get_parent_user"]}, m)

        user = await self.content_migration_user.get_parent()
        self.assertIsInstance(user, User)
        self.assertTrue(hasattr(user, "id"))
        self.assertEqual(user.id, 1)

    # get_progress()
    async def test_get_progress(self, m):
        register_uris({"content_migration": ["get_progress"]}, m)

        progress = await self.content_migration.get_progress()
        self.assertIsInstance(progress, Progress)
        self.assertTrue(hasattr(progress, "id"))
        self.assertEqual(progress.id, 1)

    # update()
    async def test_update(self, m):
        register_uris({"content_migration": ["update"]}, m)

        worked = await self.content_migration.update()
        self.assertTrue(worked)
        self.assertTrue(hasattr(self.content_migration, "migration_type"))
        self.assertEqual(self.content_migration.migration_type, "dummy_importer")

    async def test_update_fail(self, m):
        register_uris({"content_migration": ["update_fail"]}, m)

        worked = await self.content_migration.update()
        self.assertFalse(worked)


@aioresponse_mock
class TestMigrationIssue(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            requires = {
                "course": ["get_by_id", "get_content_migration_single"],
                "group": ["get_by_id", "get_content_migration_single"],
                "account": ["get_by_id", "get_content_migration_single"],
                "user": ["get_by_id", "get_content_migration_single"],
                "content_migration": [
                    "get_migration_issue_single",
                    "get_migration_issue_single_course",
                    "get_migration_issue_single_group",
                    "get_migration_issue_single_user",
                ],
            }
            register_uris(requires, m)

            self.account = await self.canvas.get_account(1)
            self.course = await self.canvas.get_course(1)
            self.group = await self.canvas.get_group(1)
            self.user = await self.canvas.get_user(1)

            self.content_migration = await self.account.get_content_migration(1)
            self.content_migration_course = await self.course.get_content_migration(1)
            self.content_migration_group = await self.group.get_content_migration(1)
            self.content_migration_user = await self.user.get_content_migration(1)

            self.migration_issue = await self.content_migration.get_migration_issue(1)
            self.migration_issue_course = (
                await self.content_migration_course.get_migration_issue(1)
            )
            self.migration_issue_group = (
                await self.content_migration_group.get_migration_issue(1)
            )
            self.migration_issue_user = await self.content_migration_user.get_migration_issue(
                1
            )

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.migration_issue)
        self.assertIsInstance(string, str)

    # update()
    async def test_update(self, m):
        register_uris({"content_migration": ["update_issue"]}, m)

        worked = await self.migration_issue.update()
        self.assertTrue(worked)
        self.assertTrue(hasattr(self.migration_issue, "id"))
        self.assertEqual(self.migration_issue.id, 1)

    async def test_update_fail(self, m):
        register_uris({"content_migration": ["update_issue_fail"]}, m)

        worked = await self.migration_issue.update()
        self.assertFalse(worked)


@aioresponse_mock
class TestMigrator(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            requires = {
                "course": ["get_by_id", "get_migration_systems_multiple"],
                "group": ["get_by_id", "get_migration_systems_multiple"],
                "account": ["get_by_id", "get_migration_systems_multiple"],
                "user": ["get_by_id", "get_migration_systems_multiple"],
                "content_migration": [
                    "get_migration_issue_single",
                    "get_migration_issue_single_course",
                    "get_migration_issue_single_group",
                    "get_migration_issue_single_user",
                ],
            }
            register_uris(requires, m)

            self.account = await self.canvas.get_account(1)
            self.course = await self.canvas.get_course(1)
            self.group = await self.canvas.get_group(1)
            self.user = await self.canvas.get_user(1)

            self.migrator = await self.account.get_migration_systems()[0]
            self.migrator_course = await self.course.get_migration_systems()[0]
            self.migrator_group = await self.group.get_migration_systems()[0]
            self.migrator_user = await self.user.get_migration_systems()[0]

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.migrator)
        self.assertIsInstance(string, str)
