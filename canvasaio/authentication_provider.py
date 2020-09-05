from canvasaio.canvas_object import CanvasObject
from canvasaio.util import combine_kwargs


class AuthenticationProvider(CanvasObject):
    def __str__(self):  # pragma: no cover
        return "{} ({})".format(self.auth_type, self.position)

    async  def update(self, **kwargs):
        """
        Update an authentication provider using the same options as the create endpoint

        :calls: `PUT /api/v1/accounts/:account_id/authentication_providers/:id \
        <https://canvas.instructure.com/doc/api/authentication_providers.html#method.account_authorization_configs.update>`_

        :rtype: :class:`canvasaio.authentication_provider.AuthenticationProvider`
        """
        response = await self._requester.request(
            "PUT",
            "accounts/{}/authentication_providers/{}".format(self.account_id, self.id),
            _kwargs=combine_kwargs(**kwargs),
        )

        response_json = await response.json()
        if response_json.get("auth_type"):
            super(AuthenticationProvider, self).set_attributes(response_json)

        return response_json.get("auth_type")

    async def delete(self):
        """
        Delete the config

        :calls: `DELETE /api/v1/accounts/:account_id/authentication_providers/:id \
        <https://canvas.instructure.com/doc/api/authentication_providers.html#method.account_authorization_configs.destroy>`_

        :rtype: :class:`canvasaio.authentication_provider.AuthenticationProvider`
        """
        response = await self._requester.request(
            "DELETE",
            "accounts/{}/authentication_providers/{}".format(self.account_id, self.id),
        )
        return AuthenticationProvider(self._requester, await response.json())
