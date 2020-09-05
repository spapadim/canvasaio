from canvasaio.canvas_object import CanvasObject
from canvasaio.util import combine_kwargs


class Bookmark(CanvasObject):
    def __str__(self):
        return "{} ({})".format(self.name, self.id)

    async def delete(self, **kwargs):
        """
        Delete this bookmark.

        :calls: `DELETE /api/v1/users/self/bookmarks/:id \
        <https://canvas.instructure.com/doc/api/bookmarks.html#method.bookmarks/bookmarks.destroy>`_

        :rtype: :class:`canvasaio.bookmark.Bookmark`
        """
        response = await self._requester.request(
            "DELETE",
            "users/self/bookmarks/{}".format(self.id),
            _kwargs=combine_kwargs(**kwargs),
        )
        return Bookmark(self._requester, await response.json())

    async def edit(self, **kwargs):
        """
        Modify this bookmark.

        :calls: `PUT /api/v1/users/self/bookmarks/:id \
        <https://canvas.instructure.com/doc/api/bookmarks.html#method.bookmarks/bookmarks.update>`_

        :rtype: :class:`canvasaio.bookmark.Bookmark`
        """
        response = await self._requester.request(
            "PUT",
            "users/self/bookmarks/{}".format(self.id),
            _kwargs=combine_kwargs(**kwargs),
        )

        response_json = await response.json()
        if "name" in response_json and "url" in response_json:
            super(Bookmark, self).set_attributes(response_json)

        return Bookmark(self._requester, response_json)
