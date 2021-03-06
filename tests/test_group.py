import unittest
from urllib.parse import quote
import uuid

from aioresponses import aioresponses, CallbackResult

from canvasaio import Canvas
from canvasaio.assignment import AssignmentOverride
from canvasaio.group import Group, GroupMembership, GroupCategory
from canvasaio.course import Page
from canvasaio.discussion_topic import DiscussionTopic
from canvasaio.exceptions import RequiredFieldMissing
from canvasaio.external_feed import ExternalFeed
from canvasaio.file import File
from canvasaio.folder import Folder
from canvasaio.license import License
from canvasaio.paginated_list import PaginatedList
from canvasaio.tab import Tab
from canvasaio.content_migration import ContentMigration, Migrator
from canvasaio.content_export import ContentExport
from canvasaio.usage_rights import UsageRights
from tests import settings
from tests.util import cleanup_file, register_uris, aioresponse_mock


@aioresponse_mock
class TestGroup(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            register_uris({"course": ["get_by_id"], "group": ["get_by_id"]}, m)

            self.course = await self.canvas.get_course(1)
            self.group = await self.canvas.get_group(1)

    async def asyncTearDown(self) -> None:
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.group)
        self.assertIsInstance(string, str)

    # show_front_page()
    async def test_show_front_page(self, m):
        register_uris({"group": ["show_front_page"]}, m)

        front_page = await self.group.show_front_page()
        self.assertIsInstance(front_page, Page)
        self.assertTrue(hasattr(front_page, "url"))
        self.assertTrue(hasattr(front_page, "title"))

    # create_front_page()
    async def test_edit_front_page(self, m):
        register_uris({"group": ["edit_front_page"]}, m)

        new_front_page = await self.group.edit_front_page()
        self.assertIsInstance(new_front_page, Page)
        self.assertTrue(hasattr(new_front_page, "url"))
        self.assertTrue(hasattr(new_front_page, "title"))

    # get_pages()
    async def test_get_pages(self, m):
        register_uris({"group": ["get_pages", "get_pages2"]}, m)

        pages = self.group.get_pages()
        page_list = [page async for page in pages]
        self.assertEqual(len(page_list), 4)
        self.assertIsInstance(page_list[0], Page)
        self.assertTrue(hasattr(page_list[0], "id"))
        self.assertEqual(page_list[0].group_id, self.group.id)

    # create_page()
    async def test_create_page(self, m):
        register_uris({"group": ["create_page"]}, m)

        title = "New Page"
        new_page = await self.group.create_page(wiki_page={"title": title})
        self.assertIsInstance(new_page, Page)
        self.assertTrue(hasattr(new_page, "title"))
        self.assertEqual(new_page.title, title)
        self.assertTrue(hasattr(new_page, "id"))
        self.assertEqual(new_page.group_id, self.group.id)

    async def test_create_page_fail(self, m):
        with self.assertRaises(RequiredFieldMissing):
            await self.group.create_page(settings.INVALID_ID)

    # get_page()
    async def test_get_page(self, m):
        register_uris({"group": ["get_page"]}, m)

        url = "my-url"
        page = await self.group.get_page(url)
        self.assertIsInstance(page, Page)

    # edit()
    async def test_edit(self, m):
        register_uris({"group": ["edit"]}, m)

        new_title = "New Group"
        response = await self.group.edit(description=new_title)
        self.assertIsInstance(response, Group)
        self.assertTrue(hasattr(response, "description"))
        self.assertEqual(response.description, new_title)

    # delete()
    async def test_delete(self, m):
        register_uris({"group": ["delete"]}, m)

        group = await self.group.delete()
        self.assertIsInstance(group, Group)
        self.assertTrue(hasattr(group, "name"))
        self.assertTrue(hasattr(group, "description"))

    # invite()
    async def test_invite(self, m):
        register_uris({"group": ["invite"]}, m)

        user_list = ["1", "2"]
        response = self.group.invite(user_list)
        gmembership_list = [groupmembership async for groupmembership in response]
        self.assertIsInstance(gmembership_list[0], GroupMembership)
        self.assertEqual(len(gmembership_list), 2)

    # get_users()
    async def test_get_users(self, m):
        register_uris({"group": ["list_users", "list_users_p2"]}, m)

        from canvasaio.user import User

        users = self.group.get_users()
        user_list = [user async for user in users]
        self.assertIsInstance(user_list[0], User)
        self.assertEqual(len(user_list), 4)

    # remove_user()
    async def test_remove_user(self, m):
        register_uris({"group": ["list_users", "list_users_p2", "remove_user"]}, m)

        from canvasaio.user import User

        user_by_id = await self.group.remove_user(1)
        self.assertIsInstance(user_by_id, User)

        users = self.group.get_users()
        user_by_obj = await self.group.remove_user(await users[0])
        self.assertIsInstance(user_by_obj, User)

    # upload()
    async def test_upload(self, m):
        register_uris({"group": ["upload", "upload_final"]}, m)

        filename = "testfile_group_{}".format(uuid.uuid4().hex)
        try:
            with open(filename, "w+") as file:
                response = await self.group.upload(file)
            self.assertTrue(response[0])
            self.assertIsInstance(response[1], dict)
            self.assertIn("url", response[1])
        finally:
            cleanup_file(filename)

    # preview_processed_html()
    async def test_preview_processed_html(self, m):
        register_uris({"group": ["preview_processed_html"]}, m)

        html_str = "<p>processed html</p>"
        response = await self.group.preview_html(html_str)
        self.assertEqual(response, html_str)

    # get_activity_stream_summary()
    async def test_get_activity_stream_summary(self, m):
        register_uris({"group": ["activity_stream_summary"]}, m)

        response = await self.group.get_activity_stream_summary()
        self.assertEqual(len(response), 2)
        self.assertIn("type", response[0])

    # get_memberships()
    async def test_get_memberships(self, m):
        register_uris({"group": ["list_memberships", "list_memberships_p2"]}, m)

        response = self.group.get_memberships()
        membership_list = [membership async for membership in response]
        self.assertEqual(len(membership_list), 4)
        self.assertIsInstance(membership_list[0], GroupMembership)
        self.assertTrue(hasattr(membership_list[0], "id"))

    # get_membership()
    async def test_get_membership(self, m):
        register_uris({"group": ["get_membership", "list_users", "list_users_p2"]}, m)

        membership_by_id = await self.group.get_membership(1, "users")
        self.assertIsInstance(membership_by_id, GroupMembership)

        users = self.group.get_users()
        membership_by_obj = await self.group.get_membership(await users[0], "users")
        self.assertIsInstance(membership_by_obj, GroupMembership)

    # create_membership()
    async def test_create_membership(self, m):
        register_uris(
            {"group": ["create_membership", "list_users", "list_users_p2"]}, m
        )

        response = await self.group.create_membership(1)
        self.assertIsInstance(response, GroupMembership)

        users = self.group.get_users()
        response = await self.group.create_membership(await users[0])
        self.assertIsInstance(response, GroupMembership)

    # update_membership()
    async def test_update_membership(self, m):
        register_uris(
            {"group": ["list_users", "list_users_p2", "update_membership_user"]}, m
        )

        updated_membership_by_id = await self.group.update_membership(1)
        self.assertIsInstance(updated_membership_by_id, GroupMembership)

        users = self.group.get_users()
        updated_membership_by_obj = await self.group.update_membership(await users[0])
        self.assertIsInstance(updated_membership_by_obj, GroupMembership)

    # get_discussion_topic()
    async def test_get_discussion_topic(self, m):
        register_uris({"group": ["get_discussion_topic", "get_discussion_topics"]}, m)

        group_id = 1
        discussion_by_id = await self.group.get_discussion_topic(group_id)
        self.assertIsInstance(discussion_by_id, DiscussionTopic)
        self.assertTrue(hasattr(discussion_by_id, "group_id"))
        self.assertEqual(group_id, discussion_by_id.id)
        self.assertEqual(discussion_by_id.group_id, 1)

        discussion_topic = await self.group.get_discussion_topics()[0]
        discussion_by_obj = await self.group.get_discussion_topic(discussion_topic)
        self.assertIsInstance(discussion_by_obj, DiscussionTopic)
        self.assertTrue(hasattr(discussion_by_obj, "group_id"))
        self.assertEqual(group_id, discussion_by_obj.id)
        self.assertEqual(discussion_by_obj.group_id, 1)

    # get_file()
    async def test_get_file(self, m):
        register_uris({"group": ["get_file"]}, m)

        file_by_id = await self.group.get_file(1)
        self.assertIsInstance(file_by_id, File)
        self.assertEqual(file_by_id.display_name, "Group_File.docx")
        self.assertEqual(file_by_id.size, 4096)

        file_by_obj = await self.group.get_file(file_by_id)
        self.assertIsInstance(file_by_obj, File)
        self.assertEqual(file_by_obj.display_name, "Group_File.docx")
        self.assertEqual(file_by_obj.size, 4096)

    # get_full_discussion_topic
    async def test_get_full_discussion_topic(self, m):
        register_uris(
            {"group": ["get_full_discussion_topic", "get_discussion_topics"]}, m
        )

        discussion_by_id = await self.group.get_full_discussion_topic(1)
        self.assertIsInstance(discussion_by_id, dict)
        self.assertIn("view", discussion_by_id)
        self.assertIn("participants", discussion_by_id)
        self.assertIn("id", discussion_by_id)
        self.assertEqual(discussion_by_id["id"], 1)

        discussion_topic = await self.group.get_discussion_topics()[0]
        discussion_by_obj = await self.group.get_full_discussion_topic(discussion_topic)
        self.assertIsInstance(discussion_by_obj, dict)
        self.assertIn("view", discussion_by_obj)
        self.assertIn("participants", discussion_by_obj)
        self.assertIn("id", discussion_by_obj)
        self.assertEqual(discussion_by_obj["id"], 1)

    # get_discussion_topics()
    async def test_get_discussion_topics(self, m):
        register_uris({"group": ["get_discussion_topics"]}, m)

        response = self.group.get_discussion_topics()
        discussion_list = [discussion async for discussion in response]
        self.assertIsInstance(discussion_list[0], DiscussionTopic)
        self.assertTrue(hasattr(discussion_list[0], "group_id"))
        self.assertEqual(2, len(discussion_list))

    # create_discussion_topic()
    async def test_create_discussion_topic(self, m):
        register_uris({"group": ["create_discussion_topic"]}, m)

        title = "Topic 1"
        discussion = await self.group.create_discussion_topic()
        self.assertTrue(hasattr(discussion, "group_id"))
        self.assertIsInstance(discussion, DiscussionTopic)
        self.assertEqual(discussion.title, title)
        self.assertEqual(discussion.group_id, 1)

    # reorder_pinned_topics()
    async def test_reorder_pinned_topics(self, m):
        # Custom callback to test that params are set correctly
        async def callback(url, data, **kwargs):
            self.assertEqual(1, len(data._fields))
            field_type_options, field_headers, field_value = data._fields[0]
            self.assertEqual("order", field_type_options["name"])
            self.assertEqual("1,2,3", field_value)
            return CallbackResult(status=200, body='{"reorder": true, "order": [1, 2, 3]}')

        m.add(
            settings.BASE_URL + "/api/v1/groups/1/discussion_topics/reorder",
            method="POST",
            callback=callback,
        )

        order = [1, 2, 3]
        discussions = await self.group.reorder_pinned_topics(order=order)
        self.assertTrue(discussions)

    async def test_reorder_pinned_topics_tuple(self, m):
        register_uris({"group": ["reorder_pinned_topics"]}, m)

        order = (1, 2, 3)
        discussions = await self.group.reorder_pinned_topics(order=order)
        self.assertTrue(discussions)

    async def test_reorder_pinned_topics_comma_separated_string(self, m):
        register_uris({"group": ["reorder_pinned_topics"]}, m)

        order = "1,2,3"
        discussions = await self.group.reorder_pinned_topics(order=order)
        self.assertTrue(discussions)

    async def test_reorder_pinned_topics_invalid_input(self, m):
        order = "invalid string"
        with self.assertRaises(ValueError):
            await self.group.reorder_pinned_topics(order=order)

    # get_external_feeds()
    async def test_get_external_feeds(self, m):
        register_uris({"group": ["list_external_feeds"]}, m)

        feeds = self.group.get_external_feeds()
        feed_list = [feed async for feed in feeds]
        self.assertEqual(len(feed_list), 2)
        self.assertTrue(hasattr(feed_list[0], "url"))
        self.assertIsInstance(feed_list[0], ExternalFeed)

    # create_external_feed()
    async def test_create_external_feed(self, m):
        register_uris({"group": ["create_external_feed"]}, m)

        url_str = "https://example.com/myblog.rss"
        response = await self.group.create_external_feed(url=url_str)
        self.assertIsInstance(response, ExternalFeed)

    # delete_external_feed()
    async def test_delete_external_feed(self, m):
        register_uris({"group": ["delete_external_feed"]}, m)

        deleted_ef_by_id = await self.group.delete_external_feed(1)

        self.assertIsInstance(deleted_ef_by_id, ExternalFeed)
        self.assertTrue(hasattr(deleted_ef_by_id, "url"))
        self.assertEqual(deleted_ef_by_id.display_name, "My Blog")

        deleted_ef_by_obj = await self.group.delete_external_feed(deleted_ef_by_id)

        self.assertIsInstance(deleted_ef_by_obj, ExternalFeed)
        self.assertTrue(hasattr(deleted_ef_by_obj, "url"))
        self.assertEqual(deleted_ef_by_obj.display_name, "My Blog")

    # get_files()
    async def test_get_files(self, m):
        register_uris({"group": ["list_group_files", "list_group_files2"]}, m)

        files = self.group.get_files()
        file_list = [file async for file in files]
        self.assertEqual(len(file_list), 4)
        self.assertIsInstance(file_list[0], File)

    # get_folder()
    async def test_get_folder(self, m):
        register_uris({"group": ["get_folder"]}, m)

        folder_by_id = await self.group.get_folder(1)
        self.assertEqual(folder_by_id.name, "Folder 1")
        self.assertIsInstance(folder_by_id, Folder)

        folder_by_obj = await self.group.get_folder(folder_by_id)
        self.assertEqual(folder_by_obj.name, "Folder 1")
        self.assertIsInstance(folder_by_obj, Folder)

    # get_folders()
    async def test_get_folders(self, m):
        register_uris({"group": ["list_folders"]}, m)

        folders = self.group.get_folders()
        folder_list = [folder async for folder in folders]
        self.assertEqual(len(folder_list), 2)
        self.assertIsInstance(folder_list[0], Folder)

    # create_folder()
    async def test_create_folder(self, m):
        register_uris({"group": ["create_folder"]}, m)

        name_str = "Test String"
        response = await self.group.create_folder(name=name_str)
        self.assertIsInstance(response, Folder)

    # get_tabs()
    async def test_get_tabs(self, m):
        register_uris({"group": ["list_tabs"]}, m)

        tabs = self.group.get_tabs()
        tab_list = [tab async for tab in tabs]
        self.assertEqual(len(tab_list), 2)
        self.assertIsInstance(tab_list[0], Tab)

    # create_content_migration
    async def test_create_content_migration(self, m):
        register_uris({"group": ["create_content_migration"]}, m)

        content_migration = await self.group.create_content_migration("dummy_importer")

        self.assertIsInstance(content_migration, ContentMigration)
        self.assertTrue(hasattr(content_migration, "migration_type"))

    async def test_create_content_migration_migrator(self, m):
        register_uris(
            {"group": ["create_content_migration", "get_migration_systems_multiple"]}, m
        )

        migrators = self.group.get_migration_systems()
        content_migration = await self.group.create_content_migration(await migrators[0])

        self.assertIsInstance(content_migration, ContentMigration)
        self.assertTrue(hasattr(content_migration, "migration_type"))

    async def test_create_content_migration_bad_migration_type(self, m):
        register_uris({"group": ["create_content_migration"]}, m)

        with self.assertRaises(TypeError):
            await self.group.create_content_migration(1)

    # get_collaborations
    async def test_get_collaborations(self, m):
        register_uris({"group": ["get_collaborations"]}, m)

        from canvasaio.collaboration import Collaboration

        collab_list = self.group.get_collaborations()

        self.assertIsInstance(collab_list, PaginatedList)

        collab_list = [collab async for collab in collab_list]

        self.assertIsInstance(collab_list[0], Collaboration)
        self.assertIsInstance(collab_list[1], Collaboration)
        self.assertEqual(collab_list[0].id, 1)
        self.assertEqual(collab_list[1].id, 2)
        self.assertEqual(collab_list[0].document_id, "oinwoenfe8w8ef_onweufe89fef")
        self.assertEqual(collab_list[1].document_id, "oinwoenfe8w8ef_onweufe89zzz")

    # get_content_migration
    async def test_get_content_migration(self, m):
        register_uris({"group": ["get_content_migration_single"]}, m)

        content_migration = await self.group.get_content_migration(1)

        self.assertIsInstance(content_migration, ContentMigration)
        self.assertTrue(hasattr(content_migration, "migration_type"))

    # get_content_migrations
    async def test_get_content_migrations(self, m):
        register_uris({"group": ["get_content_migration_multiple"]}, m)

        response = self.group.get_content_migrations()
        content_migrations = [migration async for migration in response]

        self.assertEqual(len(content_migrations), 2)

        self.assertIsInstance(content_migrations[0], ContentMigration)
        self.assertEqual(content_migrations[0].id, 1)
        self.assertEqual(content_migrations[0].migration_type, "dummy_importer")
        self.assertIsInstance(content_migrations[1], ContentMigration)
        self.assertEqual(content_migrations[1].id, 2)
        self.assertEqual(content_migrations[1].migration_type, "dummy_importer")

    # get_migration_systems
    async def test_get_migration_systems(self, m):
        register_uris({"group": ["get_migration_systems_multiple"]}, m)

        response = self.group.get_migration_systems()
        migration_systems = [system async for system in response]

        self.assertEqual(len(migration_systems), 2)

        self.assertIsInstance(migration_systems[0], Migrator)
        self.assertEqual(migration_systems[0].type, "dummy_importer")
        self.assertEqual(migration_systems[0].requires_file_upload, True)
        self.assertEqual(migration_systems[0].name, "Dummy Importer 01")
        self.assertIsInstance(migration_systems[1], Migrator)
        self.assertEqual(migration_systems[1].type, "dummy_importer_02")
        self.assertEqual(migration_systems[1].requires_file_upload, False)
        self.assertEqual(migration_systems[1].name, "Dummy Importer 02")

    # get_assignment_override
    async def test_get_assignment_override(self, m):
        register_uris({"assignment": ["override_group_alias"]}, m)

        override = await self.group.get_assignment_override(1)

        self.assertIsInstance(override, AssignmentOverride)
        self.assertEqual(override.group_id, self.group.id)

    # get_content_exports()
    async def test_list_content_exports(self, m):
        register_uris({"group": ["multiple_content_exports"]}, m)

        content_exports = self.group.get_content_exports()
        content_export_list = [content_export async for content_export in content_exports]

        self.assertEqual(len(content_export_list), 2)
        self.assertEqual(content_export_list[0].id, 2)
        self.assertEqual(content_export_list[1].export_type, "b")
        self.assertIsInstance(content_export_list[0], ContentExport)

    # get_content_export()
    async def test_show_content_export(self, m):
        register_uris({"group": ["single_content_export"]}, m)

        content_export = await self.group.get_content_export(11)

        self.assertTrue(hasattr(content_export, "export_type"))
        self.assertIsInstance(content_export, ContentExport)

    # export_content()
    async def test_export_content(self, m):
        register_uris({"group": ["export_content"]}, m)

        content_export = await self.group.export_content("d")

        self.assertIsInstance(content_export, ContentExport)
        self.assertTrue(hasattr(content_export, "export_type"))

    # set_usage_rights()
    async def test_set_usage_rights(self, m):
        register_uris({"group": ["set_usage_rights"]}, m)

        usage_rights = await self.group.set_usage_rights(
            file_ids=[1, 2],
            usage_rights={"use_justification": "fair_use", "license": "private"},
        )

        self.assertIsInstance(usage_rights, UsageRights)
        self.assertEqual(usage_rights.use_justification, "fair_use")
        self.assertEqual(usage_rights.message, "2 files updated")
        self.assertEqual(usage_rights.license, "private")
        self.assertEqual(usage_rights.file_ids, [1, 2])

    # remove_usage_rights()
    async def test_remove_usage_rights(self, m):
        register_uris({"group": ["remove_usage_rights"]}, m)

        retval = await self.group.remove_usage_rights(file_ids=[1, 2])

        self.assertIsInstance(retval, dict)
        self.assertIn("message", retval)
        self.assertEqual(retval["file_ids"], [1, 2])
        self.assertEqual(retval["message"], "2 files updated")

    # get_licenses()
    async def test_get_licenses(self, m):
        register_uris({"group": ["get_licenses"]}, m)

        licenses = self.group.get_licenses()
        self.assertIsInstance(licenses, PaginatedList)
        licenses = [lic async for lic in licenses]

        for lic in licenses:
            self.assertIsInstance(lic, License)
            self.assertTrue(hasattr(lic, "id"))
            self.assertTrue(hasattr(lic, "name"))
            self.assertTrue(hasattr(lic, "url"))

        self.assertEqual(2, len(licenses))

    # resolve_path()
    async def test_resolve_path(self, m):
        register_uris({"group": ["resolve_path"]}, m)

        full_path = "Folder_Level_1/Folder_Level_2/Folder_Level_3"
        folders = self.group.resolve_path(full_path)
        folder_list = [folder async for folder in folders]
        self.assertEqual(len(folder_list), 4)
        self.assertIsInstance(folder_list[0], Folder)
        folder_names = ("files/" + full_path).split("/")
        for folder_name, folder in zip(folder_names, folder_list):
            self.assertEqual(folder_name, folder.name)

    # resolve_path() with null input
    async def test_resolve_path_null(self, m):
        register_uris({"group": ["resolve_path_null"]}, m)

        # test with null input
        root_folder = self.group.resolve_path()
        root_folder_list = [folder async for folder in root_folder]
        self.assertEqual(len(root_folder_list), 1)
        self.assertIsInstance(root_folder_list[0], Folder)
        self.assertEqual("files", root_folder_list[0].name)


