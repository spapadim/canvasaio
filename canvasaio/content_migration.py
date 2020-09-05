from canvasaio.canvas_object import CanvasObject
from canvasaio.paginated_list import PaginatedList
from canvasaio.util import combine_kwargs, obj_or_id


class ContentMigration(CanvasObject):
    def __str__(self):
        return "{} {}".format(self.migration_type_title, self.id)

    @property
    def _parent_id(self):
        """
        Return the id of the account, course, group, or user that spawned
        this content migration.

        :rtype: int
        """
        if hasattr(self, "course_id"):
            return self.course_id
        elif hasattr(self, "group_id"):
            return self.group_id
        elif hasattr(self, "account_id"):
            return self.account_id
        elif hasattr(self, "user_id"):
            return self.user_id
        else:
            raise ValueError(
                "Content Migration does not have an account_id, course_id, group_id or user_id"
            )

    @property
    def _parent_type(self):
        """
        Return whether the content migration was spawned from a course or group.

        :rtype: str
        """
        if hasattr(self, "course_id"):
            return "course"
        elif hasattr(self, "group_id"):
            return "group"
        elif hasattr(self, "account_id"):
            return "account"
        elif hasattr(self, "user_id"):
            return "user"
        else:
            raise ValueError(
                "Content Migration does not have an account_id, course_id, group_id or user_id"
            )

    async def get_migration_issue(self, migration_issue, **kwargs):
        """
        List a single issue for this content migration.

        :calls: `GET
            /api/v1/accounts/:account_id/content_migrations/:content_migration_id/migration_issues/:id
            <https://canvas.instructure.com/doc/api/content_migrations.html#method.migration_issues.show>`_

            or `GET
            /api/v1/courses/:course_id/content_migrations/:content_migration_id/migration_issues/:id
            <https://canvas.instructure.com/doc/api/content_migrations.html#method.migration_issues.show>`_

            or `GET
            /api/v1/groups/:group_id/content_migrations/:content_migration_id/migration_issues/:id
            <https://canvas.instructure.com/doc/api/content_migrations.html#method.migration_issues.show>`_

            or `GET
            /api/v1/users/:user_id/content_migrations/:content_migration_id/migration_issues/:id
            <https://canvas.instructure.com/doc/api/content_migrations.html#method.migration_issues.show>`_

        :param migration_issue: The object or ID of the issue to retrieve.
        :type migration_issue: int, str or :class:`canvasaio.content_migration.ContentMigration`

        :rtype: :class:`canvasaio.content_migration.MigrationIssue`
        """
        from canvasaio.content_migration import MigrationIssue

        migration_issue_id = obj_or_id(
            migration_issue, "migration_issue", (MigrationIssue,)
        )

        response = await self._requester.request(
            "GET",
            "{}s/{}/content_migrations/{}/migration_issues/{}".format(
                self._parent_type, self._parent_id, self.id, migration_issue_id
            ),
            _kwargs=combine_kwargs(**kwargs),
        )

        response_json = await response.json()
        response_json.update(
            {
                "context_type": self._parent_type,
                "context_id": self._parent_id,
                "content_migration_id": self.id,
            }
        )

        return MigrationIssue(self._requester, response_json)

    def get_migration_issues(self, **kwargs):
        """
        List issues for this content migration

        :calls:
            `GET
            /api/v1/accounts/:account_id/content_migrations/:content_migration_id/migration_issues
            <https://canvas.instructure.com/doc/api/content_migrations.html#method.migration_issues.index>`_

            or `GET
            /api/v1/courses/:course_id/content_migrations/:content_migration_id/migration_issues
            <https://canvas.instructure.com/doc/api/content_migrations.html#method.migration_issues.index>`_

            or `GET
            /api/v1/groups/:group_id/content_migrations/:content_migration_id/migration_issues
            <https://canvas.instructure.com/doc/api/content_migrations.html#method.migration_issues.index>`_

            or `GET
            /api/v1/users/:user_id/content_migrations/:content_migration_id/migration_issues
            <https://canvas.instructure.com/doc/api/content_migrations.html#method.migration_issues.index>`_

        :rtype: :class:`canvasaio.content_migration.MigrationIssue`
        """
        from canvasaio.content_migration import MigrationIssue

        return PaginatedList(
            MigrationIssue,
            self._requester,
            "GET",
            "{}s/{}/content_migrations/{}/migration_issues/".format(
                self._parent_type, self._parent_id, self.id
            ),
            {
                "context_type": self._parent_type,
                "context_id": self._parent_id,
                "content_migration_id": self.id,
            },
            _kwargs=combine_kwargs(**kwargs),
        )

    async def get_parent(self, **kwargs):
        """
        Return the object that spawned this content migration.

        :rtype: :class:`canvasaio.group.Account`,
            or :class:`canvasaio.course.Course`,
            or :class:`canvasaio.course.Group`,
            or :class:`canvasaio.course.User`
        """
        from canvasaio.group import Group
        from canvasaio.course import Course
        from canvasaio.account import Account
        from canvasaio.user import User

        response = await self._requester.request(
            "GET",
            "{}s/{}".format(self._parent_type, self._parent_id),
            _kwargs=combine_kwargs(**kwargs),
        )

        if self._parent_type == "group":
            return Group(self._requester, await response.json())
        elif self._parent_type == "course":
            return Course(self._requester, await response.json())
        elif self._parent_type == "account":
            return Account(self._requester, await response.json())
        elif self._parent_type == "user":
            return User(self._requester, await response.json())

    async def get_progress(self, **kwargs):
        """
        Get the progress of the current content migration.

        :calls: `GET /api/v1/progress/:id
            <https://canvas.instructure.com/doc/api/progress.html#method.progress.show>`_

        :rtype: :class:`canvasaio.progress.Progress`
        """

        from canvasaio.progress import Progress

        progress_id = self.progress_url.split("/")[-1]

        response = await self._requester.request(
            "GET", "progress/{}".format(progress_id), _kwargs=combine_kwargs(**kwargs)
        )
        return Progress(self._requester, await response.json())

    async def update(self, **kwargs):
        """
        Update an existing content migration.

        :calls: `PUT /api/v1/accounts/:account_id/content_migrations/:id
            <https://canvas.instructure.com/doc/api/content_migrations.html#method.content_migrations.update>`_

            or `PUT /api/v1/courses/:course_id/content_migrations/:id
            <https://canvas.instructure.com/doc/api/content_migrations.html#method.content_migrations.update>`_

            or `PUT /api/v1/groups/:group_id/content_migrations/:id
            <https://canvas.instructure.com/doc/api/content_migrations.html#method.content_migrations.update>`_

            or `PUT /api/v1/users/:user_id/content_migrations/:id
            <https://canvas.instructure.com/doc/api/content_migrations.html#method.content_migrations.update>`_

        :returns: True if the migration was updated, False otherwise.
        :rtype: bool
        """
        response = await self._requester.request(
            "PUT",
            "{}s/{}/content_migrations/{}".format(
                self._parent_type, self._parent_id, self.id
            ),
            _kwargs=combine_kwargs(**kwargs),
        )

        response_json = await response.json()
        if "migration_type" in response_json:
            super(ContentMigration, self).set_attributes(response_json)
            return True
        else:
            return False


