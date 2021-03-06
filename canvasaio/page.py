from canvasaio.canvas_object import CanvasObject
from canvasaio.paginated_list import PaginatedList
from canvasaio.util import combine_kwargs, obj_or_id


class Page(CanvasObject):
    def __str__(self):
        return "{} ({})".format(self.title, self.url)

    async def delete(self, **kwargs):
        """
        Delete this page.

        :calls: `DELETE /api/v1/courses/:course_id/pages/:url \
        <https://canvas.instructure.com/doc/api/pages.html#method.wiki_pages_api.destroy>`_

        :rtype: :class:`canvasaio.page.Page`
        """
        response = await self._requester.request(
            "DELETE",
            "courses/{}/pages/{}".format(self.course_id, self.url),
            _kwargs=combine_kwargs(**kwargs),
        )
        return Page(self._requester, await response.json())

    async def edit(self, **kwargs):
        """
        Update the title or the contents of a specified wiki
        page.

        :calls: `PUT /api/v1/courses/:course_id/pages/:url \
        <https://canvas.instructure.com/doc/api/pages.html#method.wiki_pages_api.update>`_

        :rtype: :class:`canvasaio.page.Page`
        """
        response = await self._requester.request(
            "PUT",
            "{}s/{}/pages/{}".format(self.parent_type, self.parent_id, self.url),
            _kwargs=combine_kwargs(**kwargs),
        )

        page_json = await response.json()
        page_json.update({"course_id": self.course_id})
        super(Page, self).set_attributes(page_json)

        return self

    async def get_parent(self, **kwargs):
        """
        Return the object that spawned this page.

        :calls: `GET /api/v1/groups/:group_id \
            <https://canvas.instructure.com/doc/api/groups.html#method.groups.show>`_
            or :calls: `GET /api/v1/courses/:id \
            <https://canvas.instructure.com/doc/api/courses.html#method.courses.show>`_

        :rtype: :class:`canvasaio.group.Group` or :class:`canvasaio.course.Course`
        """
        from canvasaio.group import Group
        from canvasaio.course import Course

        response = await self._requester.request(
            "GET",
            "{}s/{}".format(self.parent_type, self.parent_id),
            _kwargs=combine_kwargs(**kwargs),
        )

        if self.parent_type == "group":
            return Group(self._requester, await response.json())
        elif self.parent_type == "course":
            return Course(self._requester, await response.json())

    async def get_revision_by_id(self, revision, **kwargs):
        """
        Retrieve the contents of the revision by the id.

        :calls: `GET /api/v1/courses/:course_id/pages/:url/revisions/:revision_id \
        <https://canvas.instructure.com/doc/api/pages.html#method.wiki_pages_api.show_revision>`_

        :param revision: The object or ID of a specified revision.
        :type revision: :class:`canvasaio.pagerevision.PageRevision` or int

        :returns: Contents of the page revision.
        :rtype: :class:`canvasaio.pagerevision.PageRevision`
        """
        revision_id = obj_or_id(revision, "revision", (PageRevision,))

        response = await self._requester.request(
            "GET",
            "{}s/{}/pages/{}/revisions/{}".format(
                self.parent_type, self.parent_id, self.url, revision_id
            ),
            _kwargs=combine_kwargs(**kwargs),
        )
        pagerev_json = await response.json()
        if self.parent_type == "group":
            pagerev_json.update({"group_id": self.id})
        elif self.parent_type == "course":
            pagerev_json.update({"course_id": self.id})

        return PageRevision(self._requester, pagerev_json)

    def get_revisions(self, **kwargs):
        """
        List the revisions of a page.

        :calls: `GET /api/v1/courses/:course_id/pages/:url/revisions \
        <https://canvas.instructure.com/doc/api/pages.html#method.wiki_pages_api.revisions>`_

        :rtype: :class:`canvasaio.paginated_list.PaginatedList` of
            :class:`canvasaio.pagerevision.PageRevision`
        """
        return PaginatedList(
            PageRevision,
            self._requester,
            "GET",
            "{}s/{}/pages/{}/revisions".format(
                self.parent_type, self.parent_id, self.url
            ),
            _kwargs=combine_kwargs(**kwargs),
        )

    @property
    def parent_id(self):
        """
        Return the id of the course or group that spawned this page.

        :rtype: int
        """
        if hasattr(self, "course_id"):
            return self.course_id
        elif hasattr(self, "group_id"):
            return self.group_id
        else:
            raise ValueError("Page does not have a course_id or group_id")

    @property
    def parent_type(self):
        """
        Return whether the page was spawned from a course or group.

        :rtype: str
        """
        if hasattr(self, "course_id"):
            return "course"
        elif hasattr(self, "group_id"):
            return "group"
        else:
            raise ValueError("ExternalTool does not have a course_id or group_id")

    async def revert_to_revision(self, revision, **kwargs):
        """
        Revert the page back to a specified revision.

        :calls: `POST /api/v1/courses/:course_id/pages/:url/revisions/:revision_id \
        <https://canvas.instructure.com/doc/api/pages.html#method.wiki_pages_api.revert>`_

        :param revision: The object or ID of a specified revision.
        :type revision: :class:`canvasaio.pagerevision.PageRevision` or int

        :returns: Contents of the page revision.
        :rtype: :class:`canvasaio.pagerevision.PageRevision`
        """
        revision_id = obj_or_id(revision, "revision", (PageRevision,))
        response = await self._requester.request(
            "POST",
            "{}s/{}/pages/{}/revisions/{}".format(
                self.parent_type, self.parent_id, self.url, revision_id
            ),
            _kwargs=combine_kwargs(**kwargs),
        )
        pagerev_json = await response.json()
        pagerev_json.update({"{self.parent_type}_id": self.parent_id})

        return PageRevision(self._requester, pagerev_json)

    async def show_latest_revision(self, **kwargs):
        """
        Retrieve the contents of the latest revision.

        :calls: `GET /api/v1/courses/:course_id/pages/:url/revisions/latest \
        <https://canvas.instructure.com/doc/api/pages.html#method.wiki_pages_api.show_revision>`_

        :rtype: :class:`canvasaio.pagerevision.PageRevision`
        """
        response = await self._requester.request(
            "GET",
            "{}s/{}/pages/{}/revisions/latest".format(
                self.parent_type, self.parent_id, self.url
            ),
            _kwargs=combine_kwargs(**kwargs),
        )
        return PageRevision(self._requester, await response.json())


