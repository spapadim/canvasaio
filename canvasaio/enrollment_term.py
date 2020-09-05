from canvasaio.canvas_object import CanvasObject
from canvasaio.util import combine_kwargs


class EnrollmentTerm(CanvasObject):
    def __str__(self):
        return "{} ({})".format(self.name, self.id)

    async def delete(self):
        """
        Delete this Enrollment Term.

        :calls: `DELETE /api/v1/accounts/:account_id/terms/:id \
        <https://canvas.instructure.com/doc/api/enrollment_terms.html#method.terms.destroy>`_

        :rtype: :class:`canvasaio.enrollment_term.EnrollmentTerm`
        """
        response = await self._requester.request(
            "DELETE", "accounts/{}/terms/{}".format(self.account_id, self.id)
        )
        return EnrollmentTerm(self._requester, await response.json())

    async def edit(self, **kwargs):
        """
        Modify this Enrollment Term.

        :calls: `PUT /api/v1/accounts/:account_id/terms/:id \
        <https://canvas.instructure.com/doc/api/enrollment_terms.html#method.terms.update>`_

        :rtype: :class:`canvasaio.enrollment_term.EnrollmentTerm`
        """
        response = await self._requester.request(
            "PUT",
            "accounts/{}/terms/{}".format(self.account_id, self.id),
            _kwargs=combine_kwargs(**kwargs),
        )

        return EnrollmentTerm(self._requester, await response.json())
