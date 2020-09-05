from canvasaio.canvas_object import CanvasObject
from canvasaio.paginated_list import PaginatedList
from canvasaio.util import combine_kwargs


class Login(CanvasObject):
    def __str__(self):
        return "{} ({})".format(self.id, self.unique_id)

    async def delete(self):
        """
        Delete an existing login.

        :calls: `DELETE /api/v1/users/:user_id/logins/:id \
        <https://canvas.instructure.com/doc/api/logins.html#method.pseudonyms.destroy>`_

        :rtype: :class:`canvasaio.login.Login`
        """
        response = await self._requester.request(
            "DELETE", "users/{}/logins/{}".format(self.user_id, self.id)
        )
        return Login(self._requester, await response.json())

    async def edit(self, **kwargs):
        """
        Update an existing login for a user in the given account.

        :calls: `PUT /api/v1/accounts/:account_id/logins/:id \
        <https://canvas.instructure.com/doc/api/logins.html#method.pseudonyms.update>`_

        :rtype: :class:`canvasaio.login.Login`
        """
        response = await self._requester.request(
            "PUT",
            "accounts/{}/logins/{}".format(self.account_id, self.id),
            _kwargs=combine_kwargs(**kwargs),
        )
        return Login(self._requester, await response.json())

    def get_authentication_events(self, **kwargs):
        """
        List authentication events for a given login.

        :calls: `GET /api/v1/audit/authentication/logins/:login_id \
        <https://canvas.instructure.com/doc/api/authentications_log.html#method.authentication_audit_api.for_login>`_

        :rtype: :class:`canvasaio.paginated_list.PaginatedList` of
                :class:`canvasaio.authentication_event.AuthenticationEvent`
        """
        from canvasaio.authentication_event import AuthenticationEvent

        return PaginatedList(
            AuthenticationEvent,
            self._requester,
            "GET",
            "audit/authentication/logins/{}".format(self.id),
            _kwargs=combine_kwargs(**kwargs),
        )
