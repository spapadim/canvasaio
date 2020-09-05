from datetime import datetime
import unittest
from urllib.parse import quote
import re

from aioresponses import aioresponses, CallbackResult

from canvasaio import Canvas
from canvasaio.exceptions import (
    BadRequest,
    CanvasException,
    Conflict,
    InvalidAccessToken,
    ResourceDoesNotExist,
    Unauthorized,
    UnprocessableEntity,
)
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestRequester(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)
        self.requester = self.canvas._Canvas__requester

    async def asyncTearDown(self):
        await self.canvas.close()

    # request()
    async def test_request_get(self, m):
        register_uris({"requests": ["get"]}, m)

        response = await self.requester.request("GET", "fake_get_request")
        self.assertEqual(response.status, 200)

    async def test_request_get_datetime(self, m: aioresponses):
        date = datetime.today()

        async def callback(url, params, **kwargs):
            self.assertEqual(1, len(params))
            param_name, param_value = params[0]
            self.assertEqual("date", param_name)
            self.assertEqual(date.isoformat(), param_value)  # XXX does not test URL-quoting (should be ok) and .lower()
            return CallbackResult(status=200)

        m.add(
            re.compile(re.escape(settings.BASE_URL) + r'/api/v1/test\?date=(.+)$'),
            method="GET",
            callback=callback,
        )

        response = await self.requester.request("GET", "test", date=date)
        self.assertEqual(response.status, 200)

    async def test_request_post(self, m):
        register_uris({"requests": ["post"]}, m)

        response = await self.requester.request("POST", "fake_post_request")
        self.assertEqual(response.status, 200)

    async def test_request_post_datetime(self, m):
        date = datetime.today()

        async def callback(url, data, **kwargs):
            self.assertEqual(1, len(data._fields))
            field_type_options, field_headers, field_value = data._fields[0]
            self.assertEqual("date", field_type_options["name"])
            self.assertEqual(date.isoformat(), field_value)
            return CallbackResult(status=200)

        m.add(
            settings.BASE_URL + "/api/v1/test",
            method="POST",
            callback=callback,
        )

        response = await self.requester.request("POST", "test", date=date)
        self.assertEqual(response.status, 200)

    async def test_request_delete(self, m):
        register_uris({"requests": ["delete"]}, m)

        response = await self.requester.request("DELETE", "fake_delete_request")
        self.assertEqual(response.status, 200)

    async def test_request_patch(self, m):
        register_uris({"requests": ["patch"]}, m)

        response = await self.requester.request("PATCH", "fake_patch_request")
        self.assertEqual(response.status, 200)

    async def test_request_put(self, m):
        register_uris({"requests": ["put"]}, m)

        response = await self.requester.request("PUT", "fake_put_request")
        self.assertEqual(response.status, 200)

    async def test_request_cache(self, m):
        register_uris({"requests": ["get"]}, m)

        response = await self.requester.request("GET", "fake_get_request")
        self.assertEqual(response, self.requester._cache[0])

    async def test_request_cache_clear_after_5(self, m):
        register_uris({"requests": ["get", "post"]}, m)

        for i in range(5):
            await self.requester.request("GET", "fake_get_request")

        response = await self.requester.request("POST", "fake_post_request")

        self.assertLessEqual(len(self.requester._cache), 5)
        self.assertEqual(response, self.requester._cache[0])

    async def test_request_lowercase_boolean(self, m):
        async def callback(url, data, **kwargs):
            print(f"DEB _fields={data._fields!r}")
            fields = {f[0]["name"]: f[2] for f in data._fields}
            self.assertEqual(2, len(fields))
            self.assertEqual({"test", "test2"}, set(fields.keys()))
            self.assertEqual("true", fields["test"])
            self.assertEqual("false", fields["test2"])
            return CallbackResult(status=200)

        m.add(
            settings.BASE_URL + "/api/v1/test",
            method="POST",
            callback=callback,
        )

        response = await self.requester.request("POST", "test", test=True, test2=False)
        self.assertEqual(response.status, 200)

    async def test_request_400(self, m):
        register_uris({"requests": ["400"]}, m)

        with self.assertRaises(BadRequest):
            await self.requester.request("GET", "400")

    async def test_request_401_InvalidAccessToken(self, m):
        register_uris({"requests": ["401_invalid_access_token"]}, m)

        with self.assertRaises(InvalidAccessToken):
            await self.requester.request("GET", "401_invalid_access_token")

    async def test_request_401_Unauthorized(self, m):
        register_uris({"requests": ["401_unauthorized"]}, m)

        with self.assertRaises(Unauthorized):
            await self.requester.request("GET", "401_unauthorized")

    async def test_request_404(self, m):
        register_uris({"requests": ["404"]}, m)

        with self.assertRaises(ResourceDoesNotExist):
            await self.requester.request("GET", "404")

    async def test_request_409(self, m):
        register_uris({"requests": ["409"]}, m)

        with self.assertRaises(Conflict):
            await self.requester.request("GET", "409")

    async def test_request_422(self, m):
        register_uris({"requests": ["422"]}, m)

        with self.assertRaises(UnprocessableEntity):
            await self.requester.request("GET", "422")

    async def test_request_500(self, m):
        register_uris({"requests": ["500"]}, m)

        with self.assertRaises(CanvasException):
            await self.requester.request("GET", "500")

    async def test_request_generic(self, m):
        register_uris({"requests": ["502", "503", "absurd"]}, m)

        with self.assertRaises(CanvasException):
            await self.requester.request("GET", "502")

        with self.assertRaises(CanvasException):
            await self.requester.request("GET", "503")

        with self.assertRaises(CanvasException):
            await self.requester.request("GET", "absurd")
