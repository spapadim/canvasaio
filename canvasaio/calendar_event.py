from canvasaio.canvas_object import CanvasObject
from canvasaio.util import combine_kwargs


class CalendarEvent(CanvasObject):
    def __str__(self):
        return "{} ({})".format(self.title, self.id)

    async def delete(self, **kwargs):
        """
        Delete this calendar event.

        :calls: `DELETE /api/v1/calendar_events/:id \
        <https://canvas.instructure.com/doc/api/calendar_events.html#method.calendar_events_api.destroy>`_

        :rtype: :class:`canvasaio.calendar_event.CalendarEvent`
        """
        response = await self._requester.request(
            "DELETE",
            "calendar_events/{}".format(self.id),
            _kwargs=combine_kwargs(**kwargs),
        )
        return CalendarEvent(self._requester, await response.json())

    async def edit(self, **kwargs):
        """
        Modify this calendar event.

        :calls: `PUT /api/v1/calendar_events/:id \
        <https://canvas.instructure.com/doc/api/calendar_events.html#method.calendar_events_api.update>`_

        :rtype: :class:`canvasaio.calendar_event.CalendarEvent`
        """
        response = await self._requester.request(
            "PUT",
            "calendar_events/{}".format(self.id),
            _kwargs=combine_kwargs(**kwargs),
        )

        response_json = await response.json()
        if "title" in response_json:
            super(CalendarEvent, self).set_attributes(response_json)

        return CalendarEvent(self._requester, response_json)
