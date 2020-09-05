from canvasaio.canvas_object import CanvasObject
from canvasaio.exceptions import RequiredFieldMissing
from canvasaio.util import combine_kwargs


class AppointmentGroup(CanvasObject):
    def __str__(self):
        return "{} ({})".format(self.title, self.id)

    async def delete(self, **kwargs):
        """
        Delete this appointment group.

        :calls: `DELETE /api/v1/appointment_groups/:id \
        <https://canvas.instructure.com/doc/api/appointment_groups.html#method.appointment_groups.destroy>`_

        :rtype: :class:`canvasaio.appointment_group.AppointmentGroup`
        """
        response = await self._requester.request(
            "DELETE",
            "appointment_groups/{}".format(self.id),
            _kwargs=combine_kwargs(**kwargs),
        )
        return AppointmentGroup(self._requester, await response.json())

    async def edit(self, appointment_group, **kwargs):
        """
        Modify this appointment group.

        :calls: `PUT /api/v1/appointment_groups/:id \
        <https://canvas.instructure.com/doc/api/appointment_groups.html#method.appointment_groups.update>`_

        :param appointment_group: Dict containing an array of context codes
        :type appointment_group: dict

        :rtype: :class:`canvasaio.appointment_group.AppointmentGroup`
        """
        if isinstance(appointment_group, dict) and "context_codes" in appointment_group:
            kwargs["appointment_group"] = appointment_group
        else:
            raise RequiredFieldMissing(
                "Dictionary with key 'context_codes' is required."
            )

        response = await self._requester.request(
            "PUT",
            "appointment_groups/{}".format(self.id),
            _kwargs=combine_kwargs(**kwargs),
        )

        response_json = await response.json()
        if "title" in response_json:
            super(AppointmentGroup, self).set_attributes(response_json)

        return AppointmentGroup(self._requester, response_json)
