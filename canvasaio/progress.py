from canvasaio.canvas_object import CanvasObject
from canvasaio.util import combine_kwargs


class Progress(CanvasObject):
    def __str__(self):
        return "{} - {} ({})".format(self.tag, self.workflow_state, self.id)

    async def query(self, **kwargs):
        """
        Return completion and status information about an asynchronous job.

        :calls: `GET /api/v1/progress/:id \
        <https://canvas.instructure.com/doc/api/progress.html#method.progress.show>`_

        :rtype: :class:`canvasaio.progress.Progress`
        """
        response = await self._requester.request(
            "GET",
            "progress/{}".format(self.id),
            _kwargs=combine_kwargs(**kwargs),
        )
        response_json = await response.json()

        super(Progress, self).set_attributes(response_json)

        return Progress(self._requester, response_json)
