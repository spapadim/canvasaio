import unittest

from aioresponses import aioresponses

from canvasaio import Canvas
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestDay(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):

        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            requires = {"course": ["get_by_id", "get_gradebook_history_dates"]}
            register_uris(requires, m)

            self.course = await self.canvas.get_course(1)
            self.gradebook_history_dates = await self.course.get_gradebook_history_dates()[0]

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.gradebook_history_dates)
        self.assertIsInstance(string, str)


@aioresponse_mock
class TestGrader(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):

        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            requires = {"course": ["get_by_id", "get_gradebook_history_details"]}
            register_uris(requires, m)

            self.course = await self.canvas.get_course(1)
            self.gradebook_history_details = await self.course.get_gradebook_history_details(
                "03-26-2019"
            )[0]

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.gradebook_history_details)
        self.assertIsInstance(string, str)


@aioresponse_mock
class TestSubmissionHistory(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):

        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            requires = {"course": ["get_by_id", "get_submission_history"]}
            register_uris(requires, m)

            self.course = await self.canvas.get_course(1)
            self.submission_history = await self.course.get_submission_history(
                "08-23-2019", 1, 1
            )[0]

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.submission_history)
        self.assertIsInstance(string, str)


@aioresponse_mock
class TestSubmissionVersion(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):

        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            requires = {"course": ["get_by_id", "get_uncollated_submissions"]}
            register_uris(requires, m)

            self.course = await self.canvas.get_course(1)
            self.uncollated_submissions = await self.course.get_uncollated_submissions()[0]

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.uncollated_submissions)
        self.assertIsInstance(string, str)