@aioresponse_mock
class TestGroupMembership(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            register_uris({"group": ["get_by_id", "get_membership"]}, m)

            self.group = await self.canvas.get_group(1)
            self.membership = await self.group.get_membership(1, "users")

    async def asyncTearDown(self) -> None:
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.membership)
        self.assertIsInstance(string, str)

    # update()
    async def test_update(self, m):
        register_uris({"group": ["update_membership_membership"]}, m)

        response = await self.membership.update(mem_id=1, moderator=False)
        self.assertIsInstance(response, GroupMembership)

    # remove_user()
    async def test_remove_user(self, m):
        register_uris({"group": ["remove_user"], "user": ["get_by_id"]}, m)

        response_by_id = await self.membership.remove_user(1)
        self.assertIsInstance(response_by_id, dict)
        self.assertEqual(len(response_by_id), 0)

        user_obj = await self.canvas.get_user(1)
        response_by_obj = await self.membership.remove_user(user_obj)
        self.assertIsInstance(response_by_obj, dict)
        self.assertEqual(len(response_by_obj), 0)

    # remove_self()
    async def test_remove_self(self, m):
        register_uris({"group": ["remove_self"]}, m)

        response = await self.membership.remove_self()

        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 0)


@aioresponse_mock
class TestGroupCategory(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)
        with aioresponses() as m:
            register_uris({"course": ["get_by_id", "create_group_category"]}, m)

            self.course = await self.canvas.get_course(1)
            self.group_category = await self.course.create_group_category("Test String")

    async def asyncTearDown(self) -> None:
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.group_category)
        self.assertIsInstance(string, str)

    # create_group()
    async def test_create_group(self, m):
        register_uris({"group": ["category_create_group"]}, m)

        test_str = "Test Create Group"
        response = await self.group_category.create_group(name=test_str)
        self.assertIsInstance(response, Group)
        self.assertTrue(hasattr(response, "name"))
        self.assertEqual(response.name, test_str)

    # update()
    async def test_update(self, m):
        register_uris({"group": ["category_update"]}, m)

        new_name = "Test Update Category"
        response = await self.group_category.update(name=new_name)
        self.assertIsInstance(response, GroupCategory)

    # delete_category()
    async def test_delete_category(self, m):
        register_uris({"group": ["category_delete_category"]}, m)

        response = await self.group_category.delete()

        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 0)

    # get_groups()
    async def test_get_groups(self, m):
        register_uris({"group": ["category_list_groups"]}, m)

        response = self.group_category.get_groups()
        group_list = [group async for group in response]
        self.assertEqual(len(group_list), 2)
        self.assertIsInstance(group_list[0], Group)
        self.assertTrue(hasattr(group_list[0], "id"))

    # get_users()
    async def test_get_users(self, m):
        from canvasaio.user import User

        register_uris({"group": ["category_list_users"]}, m)

        response = self.group_category.get_users()
        user_list = [user async for user in response]
        self.assertEqual(len(user_list), 4)
        self.assertIsInstance(user_list[0], User)
        self.assertTrue(hasattr(user_list[0], "user_id"))

    # assign_members()
    async def test_assign_members(self, m):
        from canvasaio.progress import Progress
        from canvasaio.paginated_list import PaginatedList

        requires = {
            "group": ["category_assign_members_true", "category_assign_members_false"]
        }
        register_uris(requires, m)

        result_true = self.group_category.assign_members(sync=True)
        return_false = await self.group_category.assign_members()

        self.assertIsInstance(result_true, PaginatedList)
        self.assertIsInstance(return_false, Progress)
