from canvasaio.bookmark import Bookmark
from canvasaio.course import Course
from canvasaio.favorite import Favorite
from canvasaio.group import Group
from canvasaio.paginated_list import PaginatedList
from canvasaio.user import User
from canvasaio.util import combine_kwargs, obj_or_id


class CurrentUser(User):
    def __str__(self):
        return "{} ({})".format(self.name, self.id)

    async def add_favorite_course(self, course, use_sis_id=False, **kwargs):
        """
        Add a course to the current user's favorites. If the course is already
        in the user's favorites, nothing happens.

        :calls: `POST /api/v1/users/self/favorites/courses/:id \
        <https://canvas.instructure.com/doc/api/favorites.html#method.favorites.add_favorite_course>`_

        :param course: The course or ID/SIS ID of the course.
        :type course: :class:`canvasaio.course.Course` or int

        :param use_sis_id: Whether or not `course` is an sis ID.
            Defaults to `False`.
        :type use_sis_id: bool

        :rtype: :class:`canvasaio.favorite.Favorite`
        """
        if use_sis_id:
            course_id = course
            uri_str = "users/self/favorites/courses/sis_course_id:{}"
        else:
            course_id = obj_or_id(course, "course", (Course,))
            uri_str = "users/self/favorites/courses/{}"

        response = await self._requester.request(
            "POST", uri_str.format(course_id), _kwargs=combine_kwargs(**kwargs)
        )
        return Favorite(self._requester, await response.json())

    async def add_favorite_group(self, group, use_sis_id=False, **kwargs):
        """
        Add a group to the current user's favorites. If the group is already
        in the user's favorites, nothing happens.

        :calls: `POST /api/v1/users/self/favorites/groups/:id \
        <https://canvas.instructure.com/doc/api/favorites.html#method.favorites.add_favorite_groups>`_

        :param group: The ID or SIS ID of the group.
        :type group: :class:`canvasaio.group.Group` or int

        :param use_sis_id: Whether or not `group` is an sis ID.
            Defaults to `False`.
        :type use_sis_id: bool

        :rtype: :class:`canvasaio.favorite.Favorite`
        """
        if use_sis_id:
            group_id = group
            uri_str = "users/self/favorites/groups/sis_group_id:{}"
        else:
            group_id = obj_or_id(group, "group", (Group,))
            uri_str = "users/self/favorites/groups/{}"

        response = await self._requester.request(
            "POST", uri_str.format(group_id), _kwargs=combine_kwargs(**kwargs)
        )
        return Favorite(self._requester, await response.json())

    async def create_bookmark(self, name, url, **kwargs):
        """
        Create a new Bookmark.

        :calls: `POST /api/v1/users/self/bookmarks \
        <https://canvas.instructure.com/doc/api/bookmarks.html#method.bookmarks/bookmarks.create>`_

        :param name: The name of the bookmark.
        :type name: `str`
        :param url: The url of the bookmark.
        :type url: `str`
        :rtype: :class:`canvasaio.bookmark.Bookmark`
        """
        from canvasaio.bookmark import Bookmark

        response = await self._requester.request(
            "POST",
            "users/self/bookmarks",
            name=name,
            url=url,
            _kwargs=combine_kwargs(**kwargs),
        )

        return Bookmark(self._requester, await response.json())

    async def get_bookmark(self, bookmark, **kwargs):
        """
        Return single Bookmark by id

        :calls: `GET /api/v1/users/self/bookmarks/:id \
        <https://canvas.instructure.com/doc/api/bookmarks.html#method.bookmarks/bookmarks.show>`_

        :param bookmark: The object or ID of the bookmark.
        :type bookmark: :class:`canvasaio.bookmark.Bookmark` or int

        :rtype: :class:`canvasaio.bookmark.Bookmark`
        """
        from canvasaio.bookmark import Bookmark

        bookmark_id = obj_or_id(bookmark, "bookmark", (Bookmark,))

        response = await self._requester.request(
            "GET",
            "users/self/bookmarks/{}".format(bookmark_id),
            _kwargs=combine_kwargs(**kwargs),
        )
        return Bookmark(self._requester, await response.json())

    def get_bookmarks(self, **kwargs):
        """
        List bookmarks that the current user can view or manage.

        :calls: `GET /api/v1/users/self/bookmarks \
        <https://canvas.instructure.com/doc/api/bookmarks.html#method.bookmarks/bookmarks.index>`_

        :rtype: :class:`canvasaio.paginated_list.PaginatedList` of
            :class:`canvasaio.bookmark.Bookmark`
        """
        return PaginatedList(Bookmark, self._requester, "GET", "users/self/bookmarks")

    def get_favorite_courses(self, **kwargs):
        """
        Retrieve the paginated list of favorite courses for the current user.
        If the user has not chosen any favorites,
        then a selection of currently enrolled courses will be returned.

        :calls: `GET /api/v1/users/self/favorites/courses \
        <https://canvas.instructure.com/doc/api/favorites.html#method.favorites.list_favorite_courses>`_

        :rtype: :class:`canvasaio.paginated_list.PaginatedList` of
            :class:`canvasaio.course.Course`
        """

        return PaginatedList(
            Course,
            self._requester,
            "GET",
            "users/self/favorites/courses",
            _kwargs=combine_kwargs(**kwargs),
        )

    def get_favorite_groups(self, **kwargs):
        """
        Retrieve the paginated list of favorite groups for the current user.
        If the user has not chosen any favorites, then a selection of groups
        that the user is a member of will be returned.

        :calls: `GET /api/v1/users/self/favorites/groups \
        <https://canvas.instructure.com/doc/api/favorites.html#method.favorites.list_favorite_groups>`_

        :rtype: :class:`canvasaio.paginated_list.PaginatedList` of
            :class:`canvasaio.group.Group`
        """

        return PaginatedList(
            Group,
            self._requester,
            "GET",
            "users/self/favorites/groups",
            _kwargs=combine_kwargs(**kwargs),
        )

    def get_groups(self, **kwargs):
        """
        Return the list of active groups for the user.

        :calls: `GET /api/v1/users/self/groups \
        <https://canvas.instructure.com/doc/api/groups.html#method.groups.index>`_

        :rtype: :class:`canvasaio.paginated_list.PaginatedList` of :class:`canvasaio.group.Group`
        """
        from canvasaio.group import Group

        return PaginatedList(
            Group,
            self._requester,
            "GET",
            "users/self/groups",
            _kwargs=combine_kwargs(**kwargs),
        )

    async def reset_favorite_courses(self, **kwargs):
        """
        Reset the current user's course favorites to the default
        automatically generated list of enrolled courses

        :calls: `DELETE /api/v1/users/self/favorites/courses \
        <https://canvas.instructure.com/doc/api/favorites.html#method.favorites.reset_course_favorites>`_

        :returns: `True` if reset correctly, `False` otherwise.
        :rtype: bool
        """

        response = await self._requester.request(
            "DELETE", "users/self/favorites/courses", _kwargs=combine_kwargs(**kwargs)
        )
        return (await response.json()).get("message") == "OK"

    async def reset_favorite_groups(self, **kwargs):
        """
        Reset the current user's group favorites to the default
        automatically generated list of enrolled groups

        :calls: `DELETE /api/v1/users/self/favorites/groups \
        <https://canvas.instructure.com/doc/api/favorites.html#method.favorites.reset_groups_favorites>`_

        :returns: `True` if reset correctly, `False` otherwise.
        :rtype: bool
        """

        response = await self._requester.request(
            "DELETE", "users/self/favorites/groups", _kwargs=combine_kwargs(**kwargs)
        )
        return (await response.json()).get("message") == "OK"
