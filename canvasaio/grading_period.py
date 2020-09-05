from canvasaio.canvas_object import CanvasObject
from canvasaio.exceptions import RequiredFieldMissing
from canvasaio.util import combine_kwargs


class GradingPeriod(CanvasObject):
    def __str__(self):
        return "{} ({})".format(self.title, self.id)

    async def delete(self, **kwargs):
        """
        Delete a grading period for a course.

        :calls: `DELETE /api/v1/courses/:course_id/grading_periods/:id \
        <https://canvas.instructure.com/doc/api/grading_periods.html#method.grading_periods.update>`_

        :returns: Status code 204 if delete was successful
        :rtype: int
        """
        response = await self._requester.request(
            "DELETE",
            "courses/{}/grading_periods/{}".format(self.course_id, self.id),
            _kwargs=combine_kwargs(**kwargs),
        )

        return response.status

    async def update(self, grading_period, **kwargs):
        """
        Update a grading period for a course.

        :calls: `PUT /api/v1/courses/:course_id/grading_periods/:id \
        <https://canvas.instructure.com/doc/api/grading_periods.html#method.grading_periods.update>`_

        :param grading_period: List of nested paramameters.
        :type grading_period: list[dict]

        :rtype: :class:`canvasaio.grading_period.GradingPeriod`
        """
        if isinstance(grading_period, list):
            kwargs["grading_periods"] = grading_period
        else:
            raise RequiredFieldMissing("List is required")

        if "start_date" not in kwargs["grading_periods"][0]:
            raise RequiredFieldMissing("start_date is missing")

        if "end_date" not in kwargs["grading_periods"][0]:
            raise RequiredFieldMissing("end_date is missing")

        response = await self._requester.request(
            "PUT",
            "courses/{}/grading_periods/{}".format(self.course_id, self.id),
            _kwargs=combine_kwargs(**kwargs),
        )

        response_json = await response.json()
        grading_period = response_json["grading_periods"][0]
        grading_period.update({"course_id": self.course_id})

        return GradingPeriod(self._requester, grading_period)