class PageRevision(CanvasObject):
    def __str__(self):
        return "{} ({})".format(self.updated_at, self.revision_id)

    async def get_parent(self, **kwargs):
        """
        Return the object that spawned this page.

        :calls: `GET /api/v1/groups/:group_id \
            <https://canvas.instructure.com/doc/api/groups.html#method.groups.show>`_
            or :calls: `GET /api/v1/courses/:id \
            <https://canvas.instructure.com/doc/api/courses.html#method.courses.show>`_

        :rtype: :class:`canvasaio.group.Group` or :class:`canvasaio.course.Course`
        """
        from canvasaio.group import Group
        from canvasaio.course import Course

        response = await self._requester.request(
            "GET",
            "{}s/{}".format(self.parent_type, self.parent_id),
            _kwargs=combine_kwargs(**kwargs),
        )

        if self.parent_type == "group":
            return Group(self._requester, await response.json())
        elif self.parent_type == "course":
            return Course(self._requester, await response.json())

    @property
    def parent_id(self):
        """
        Return the id of the course or group that spawned this page.

        :rtype: int
        """
        if hasattr(self, "course_id"):
            return self.course_id
        elif hasattr(self, "group_id"):
            return self.group_id
        else:
            raise ValueError("Page does not have a course_id or group_id")

    @property
    def parent_type(self):
        """
        Return whether the page was spawned from a course or group.

        :rtype: str
        """
        if hasattr(self, "course_id"):
            return "course"
        elif hasattr(self, "group_id"):
            return "group"
        else:
            raise ValueError("ExternalTool does not have a course_id or group_id")
