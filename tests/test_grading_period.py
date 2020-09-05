import unittest

from aioresponses import aioresponses

from canvasaio import Canvas
from canvasaio.exceptions import RequiredFieldMissing
from canvasaio.grading_period import GradingPeriod
from tests.util import register_uris, aioresponse_mock
from tests import settings


@aioresponse_mock
class TestGradingPeriod(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        self.grading_period = GradingPeriod(
            self.canvas._Canvas__requester,
            {"title": "grading period 1", "id": 1, "course_id": 1},
        )

    async def asyncTearDown(self):
        await self.canvas.close()

    def test_str(self, m):
        test_str = str(self.grading_period)
        self.assertIsInstance(test_str, str)

    # update()
    async def test_update(self, m):
        register_uris({"grading_period": ["update"]}, m)

        edited_grading_period = await self.grading_period.update(
            grading_period=[
                {
                    "start_date": "2019-06-10T06:00:00Z",
                    "end_date": "2019-06-15T06:00:00Z",
                }
            ]
        )

        self.assertIsInstance(edited_grading_period, GradingPeriod)
        self.assertTrue(hasattr(edited_grading_period, "title"))
        self.assertTrue(hasattr(edited_grading_period, "course_id"))
        self.assertEqual(edited_grading_period.title, "Grading period 1")
        self.assertEqual(edited_grading_period.course_id, 1)
        self.assertTrue(hasattr(edited_grading_period, "start_date"))
        self.assertTrue(hasattr(edited_grading_period, "end_date"))
        self.assertEqual(edited_grading_period.start_date, "2019-05-23T06:00:00Z")
        self.assertEqual(edited_grading_period.end_date, "2019-08-23T06:00:00Z")

    # Check that the appropriate exception is raised when no list is given.
    async def test_update_without_list(self, m):
        register_uris({"grading_period": ["update"]}, m)

        with self.assertRaises(RequiredFieldMissing):
            await self.grading_period.update(
                grading_period={
                    "start_date": "2019-06-10T06:00:00Z",
                    "end_date": "2019-06-15T06:00:00Z",
                }
            )

    # Check that the grading_period that is passed has a start date
    async def test_update_without_start_date(self, m):
        register_uris({"grading_period": ["update"]}, m)

        with self.assertRaises(RequiredFieldMissing):
            await self.grading_period.update(
                grading_period=[{"end_date": "2019-06-15T06:00:00Z"}]
            )

    # Check that the appropriate exception is raised when no list is given.
    async def test_update_without_end_date(self, m):
        register_uris({"grading_period": ["update"]}, m)

        with self.assertRaises(RequiredFieldMissing):
            await self.grading_period.update(
                grading_period=[{"start_date": "2019-06-10T06:00:00Z"}]
            )

    # delete()
    async def test_delete(self, m):
        register_uris({"grading_period": ["delete"]}, m)
        self.assertEqual(await self.grading_period.delete(), 204)