class MigrationIssue(CanvasObject):
    def __str__(self):
        return "{}: {}".format(self.id, self.description)

    async def update(self, **kwargs):
        """
        Update an existing migration issue.

        :calls: `PUT
            /api/v1/accounts/:account_id/content_migrations/:content_migration_id/migration_issues/:id
            <https://canvas.instructure.com/doc/api/content_migrations.html#method.migration_issues.update>`_
            or `PUT
            /api/v1/courses/:course_id/content_migrations/:content_migration_id/migration_issues/:id
            <https://canvas.instructure.com/doc/api/content_migrations.html#method.migration_issues.update>`_
            or `PUT
            /api/v1/groups/:group_id/content_migrations/:content_migration_id/migration_issues/:id
            <https://canvas.instructure.com/doc/api/content_migrations.html#method.migration_issues.update>`_
            or `PUT
            /api/v1/users/:user_id/content_migrations/:content_migration_id/migration_issues/:id
            <https://canvas.instructure.com/doc/api/content_migrations.html#method.migration_issues.update>`_

        :returns: True if the issue was updated, False otherwise.
        :rtype: bool
        """
        response = await self._requester.request(
            "PUT",
            "{}s/{}/content_migrations/{}/migration_issues/{}".format(
                self.context_type, self.context_id, self.content_migration_id, self.id
            ),
            _kwargs=combine_kwargs(**kwargs),
        )

        response_json = await response.json()
        if "workflow_state" in response_json:
            super(MigrationIssue, self).set_attributes(response_json)
            return True
        else:
            return False


class Migrator(CanvasObject):
    def __str__(self):
        return "{}".format(self.type)
