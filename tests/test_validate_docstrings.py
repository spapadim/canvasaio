import re
import io

from canvasaio.canvas_object import CanvasObject
from canvasaio.folder import Folder
from canvasaio.util import combine_kwargs, obj_or_id
from scripts.validate_docstrings import validate_method

import unittest

from aioresponses import aioresponses

from tests.util import aioresponse_mock


# test_endpoint_docstrings
@aioresponse_mock
class TestValidateDocstrings(unittest.IsolatedAsyncioTestCase):
    async def test_validate_method_verb_mismatch(self, m):
        url = "https://canvas.instructure.com/doc/api/files.html#method.files.destroy>"
        register_doc_uri(url, m)
        self.assertFalse(await validate_method(ExampleMethods.verb_mismatch, True))

    async def test_validate_method_invalid_verb(self, m):
        url = "https://canvas.instructure.com/doc/api/files.html#method.files.destroy"
        register_doc_uri(url, m)
        self.assertFalse(await validate_method(ExampleMethods.invalid_verb, True))

    async def test_validate_method_no_api_call(self, m):
        self.assertTrue(await validate_method(ExampleMethods.no_api_call, True))

    async def test_validate_method_good_docstring(self, m):
        url = "https://canvas.instructure.com/doc/api/files.html#method.files.destroy"
        register_doc_uri(url, m)
        self.assertTrue(await validate_method(ExampleMethods.good_docstring, True))

    async def test_validate_method_multiple_endpoints(self, m):
        url = "https://canvas.instructure.com/doc/api/files.html#method.folders.show"
        register_doc_uri(url, m)
        self.assertTrue(await validate_method(ExampleMethods.multiple_endpoints, True))

    async def test_validate_method_multiline_URL(self, m):
        url = (
            "https://canvas.instructure.com/doc/api/notification_preferences.html"
            "#method.notification_preferences.index"
        )
        register_doc_uri(url, m)
        self.assertTrue(await validate_method(ExampleMethods.multiline_URL, True))

    async def test_validate_method_invalid_URL(self, m):
        url = "https://canvas.instructure.com/doc/api/404.html"
        register_doc_uri(url, m, code=404)
        self.assertFalse(await validate_method(ExampleMethods.invalid_URL, True))

    async def test_validate_method_missing_endpoint_URL(self, m):
        url = "https://canvas.instructure.com/doc/api/files.html"
        register_doc_uri(url, m)
        self.assertFalse(await validate_method(ExampleMethods.missing_endpoint_URL, True))

    async def test_validate_method_endpoint_URL_invalid(self, m):
        url = "https://canvas.instructure.com/doc/api/files.html#invalid"
        register_doc_uri(url, m)
        self.assertFalse(await validate_method(ExampleMethods.endpoint_invalid, True))

    async def test_validate_method_not_an_endpoint(self, m):
        url = (
            "https://canvas.instructure.com/doc/api/notification_preferences.html"
            "#NotificationPreference"
        )
        register_doc_uri(url, m)
        self.assertFalse(await validate_method(ExampleMethods.not_an_endpoint, True))


def register_doc_uri(url, m: aioresponses, code=200):
    url_groups = re.search(r"(.*\/)([^\/]*)\.html", url)
    if not url_groups:
        return
    file_name = url_groups.group(2)

    with io.open(
        "tests/fixtures/{}.html".format(file_name), "r", encoding="utf-8"
    ) as file:
        data = file.read()

    m.get(
        url_groups.group(1) + url_groups.group(2) + ".html",
        body=data,
        content_type="text/plain",
        status=code,
    )


