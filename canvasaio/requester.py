from datetime import datetime
import logging
from pprint import pformat

from typing import Optional

import aiohttp

from canvasaio.exceptions import (
    BadRequest,
    CanvasException,
    Conflict,
    Forbidden,
    InvalidAccessToken,
    ResourceDoesNotExist,
    Unauthorized,
    UnprocessableEntity,
)
from canvasaio.util import clean_headers


logger = logging.getLogger(__name__)


class Requester(object):
    """
    Responsible for handling HTTP requests.
    """

    def __init__(self, base_url, access_token):
        """
        :param base_url: The base URL of the Canvas instance's API.
        :type base_url: str
        :param access_token: The API key to authenticate requests with.
        :type access_token: str
        """
        # Preserve the original base url and add "/api/v1" to it
        self.original_url = base_url
        self.base_url = base_url + "/api/v1/"
        self.access_token = access_token
        self.__session = None  # defer construction of ClientSession, since that needs to be done in async context
        self._cache = []

    @property
    async def _session(self):
        """
        Deferred creation of aiohttp.ClientSession, since this needs to be done from async context
        """
        if self.__session == None:
            self.__session = aiohttp.ClientSession()
        return self.__session

    async def close(self):
        import traceback
        if self.__session != None:
            await self.__session.close()

    async def _delete_request(self, url, headers, data=None, **kwargs):
        """
        Issue a DELETE request to the specified endpoint with the data provided.

        :param url: The URL to request.
        :type url: str
        :param headers: The HTTP headers to send with this request.
        :type headers: dict
        :param data: The data to send with this request.
        :type data: dict
        """
        session = await self._session
        return await session.delete(url, headers=headers, data=data)

    async def _get_request(self, url, headers, params=None, **kwargs):
        """
        Issue a GET request to the specified endpoint with the data provided.

        :param url: The URL to request.
        :type url: str
        :param headers: The HTTP headers to send with this request.
        :type headers: dict
        :param params: The parameters to send with this request.
        :type params: dict
        """
        session = await self._session
        return await session.get(url, headers=headers, params=params)

    async def _patch_request(self, url, headers, data=None, **kwargs):
        """
        Issue a PATCH request to the specified endpoint with the data provided.

        :param url: The URL to request.
        :type url: str
        :param headers: The HTTP headers to send with this request.
        :type headers: dict
        :param data: The data to send with this request.
        :type data: dict
        """
        session = await self._session
        return await session.patch(url, headers=headers, data=data)

    async def _post_request(self, url, headers, data=None, json=False):
        """
        Issue a POST request to the specified endpoint with the data provided.

        :param url: The URL to request.
        :type url: str
        :param headers: The HTTP headers to send with this request.
        :type headers: dict
        :param data: The data to send with this request.
        :type data: dict
        :param json: Whether or not to send the data as json
        :type json: bool
        """
        session = await self._session

        if json:
            return await session.post(url, headers=headers, json=dict(data))

        # Grab file from data.
        files = None
        for field, value in data:
            if field == "file":
                if isinstance(value, dict):
                    files = value
                else:
                    files = {"file": value}
                break

        # Remove file entry from data.
        # XXX This contradicts type of "data" in docstring (can't hash a slice...)
        #   So, apparently data must me a list of tuples
        # XXX It appears that this functionality isn't actually used by the API...?
        data[:] = [tup for tup in data if tup[0] != "file"]

        # TODO Check if this can be simplified
        #    According to request lib docs, files must be a dict with file-like value type
        #   If that is the case (i.e., passing string values would raise error), then we
        #   can perhaps simply concatenate dict(data) + files as the aiohttp lib data parameter
        #   Instead, we're playing safe (since I have no tide to investigate -- e.g., can a
        #   file attachment and a form field share names?)
        form_data = aiohttp.FormData()
        for field, value in data:
            form_data.add_field(field, value)
        if files is not None:
            for filename, value in files.items():
                form_data.add_field(filename, value, filename=filename)

        return await session.post(url, headers=headers, data=form_data)

    async def _put_request(self, url, headers, data=None, **kwargs):
        """
        Issue a PUT request to the specified endpoint with the data provided.

        :param url: The URL to request.
        :type url: str
        :param headers: The HTTP headers to send with this request.
        :type headers: dict
        :param data: The data to send with this request.
        :type data: dict
        """
        session = await self._session
        return await session.put(url, headers=headers, data=data)

    async def request(
        self,
        method: str,
        endpoint: Optional[str] = None,
        headers: Optional[dict] = None,
        use_auth: bool = True,
        _url: Optional[str] = None,
        _kwargs: list = None,
        json: bool = False,
        **kwargs
    ) -> aiohttp.ClientResponse:
        """
        Make a request to the Canvas API and return the response.

        :param method: The HTTP method for the request.
        :type method: str
        :param endpoint: The endpoint to call.
        :type endpoint: str
        :param headers: Optional HTTP headers to be sent with the request.
        :type headers: dict
        :param use_auth: Optional flag to remove the authentication
            header from the request.
        :type use_auth: bool
        :param _url: Optional argument to send a request to a URL
            outside of the Canvas API. If this is selected and an
            endpoint is provided, the endpoint will be ignored and
            only the _url argument will be used.
        :type _url: str
        :param _kwargs: A list of 2-tuples representing processed
            keyword arguments to be sent to Canvas as params or data.
        :type _kwargs: `list`
        :param json: Whether or not to treat the data as json instead of form data.
            currently only the POST request of GraphQL is using this parameter.
            For all other methods it's just passed and ignored.
        :type json: `bool`
        :rtype: str
        """
        full_url = _url if _url else "{}{}".format(self.base_url, endpoint)

        if not headers:
            headers = {}

        if use_auth:
            auth_header = {"Authorization": "Bearer {}".format(self.access_token)}
            headers.update(auth_header)

        # Convert kwargs into list of 2-tuples and combine with _kwargs.
        _kwargs = _kwargs or []
        _kwargs.extend(kwargs.items())

        # Do any final argument processing before sending to request method.
        for i, kwarg in enumerate(_kwargs):
            kw, arg = kwarg

            # Convert boolean objects to a lowercase string.
            if isinstance(arg, bool):
                _kwargs[i] = (kw, str(arg).lower())

            # Convert any datetime objects into ISO 8601 formatted strings.
            elif isinstance(arg, datetime):
                _kwargs[i] = (kw, arg.isoformat())

        # print(f"DBG request() _kwargs = {_kwargs}")

        # Determine the appropriate request method.
        if method == "GET":
            req_method = self._get_request
        elif method == "POST":
            req_method = self._post_request
        elif method == "DELETE":
            req_method = self._delete_request
        elif method == "PUT":
            req_method = self._put_request
        elif method == "PATCH":
            req_method = self._patch_request
        else:
            raise ValueError(f"Invalid HTTP request method: {method}")

        # Call the request method
        logger.info("Request: {method} {url}".format(method=method, url=full_url))
        logger.debug(
            "Headers: {headers}".format(headers=pformat(clean_headers(headers)))
        )

        if _kwargs:
            logger.debug("Data: {data}".format(data=pformat(_kwargs)))

        response = await req_method(full_url, headers, _kwargs, json=json)
        logger.info(
            "Response: {method} {url} {status}".format(
                method=method, url=full_url, status=response.status
            )
        )
        logger.debug(
            "Headers: {headers}".format(
                headers=pformat(clean_headers(response.headers))
            )
        )

        try:
            logger.debug("Data: {data}".format(data=pformat(await response.json())))
        except ValueError:
            logger.debug("Data: {data}".format(data=pformat(await response.text())))

        # Add response to internal cache
        if len(self._cache) > 4:
            self._cache.pop()

        self._cache.insert(0, response)

        # Raise for status codes
        if response.status == 400:
            raise BadRequest(await response.text())
        elif response.status == 401:
            if "WWW-Authenticate" in response.headers:
                raise InvalidAccessToken(await response.json())
            else:
                raise Unauthorized(await response.json())
        elif response.status == 403:
            raise Forbidden(await response.text())
        elif response.status == 404:
            raise ResourceDoesNotExist("Not Found")
        elif response.status == 409:
            raise Conflict(await response.text())
        elif response.status == 422:
            raise UnprocessableEntity(await response.text())
        elif response.status > 400:
            # generic catch-all for error codes
            raise CanvasException(
                "Encountered an error: status code {}".format(response.status)
            )

        return response
