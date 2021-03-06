from canvasaio.canvas_object import CanvasObject
from canvasaio.util import combine_kwargs


class Rubric(CanvasObject):
    def __str__(self):
        return "{} ({})".format(self.title, self.id)


class RubricAssociation(CanvasObject):
    def __str__(self):
        return "{}, {}".format(self.id, self.association_type)

    async def delete(self, **kwargs):
        """
        Delete a RubricAssociation.

        :calls: `DELETE /api/v1/courses/:course_id/rubric_associations/:id \
        <https://canvas.instructure.com/doc/api/rubrics.html#method.rubric_associations.destroy>`_

        :rtype: :class:`canvasaio.rubric.RubricAssociation`
        """
        from canvasaio.rubric import RubricAssociation

        response = await self._requester.request(
            "DELETE",
            "courses/{}/rubric_associations/{}".format(self.course_id, self.id),
            _kwargs=combine_kwargs(**kwargs),
        )

        return RubricAssociation(self._requester, await response.json())

    async def update(self, **kwargs):
        """
        Update a RubricAssociation.

        :calls: `PUT /api/v1/courses/:course_id/rubric_associations/:id \
        <https://canvas.instructure.com/doc/api/rubrics.html#method.rubric_associations.update>`_

        :returns: Returns a RubricAssociation.
        :rtype: :class:`canvasaio.rubric.RubricAssociation`
        """
        from canvasaio.rubric import RubricAssociation

        response = await self._requester.request(
            "PUT",
            "courses/{}/rubric_associations/{}".format(self.course_id, self.id),
            _kwargs=combine_kwargs(**kwargs),
        )

        response_json = await response.json()
        response_json.update({"course_id": self.course_id})
        if "association_type" in response_json:
            super(RubricAssociation, self).set_attributes(response_json)

        return self
