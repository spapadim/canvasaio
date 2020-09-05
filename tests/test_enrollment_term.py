import unittest

from aioresponses import aioresponses

from canvasaio import Canvas
from canvasaio.enrollment_term import EnrollmentTerm
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestEnrollmentTerm(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            register_uris({"account": ["get_by_id", "create_enrollment_term"]}, m)

            self.account = await self.canvas.get_account(1)
            self.enrollment_term = await self.account.create_enrollment_term(
                enrollment_term={"name": "Test Enrollment Term"}
            )

    async def asyncTearDown(self):
        await self.canvas.close()

    # delete()
    async def test_delete_enrollment_term(self, m):
        register_uris({"enrollment_term": ["delete_enrollment_term"]}, m)

        deleted_enrollment_term = await self.enrollment_term.delete()

        self.assertIsInstance(deleted_enrollment_term, EnrollmentTerm)
        self.assertTrue(hasattr(deleted_enrollment_term, "name"))
        self.assertEqual(deleted_enrollment_term.name, "Test Enrollment Term")

    # edit()
    async def test_edit_enrollment_term(self, m):
        register_uris({"enrollment_term": ["edit_enrollment_term"]}, m)

        name = "New Name"
        edited_enrollment_term = await self.enrollment_term.edit(
            enrollment_term={"name": name}
        )

        self.assertIsInstance(edited_enrollment_term, EnrollmentTerm)
        self.assertTrue(hasattr(edited_enrollment_term, "name"))
        self.assertEqual(edited_enrollment_term.name, name)

    # __str__()
    def test__str__(self, m):
        string = str(self.enrollment_term)
        self.assertIsInstance(string, str)
