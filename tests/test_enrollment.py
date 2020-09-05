import unittest

from aioresponses import aioresponses

from canvasaio.canvas import Canvas
from canvasaio.enrollment import Enrollment
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestEnrollment(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            requires = {"account": ["get_by_id"], "enrollment": ["get_by_id"]}
            register_uris(requires, m)

            self.account = await self.canvas.get_account(1)
            self.enrollment = await self.account.get_enrollment(1)

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.enrollment)
        self.assertIsInstance(string, str)

    # deactivate()
    async def test_deactivate(self, m):
        register_uris({"enrollment": ["deactivate"]}, m)

        target_enrollment = await self.enrollment.deactivate("conclude")

        self.assertIsInstance(target_enrollment, Enrollment)

    async def test_deactivate_invalid_task(self, m):
        with self.assertRaises(ValueError):
            await self.enrollment.deactivate("finish")

    # reactivate()
    async def test_reactivate(self, m):
        register_uris({"enrollment": ["reactivate"]}, m)

        target_enrollment = await self.enrollment.reactivate()

        self.assertIsInstance(target_enrollment, Enrollment)