class ExampleMethods(CanvasObject):
    async def verb_mismatch(self):
        """
        :calls: `PUT /api/v1/files/:id  \
        <https://canvas.instructure.com/doc/api/files.html#method.files.destroy>`_

        :rtype: :class:`canvasaio.file.File`
        """
        response = await self._requester.request("DELETE", "files/{}".format(self.id))
        return ExampleMethods(self._requester, await response.json())

    async def invalid_verb(self):
        """
        Delete this file.

        :calls: `BELETE /api/v1/files/:id  \
        <https://canvas.instructure.com/doc/api/files.html#method.files.destroy>`_

        :rtype: :class:`canvasaio.file.File`
        """
        response = await self._requester.request("DELETE", "files/{}".format(self.id))
        return ExampleMethods(self._requester, await response.json())

    def no_api_call(self):
        """
        Empty docstring.
        """
        return False

    async def good_docstring(self):
        """
        Delete this file.

        :calls: `DELETE /api/v1/files/:id  \
        <https://canvas.instructure.com/doc/api/files.html#method.files.destroy>`_

        :rtype: :class:`canvasaio.file.File`
        """
        response = await self._requester.request("DELETE", "files/{}".format(self.id))
        return ExampleMethods(self._requester, await response.json())

    async def multiple_endpoints(self, folder):
        """
        Return the details for a folder

        :calls: `GET /api/v1/folders/:id \
        <https://canvas.instructure.com/doc/api/files.html#method.folders.show>`_

        :param folder: The object or ID of the folder to retrieve.
        :type folder: :class:`canvasaio.folder.Folder` or int

        :rtype: :class:`canvasaio.folder.Folder`
        """
        folder_id = obj_or_id(folder, "folder", (Folder,))

        response = await self.__requester.request("GET", "folders/{}".format(folder_id))
        return Folder(self.__requester, await response.json())

    async def multiline_URL(self, **kwargs):
        """
        Fetch all preferences for the given communication channel.

        :calls: `GET
            /api/v1/users/:user_id/communication_channels/:communication_channel_id/ \
                notification_preferences \
        <https://canvas.instructure.com/doc/api/notification_preferences.html#method.notification_preferences.index>`_

        :rtype: `list`
        """
        response = await self._requester.request(
            "GET",
            "users/{}/communication_channels/{}/notification_preferences".format(
                self.user_id, self.id
            ),
            _kwargs=combine_kwargs(**kwargs),
        )

        return (await response.json())["notification_preferences"]

    def non_api_call(self):
        """
        Kick off uploading process. Handles open/closing file if a path
        is passed.

        :calls: request_upload_token
        :returns: True if the file uploaded successfully, False \
            otherwise, and the JSON response from the API.
        :rtype: tuple
        """
        pass

    async def invalid_URL(self):
        """
        Delete this file.

        :calls: `DELETE /api/v1/files/:id  \
        <https://canvas.instructure.com/doc/api/404.html>`_

        :rtype: :class:`canvasaio.file.File`
        """
        response = await self._requester.request("DELETE", "files/{}".format(self.id))
        return ExampleMethods(self._requester, await response.json())

    async def missing_endpoint_URL(self, folder):
        """
        Return the details for a folder

        :calls: `GET /api/v1/folders/:id \
        <https://canvas.instructure.com/doc/api/files.html>`_

        :param folder: The object or ID of the folder to retrieve.
        :type folder: :class:`canvasaio.folder.Folder` or int

        :rtype: :class:`canvasaio.folder.Folder`
        """
        folder_id = obj_or_id(folder, "folder", (Folder,))

        response = await self.__requester.request("GET", "folders/{}".format(folder_id))
        return Folder(self.__requester, await response.json())

    async def endpoint_invalid(self, folder):
        """
        Return the details for a folder

        :calls: `GET /api/v1/folders/:id \
        <https://canvas.instructure.com/doc/api/files.html#invalid>`_

        :param folder: The object or ID of the folder to retrieve.
        :type folder: :class:`canvasaio.folder.Folder` or int

        :rtype: :class:`canvasaio.folder.Folder`
        """
        folder_id = obj_or_id(folder, "folder", (Folder,))

        response = await self.__requester.request("GET", "folders/{}".format(folder_id))
        return Folder(self.__requester, await response.json())

    async def not_an_endpoint(self, **kwargs):
        """
        Fetch all preferences for the given communication channel.

        :calls: `GET
            /api/v1/users/:user_id/communication_channels/:communication_channel_id/ \
                notification_preferences \
        <https://canvas.instructure.com/doc/api/notification_preferences.html#NotificationPreference>`_

        :rtype: `list`
        """
        response = await self._requester.request(
            "GET",
            "users/{}/communication_channels/{}/notification_preferences".format(
                self.user_id, self.id
            ),
            _kwargs=combine_kwargs(**kwargs),
        )

        return (await response.json())["notification_preferences"]
