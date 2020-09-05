from canvasaio.calendar_event import CalendarEvent
from canvasaio.canvas_object import CanvasObject
from canvasaio.communication_channel import CommunicationChannel
from canvasaio.feature import Feature, FeatureFlag
from canvasaio.folder import Folder
from canvasaio.paginated_list import PaginatedList
from canvasaio.license import License
from canvasaio.upload import Uploader
from canvasaio.usage_rights import UsageRights
from canvasaio.util import combine_kwargs, obj_or_id, obj_or_str


class User(CanvasObject):
    def __str__(self):
        return "{} ({})".format(self.name, self.id)

    async def add_observee(self, observee_id, **kwargs):
        """
        Registers a user as being observed by the given user.

        :calls: `PUT /api/v1/users/:user_id/observees/:observee_id \
        <https://canvas.instructure.com/doc/api/user_observees.html#method.user_observees.update>`_

        :param observee_id: The login id for the user to observe.
        :type observee_id: int
        :rtype: :class: `canvasaio.user.User`
        """

        response = await self._requester.request(
            "PUT",
            "users/{}/observees/{}".format(self.id, observee_id),
            _kwargs=combine_kwargs(**kwargs),
        )
        return User(self._requester, await response.json())

    async def add_observee_with_credentials(self, **kwargs):
        """
        Register the given user to observe another user, given the observee's credentials.

        :calls: `POST /api/v1/users/:user_id/observees \
        <https://canvas.instructure.com/doc/api/user_observees.html#method.user_observees.create>`_

        :rtype: :class:`canvasaio.user.User`
        """

        response = await self._requester.request(
            "POST",
            "users/{}/observees".format(self.id),
            _kwargs=combine_kwargs(**kwargs),
        )
        return User(self._requester, await response.json())

    async def create_communication_channel(self, **kwargs):
        """
        Create a communication channel for this user

        :calls: `POST /api/v1/users/:user_id/communication_channels \
        <https://canvas.instructure.com/doc/api/communication_channels.html#method.communication_channels.create>`_

        :rtype: :class:`canvasaio.communication_channel.CommunicationChannel`
        """
        response = await self._requester.request(
            "POST",
            "users/{}/communication_channels".format(self.id),
            _kwargs=combine_kwargs(**kwargs),
        )

        return CommunicationChannel(self._requester, await response.json())

    async def create_content_migration(self, migration_type, **kwargs):
        """
        Create a content migration.

        :calls: `POST /api/v1/users/:user_id/content_migrations \
        <https://canvas.instructure.com/doc/api/content_migrations.html#method.content_migrations.create>`_

        :param migration_type: The migrator type to use in this migration
        :type migration_type: str or :class:`canvasaio.content_migration.Migrator`

        :rtype: :class:`canvasaio.content_migration.ContentMigration`
        """
        from canvasaio.content_migration import ContentMigration, Migrator

        if isinstance(migration_type, Migrator):
            kwargs["migration_type"] = migration_type.type
        elif isinstance(migration_type, str):
            kwargs["migration_type"] = migration_type
        else:
            raise TypeError("Parameter migration_type must be of type Migrator or str")

        response = await self._requester.request(
            "POST",
            "users/{}/content_migrations".format(self.id),
            _kwargs=combine_kwargs(**kwargs),
        )

        response_json = await response.json()
        response_json.update({"user_id": self.id})

        return ContentMigration(self._requester, response_json)

    async def create_folder(self, name, **kwargs):
        """
        Creates a folder in this user.

        :calls: `POST /api/v1/users/:user_id/folders \
        <https://canvas.instructure.com/doc/api/files.html#method.folders.create>`_

        :param name: The name of the folder.
        :type name: str
        :rtype: :class:`canvasaio.folder.Folder`
        """
        response = await self._requester.request(
            "POST",
            "users/{}/folders".format(self.id),
            name=name,
            _kwargs=combine_kwargs(**kwargs),
        )
        return Folder(self._requester, await response.json())

    async def edit(self, **kwargs):
        """
        Modify this user's information.

        :calls: `PUT /api/v1/users/:id \
        <https://canvas.instructure.com/doc/api/users.html#method.users.update>`_

        :rtype: :class:`canvasaio.user.User`
        """
        response = await self._requester.request(
            "PUT", "users/{}".format(self.id), _kwargs=combine_kwargs(**kwargs)
        )
        super(User, self).set_attributes(await response.json())
        return self

    async def export_content(self, export_type, **kwargs):
        """
        Begin a content export job for a user.

        :calls: `POST /api/v1/users/:user_id/content_exports\
        <https://canvas.instructure.com/doc/api/content_exports.html#method.content_exports_api.create>`_

        :param export_type: The type of content to export.
        :type export_type: str

        :rtype: :class:`canvasaio.content_export.ContentExport`
        """
        from canvasaio.content_export import ContentExport

        kwargs["export_type"] = export_type

        response = await self._requester.request(
            "POST",
            "users/{}/content_exports".format(self.id),
            _kwargs=combine_kwargs(**kwargs),
        )
        return ContentExport(self._requester, await response.json())

    def get_assignments(self, course, **kwargs):
        """
        Return the list of assignments for this user if the current
        user (the API key owner) has rights to view. See List assignments for valid arguments.

        :calls: `GET /api/v1/users/:user_id/courses/:course_id/assignments \
        <https://canvas.instructure.com/doc/api/assignments.html#method.assignments_api.user_index>`_

        :param course: The object or ID of the course to retrieve.
        :type course: :class:`canvasaio.course.Course` or int

        :rtype: :class:`canvasaio.paginated_list.PaginatedList` of
            :class:`canvasaio.assignment.Assignment`
        """
        from canvasaio.assignment import Assignment
        from canvasaio.course import Course

        course_id = obj_or_id(course, "course", (Course,))

        return PaginatedList(
            Assignment,
            self._requester,
            "GET",
            "users/{}/courses/{}/assignments".format(self.id, course_id),
            _kwargs=combine_kwargs(**kwargs),
        )

    def get_authentication_events(self, **kwargs):
        """
        List authentication events for a given user.

        :calls: `GET /api/v1/audit/authentication/users/:user_id \
        <https://canvas.instructure.com/doc/api/authentications_log.html#method.authentication_audit_api.for_user>`_

        :rtype: :class:`canvasaio.paginated_list.PaginatedList` of
                :class:`canvasaio.authentication_event.AuthenticationEvent`
        """
        from canvasaio.authentication_event import AuthenticationEvent

        return PaginatedList(
            AuthenticationEvent,
            self._requester,
            "GET",
            "audit/authentication/users/{}".format(self.id),
            _kwargs=combine_kwargs(**kwargs),
        )

    def get_avatars(self, **kwargs):
        """
        Retrieve the possible user avatar options that can be set with the user update endpoint.

        :calls: `GET /api/v1/users/:user_id/avatars \
        <https://canvas.instructure.com/doc/api/users.html#method.profile.profile_pics>`_

        :rtype: :class:`canvasaio.paginated_list.PaginatedList` of
            :class:`canvasaio.avatar.Avatar`
        """
        from canvasaio.avatar import Avatar

        return PaginatedList(
            Avatar,
            self._requester,
            "GET",
            "users/{}/avatars".format(self.id),
            _kwargs=combine_kwargs(**kwargs),
        )

    def get_calendar_events_for_user(self, **kwargs):
        """
        List calendar events that the current user can view or manage.

        :calls: `GET /api/v1/users/:user_id/calendar_events \
        <https://canvas.instructure.com/doc/api/calendar_events.html#method.calendar_events_api.user_index>`_

        :rtype: :class:`canvasaio.paginated_list.PaginatedList` of
            :class:`canvasaio.calendar_event.CalendarEvent`
        """
        return PaginatedList(
            CalendarEvent,
            self._requester,
            "GET",
            "users/{}/calendar_events".format(self.id),
            _kwargs=combine_kwargs(**kwargs),
        )

    def get_closed_poll_sessions(self, **kwargs):
        """
        Returns a paginated list of all closed poll sessions available to the current user.

        :calls: `GET /api/v1/poll_sessions/closed \
        <https://canvas.instructure.com/doc/api/poll_sessions.html#method.polling/poll_sessions.closed>`_

        :rtype: :class:`canvasaio.paginated_list.PaginatedList` of
            :class:`canvasaio.poll_session.PollSession`
        """
        from canvasaio.poll_session import PollSession

        return PaginatedList(
            PollSession,
            self._requester,
            "GET",
            "poll_sessions/closed",
            _root="poll_sessions",
            _kwargs=combine_kwargs(**kwargs),
        )

    async def get_color(self, asset_string, **kwargs):
        """
        Return the custom colors that have been saved by this user for a given context.

        The `asset_string` parameter should be in the format 'context_id', for example 'course_42'.

        :calls: `GET /api/v1/users/:id/colors/:asset_string \
        <https://canvas.instructure.com/doc/api/users.html#method.users.get_custom_color>`_

        :param asset_string: The asset to retrieve the color from.
        :type asset_string: str
        :rtype: dict
        """
        response = await self._requester.request(
            "GET",
            "users/{}/colors/{}".format(self.id, asset_string),
            _kwargs=combine_kwargs(**kwargs),
        )
        return await response.json()

    async def get_colors(self, **kwargs):
        """
        Return all custom colors that have been saved by this user.

        :calls: `GET /api/v1/users/:id/colors \
        <https://canvas.instructure.com/doc/api/users.html#method.users.get_custom_colors>`_

        :rtype: dict
        """
        response = await self._requester.request(
            "GET",
            "users/{}/colors".format(self.id),
            _kwargs=combine_kwargs(**kwargs),
        )
        return await response.json()

    def get_communication_channels(self, **kwargs):
        """
        List communication channels for the specified user, sorted by
        position.

        :calls: `GET /api/v1/users/:user_id/communication_channels \
        <https://canvas.instructure.com/doc/api/communication_channels.html#method.communication_channels.index>`_

        :rtype: :class:`canvasaio.paginated_list.PaginatedList` of
            :class:`canvasaio.communication_channel.CommunicationChannel`
        """
        return PaginatedList(
            CommunicationChannel,
            self._requester,
            "GET",
            "users/{}/communication_channels".format(self.id),
            _kwargs=combine_kwargs(**kwargs),
        )

    async def get_content_export(self, content_export, **kwargs):
        """
        Return information about a single content export.

        :calls: `GET /api/v1/users/:user_id/content_exports/:id\
        <https://canvas.instructure.com/doc/api/content_exports.html#method.content_exports_api.show>`_

        :param content_export: The object or ID of the content export to show.
        :type content_export: int or :class:`canvasaio.content_export.ContentExport`

        :rtype: :class:`canvasaio.content_export.ContentExport`
        """
        from canvasaio.content_export import ContentExport

        export_id = obj_or_id(content_export, "content_export", (ContentExport,))

        response = await self._requester.request(
            "GET",
            "users/{}/content_exports/{}".format(self.id, export_id),
            _kwargs=combine_kwargs(**kwargs),
        )

        return ContentExport(self._requester, await response.json())

    def get_content_exports(self, **kwargs):
        """
        Return a paginated list of the past and pending content export jobs for a user.

        :calls: `GET /api/v1/users/:user_id/content_exports\
        <https://canvas.instructure.com/doc/api/content_exports.html#method.content_exports_api.index>`_

        :rtype: :class:`canvasaio.paginated_list.PaginatedList` of
            :class:`canvasaio.content_export.ContentExport`
        """
        from canvasaio.content_export import ContentExport

        return PaginatedList(
            ContentExport,
            self._requester,
            "GET",
            "users/{}/content_exports".format(self.id),
            kwargs=combine_kwargs(**kwargs),
        )

    async def get_content_migration(self, content_migration, **kwargs):
        """
        Retrive a content migration by its ID

        :calls: `GET /api/v1/users/:user_id/content_migrations/:id \
        <https://canvas.instructure.com/doc/api/content_migrations.html#method.content_migrations.show>`_

        :param content_migration: The object or ID of the content migration to retrieve.
        :type content_migration: int, str or :class:`canvasaio.content_migration.ContentMigration`

        :rtype: :class:`canvasaio.content_migration.ContentMigration`
        """
        from canvasaio.content_migration import ContentMigration

        migration_id = obj_or_id(
            content_migration, "content_migration", (ContentMigration,)
        )

        response = await self._requester.request(
            "GET",
            "users/{}/content_migrations/{}".format(self.id, migration_id),
            _kwargs=combine_kwargs(**kwargs),
        )

        response_json = await response.json()
        response_json.update({"user_id": self.id})

        return ContentMigration(self._requester, response_json)

    def get_content_migrations(self, **kwargs):
        """
        List content migrations that the current account can view or manage.

        :calls: `GET /api/v1/users/:user_id/content_migrations/ \
        <https://canvas.instructure.com/doc/api/content_migrations.html#method.content_migrations.index>`_

        :rtype: :class:`canvasaio.paginated_list.PaginatedList` of
            :class:`canvasaio.content_migration.ContentMigration`
        """
        from canvasaio.content_migration import ContentMigration

        return PaginatedList(
            ContentMigration,
            self._requester,
            "GET",
            "users/{}/content_migrations".format(self.id),
            {"user_id": self.id},
            _kwargs=combine_kwargs(**kwargs),
        )

    def get_courses(self, **kwargs):
        """
        Retrieve all courses this user is enrolled in.

        :calls: `GET /api/v1/users/:user_id/courses \
        <https://canvas.instructure.com/doc/api/courses.html#method.courses.user_index>`_

        :rtype: :class:`canvasaio.paginated_list.PaginatedList` of
            :class:`canvasaio.course.Course`
        """
        from canvasaio.course import Course

        return PaginatedList(
            Course,
            self._requester,
            "GET",
            "users/{}/courses".format(self.id),
            _kwargs=combine_kwargs(**kwargs),
        )

    def get_enabled_features(self, **kwargs):
        """
        Lists all of the enabled features for a user.

        :calls: `GET /api/v1/users/:user_id/features/enabled \
        <https://canvas.instructure.com/doc/api/feature_flags.html#method.feature_flags.enabled_features>`_

        :rtype: :class:`canvasaio.paginated_list.PaginatedList` of
            :class:`canvasaio.feature.Feature`
        """
        return PaginatedList(
            Feature,
            self._requester,
            "GET",
            "users/{}/features/enabled".format(self.id),
            {"user_id": self.id},
            _kwargs=combine_kwargs(**kwargs),
        )

    def get_enrollments(self, **kwargs):
        """
        List all of the enrollments for this user.

        :calls: `GET /api/v1/users/:user_id/enrollments \
        <https://canvas.instructure.com/doc/api/enrollments.html#method.enrollments_api.index>`_

        :rtype: :class:`canvasaio.paginated_list.PaginatedList` of
            :class:`canvasaio.enrollment.Enrollment`
        """
        from canvasaio.enrollment import Enrollment

        return PaginatedList(
            Enrollment,
            self._requester,
            "GET",
            "users/{}/enrollments".format(self.id),
            _kwargs=combine_kwargs(**kwargs),
        )

    async def get_feature_flag(self, feature, **kwargs):
        """
        Returns the feature flag that applies to the given user.

        :calls: `GET /api/v1/users/:user_id/features/flags/:feature \
        <https://canvas.instructure.com/doc/api/feature_flags.html#method.feature_flags.show>`_

        :param feature: The feature object or name of the feature to retrieve.
        :type feature: :class:`canvasaio.feature.Feature` or str

        :rtype: :class:`canvasaio.feature.FeatureFlag`
        """
        feature_name = obj_or_str(feature, "name", (Feature,))

        response = await self._requester.request(
            "GET",
            "users/{}/features/flags/{}".format(self.id, feature_name),
            _kwargs=combine_kwargs(**kwargs),
        )
        return FeatureFlag(self._requester, await response.json())

    def get_features(self, **kwargs):
        """
        Lists all of the features for this user.

        :calls: `GET /api/v1/users/:user_id/features \
        <https://canvas.instructure.com/doc/api/feature_flags.html#method.feature_flags.index>`_

        :rtype: :class:`canvasaio.paginated_list.PaginatedList` of
            :class:`canvasaio.feature.Feature`
        """
        return PaginatedList(
            Feature,
            self._requester,
            "GET",
            "users/{}/features".format(self.id),
            {"user_id": self.id},
            _kwargs=combine_kwargs(**kwargs),
        )

    async def get_file(self, file, **kwargs):
        """
        Return the standard attachment json object for a file.

        :calls: `GET /api/v1/users/:user_id/files/:id \
        <https://canvas.instructure.com/doc/api/files.html#method.files.api_show>`_

        :param file: The object or ID of the file to retrieve.
        :type file: :class:`canvasaio.file.File` or int

        :rtype: :class:`canvasaio.file.File`
        """
        from canvasaio.file import File

        file_id = obj_or_id(file, "file", (File,))

        response = await self._requester.request(
            "GET",
            "users/{}/files/{}".format(self.id, file_id),
            _kwargs=combine_kwargs(**kwargs),
        )
        return File(self._requester, await response.json())

    def get_files(self, **kwargs):
        """
        Returns the paginated list of files for the user.

        :calls: `GET /api/v1/users/:user_id/files \
            <https://canvas.instructure.com/doc/api/files.html#method.files.api_index>`_

        :rtype: :class:`canvasaio.paginated_list.PaginatedList` of
            :class:`canvasaio.file.File`
        """
        from canvasaio.file import File

        return PaginatedList(
            File,
            self._requester,
            "GET",
            "users/{}/files".format(self.id),
            _kwargs=combine_kwargs(**kwargs),
        )

    async def get_folder(self, folder, **kwargs):
        """
        Returns the details for a user's folder

        :calls: `GET /api/v1/users/:user_id/folders/:id \
        <https://canvas.instructure.com/doc/api/files.html#method.folders.show>`_

        :param folder: The object or ID of the folder to retrieve.
        :type folder: :class:`canvasaio.folder.Folder` or int

        :rtype: :class:`canvasaio.folder.Folder`
        """
        from canvasaio.folder import Folder

        folder_id = obj_or_id(folder, "folder", (Folder,))

        response = await self._requester.request(
            "GET",
            "users/{}/folders/{}".format(self.id, folder_id),
            _kwargs=combine_kwargs(**kwargs),
        )
        return Folder(self._requester, await response.json())

    def get_folders(self, **kwargs):
        """
        Returns the paginated list of all folders for the given user. This will be returned as a
        flat list containing all subfolders as well.

        :calls: `GET /api/v1/users/:user_id/folders \
        <https://canvas.instructure.com/doc/api/files.html#method.folders.list_all_folders>`_

        :rtype: :class:`canvasaio.paginated_list.PaginatedList` of
            :class:`canvasaio.folder.Folder`
        """
        return PaginatedList(
            Folder,
            self._requester,
            "GET",
            "users/{}/folders".format(self.id),
            _kwargs=combine_kwargs(**kwargs),
        )

    def get_licenses(self, **kwargs):
        """
        Returns a paginated list of the licenses that can be applied to the
        files under the user scope

        :calls: `GET /api/v1/users/:user_id/content_licenses \
        <https://canvas.instructure.com/doc/api/files.html#method.usage_rights.licenses>`_

        :rtype: :class:`canvasaio.paginated_list.PaginatedList` of
            :class:`canvasaio.license.License`
        """

        return PaginatedList(
            License,
            self._requester,
            "GET",
            "users/{}/content_licenses".format(self.id),
            _kwargs=combine_kwargs(**kwargs),
        )

    def get_migration_systems(self, **kwargs):
        """
        Return a list of migration systems.

        :calls: `GET /api/v1/users/:user_id/content_migrations/migrators \
        <https://canvas.instructure.com/doc/api/content_migrations.html#method.content_migrations.available_migrators>`_

        :rtype: :class:`canvasaio.paginated_list.PaginatedList` of
            :class:`canvasaio.content_migration.Migrator`
        """
        from canvasaio.content_migration import Migrator

        return PaginatedList(
            Migrator,
            self._requester,
            "GET",
            "users/{}/content_migrations/migrators".format(self.id),
            _kwargs=combine_kwargs(**kwargs),
        )

    def get_missing_submissions(self, **kwargs):
        """
        Retrieve all past-due assignments for which the student does not
        have a submission.

        :calls: `GET /api/v1/users/:user_id/missing_submissions \
        <https://canvas.instructure.com/doc/api/users.html#method.users.missing_submissions>`_

        :rtype: :class:`canvasaio.paginated_list.PaginatedList` of
            :class:`canvasaio.assignment.Assignment`
        """
        from canvasaio.assignment import Assignment

        return PaginatedList(
            Assignment,
            self._requester,
            "GET",
            "users/{}/missing_submissions".format(self.id),
            _kwargs=combine_kwargs(**kwargs),
        )

    def get_observees(self, **kwargs):
        """
        List the users that the given user is observing

        :calls:  `GET /api/v1/users/:user_id/observees \
        <https://canvas.instructure.com/doc/api/user_observees.html#method.user_observees.index>`_

        :rtype: :class:`canvasaio.paginated_list.PaginatedList` of
            :class:`canvasaio.user.User`
        """

        return PaginatedList(
            User,
            self._requester,
            "GET",
            "users/{}/observees".format(self.id),
            _kwargs=combine_kwargs(**kwargs),
        )

    def get_open_poll_sessions(self, **kwargs):
        """
        Returns a paginated list of all opened poll sessions available to the current user.

        :calls: `GET /api/v1/poll_sessions/opened \
        <https://canvas.instructure.com/doc/api/poll_sessions.html#method.polling/poll_sessions.opened>`_

        :rtype: :class:`canvasaio.paginated_list.PaginatedList` of
            :class:`canvasaio.poll_session.PollSession`
        """
        from canvasaio.poll_session import PollSession

        return PaginatedList(
            PollSession,
            self._requester,
            "GET",
            "poll_sessions/opened",
            _root="poll_sessions",
            _kwargs=combine_kwargs(**kwargs),
        )

    def get_page_views(self, **kwargs):
        """
        Retrieve this user's page views.

        :calls: `GET /api/v1/users/:user_id/page_views \
        <https://canvas.instructure.com/doc/api/users.html#method.page_views.index>`_

        :rtype: :class:`canvasaio.paginated_list.PaginatedList` of
            :class:`canvasaio.course.PageView`
        """
        from canvasaio.page_view import PageView

        return PaginatedList(
            PageView,
            self._requester,
            "GET",
            "users/{}/page_views".format(self.id),
            _kwargs=combine_kwargs(**kwargs),
        )

    async def get_profile(self, **kwargs):
        """
        Retrieve this user's profile.

        :calls: `GET /api/v1/users/:user_id/profile \
        <https://canvas.instructure.com/doc/api/users.html#method.profile.settings>`_

        :rtype: dict
        """
        response = await self._requester.request("GET", "users/{}/profile".format(self.id))
        return await response.json()

    def get_user_logins(self, **kwargs):
        """
        Given a user ID, return that user's logins for the given account.

        :calls: `GET /api/v1/users/:user_id/logins \
        <https://canvas.instructure.com/doc/api/logins.html#method.pseudonyms.index>`_

        :rtype: :class:`canvasaio.paginated_list.PaginatedList` of
            :class:`canvasaio.login.Login`
        """
        from canvasaio.login import Login

        return PaginatedList(
            Login,
            self._requester,
            "GET",
            "users/{}/logins".format(self.id),
            _kwargs=combine_kwargs(**kwargs),
        )

    async def merge_into(self, destination_user, **kwargs):
        """
        Merge this user into another user.

        :calls: `PUT /api/v1/users/:id/merge_into/:destination_user_id \
        <https://canvas.instructure.com/doc/api/users.html#method.users.merge_into>`_

        :param destination_user: The object or ID of the user to merge into.
        :type destination_user: :class:`canvasaio.user.User` or int

        :rtype: :class:`canvasaio.user.User`
        """
        dest_user_id = obj_or_id(destination_user, "destination_user", (User,))

        response = await self._requester.request(
            "PUT",
            "users/{}/merge_into/{}".format(self.id, dest_user_id),
            _kwargs=combine_kwargs(**kwargs),
        )
        super(User, self).set_attributes(await response.json())
        return self

    async def remove_observee(self, observee_id, **kwargs):
        """
        Unregisters a user as being observed by the given user.

        :calls: `DELETE /api/v1/users/:user_id/observees/:observee_id \
        <https://canvas.instructure.com/doc/api/user_observees.html#method.user_observees.destroy>`_

        :param observee_id: The login id for the user to observe.
        :type observee_id: int
        :rtype: :class: `canvasaio.user.User`
        """

        response = await self._requester.request(
            "DELETE",
            "users/{}/observees/{}".format(self.id, observee_id),
            _kwargs=combine_kwargs(**kwargs),
        )
        return User(self._requester, await response.json())

    async def remove_usage_rights(self, **kwargs):
        """
        Changes the usage rights for specified files that are under the user scope

        :calls: `DELETE /api/v1/users/:user_id/usage_rights \
        <https://canvas.instructure.com/doc/api/files.html#method.usage_rights.remove_usage_rights>`_

        :rtype: dict
        """

        response = await self._requester.request(
            "DELETE",
            "users/{}/usage_rights".format(self.id),
            _kwargs=combine_kwargs(**kwargs),
        )

        return await response.json()

    def resolve_path(self, full_path=None, **kwargs):
        """
        Returns the paginated list of all of the folders in the given
        path starting at the user root folder. Returns root folder if called
        with no arguments.

        :calls: `GET /api/v1/users/:user_id/folders/by_path/*full_path \
        <https://canvas.instructure.com/doc/api/files.html#method.folders.resolve_path>`_

        :param full_path: Full path to resolve, relative to user root.
        :type full_path: string

        :rtype: :class:`canvasaio.paginated_list.PaginatedList` of
            :class:`canvasaio.folder.Folder`
        """

        if full_path:
            return PaginatedList(
                Folder,
                self._requester,
                "GET",
                "users/{0}/folders/by_path/{1}".format(self.id, full_path),
                _kwargs=combine_kwargs(**kwargs),
            )
        else:
            return PaginatedList(
                Folder,
                self._requester,
                "GET",
                "users/{0}/folders/by_path".format(self.id),
                _kwargs=combine_kwargs(**kwargs),
            )

    async def set_usage_rights(self, **kwargs):
        """
        Changes the usage rights for specified files that are under the user scope

        :calls: `PUT /api/v1/users/:user_id/usage_rights \
        <https://canvas.instructure.com/doc/api/files.html#method.usage_rights.set_usage_rights>`_

        :rtype: :class:`canvasaio.usage_rights.UsageRights`
        """

        response = await self._requester.request(
            "PUT",
            "users/{}/usage_rights".format(self.id),
            _kwargs=combine_kwargs(**kwargs),
        )

        return UsageRights(self._requester, await response.json())

    async def show_observee(self, observee_id, **kwargs):
        """
        Gets information about an observed user.

        :calls: `GET /api/v1/users/:user_id/observees/:observee_id \
        <https://canvas.instructure.com/doc/api/user_observees.html#method.user_observees.show>`_

        :param observee_id: The login id for the user to observe.
        :type observee_id: int
        :rtype: :class: `canvasaio.user.User`
        """

        response = await self._requester.request(
            "GET",
            "users/{}/observees/{}".format(self.id, observee_id),
            _kwargs=combine_kwargs(**kwargs),
        )
        return User(self._requester, await response.json())

    async def update_color(self, asset_string, hexcode, **kwargs):
        """
        Update a custom color for this user for a given context.

        This allows colors for the calendar and elsewhere to be customized on a user basis.

        The `asset_string` parameter should be in the format 'context_id', for example 'course_42'.
        The `hexcode` parameter need not include the '#'.

        :calls: `PUT /api/v1/users/:id/colors/:asset_string \
        <https://canvas.instructure.com/doc/api/users.html#method.users.set_custom_color>`_

        :param asset_string: The asset to modify the color for.
        :type asset_string: str
        :param hexcode: The hexcode of the color to use.
        :type hexcode: str
        :rtype: dict
        """
        kwargs["hexcode"] = hexcode
        response = await self._requester.request(
            "PUT",
            "users/{}/colors/{}".format(self.id, asset_string),
            _kwargs=combine_kwargs(**kwargs),
        )
        return await response.json()

    async def update_settings(self, **kwargs):
        """
        Update this user's settings.

        :calls: `PUT /api/v1/users/:id/settings \
        <https://canvas.instructure.com/doc/api/users.html#method.users.settings>`_

        :rtype: dict
        """
        response = await self._requester.request(
            "PUT", "users/{}/settings".format(self.id), _kwargs=combine_kwargs(**kwargs)
        )
        return await response.json()

    async def upload(self, file, **kwargs):
        """
        Upload a file for a user.

        NOTE: You *must* have authenticated with this user's API key to
        upload on their behalf no matter what permissions the issuer of the
        request has.

        :calls: `POST /api/v1/users/:user_id/files \
        <https://canvas.instructure.com/doc/api/users.html#method.users.create_file>`_

        :param file: The file or path of the file to upload.
        :type file: file or str
        :returns: True if the file uploaded successfully, False otherwise, \
                    and the JSON response from the API.
        :rtype: tuple
        """
        return await Uploader(
            self._requester, "users/{}/files".format(self.id), file, **kwargs
        ).start()


class UserDisplay(CanvasObject):
    def __str__(self):
        return "{}".format(self.display_name)
