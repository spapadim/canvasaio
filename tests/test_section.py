import unittest

from aioresponses import aioresponses

from canvasaio import Canvas
from canvasaio.assignment import AssignmentOverride
from canvasaio.enrollment import Enrollment
from canvasaio.progress import Progress
from canvasaio.section import Section
from canvasaio.submission import GroupedSubmission, Submission
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestSection(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            register_uris({"section": ["get_by_id"]}, m)

            self.section = await self.canvas.get_section(1)

    async def asyncTearDown(self) -> None:
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.section)
        self.assertIsInstance(string, str)

    # get_assignment_override
    async def test_get_assignment_override(self, m):
        register_uris({"assignment": ["override_section_alias"]}, m)

        override = await self.section.get_assignment_override(1)

        self.assertIsInstance(override, AssignmentOverride)
        self.assertEqual(override.course_section_id, self.section.id)

    # get_enrollments()
    async def test_get_enrollments(self, m):
        register_uris({"section": ["list_enrollments", "list_enrollments_2"]}, m)

        enrollments = self.section.get_enrollments()
        enrollment_list = [enrollment async for enrollment in enrollments]

        self.assertEqual(len(enrollment_list), 4)
        self.assertIsInstance(enrollment_list[0], Enrollment)

    async def test_cross_list_section(self, m):
        register_uris({"course": ["get_by_id_2"], "section": ["crosslist_section"]}, m)

        section_by_id = await self.section.cross_list_section(2)
        self.assertIsInstance(section_by_id, Section)

        course_obj = await self.canvas.get_course(2)
        section_by_obj = await self.section.cross_list_section(course_obj)
        self.assertIsInstance(section_by_obj, Section)

    async def test_decross_list_section(self, m):
        register_uris({"section": ["decross_section"]}, m)

        section = await self.section.decross_list_section()

        self.assertIsInstance(section, Section)

    async def test_edit(self, m):
        register_uris({"section": ["edit"]}, m)

        edit = await self.section.edit()

        self.assertIsInstance(edit, Section)

    async def test_delete(self, m):
        register_uris({"section": ["delete"]}, m)

        deleted_section = await self.section.delete()

        self.assertIsInstance(deleted_section, Section)

    # get_multiple_submission()
    async def test_get_multiple_submissions(self, m):
        register_uris({"section": ["list_multiple_submissions"]}, m)

        submissions = self.section.get_multiple_submissions()
        submission_list = [submission async for submission in submissions]

        self.assertEqual(len(submission_list), 2)
        self.assertIsInstance(submission_list[0], Submission)

    async def test_get_multiple_submissions_grouped_true(self, m):
        register_uris({"section": ["list_multiple_submissions_grouped"]}, m)

        submissions = self.section.get_multiple_submissions(grouped=True)
        submission_list = [submission async for submission in submissions]

        self.assertEqual(len(submission_list), 2)
        self.assertIsInstance(submission_list[0], GroupedSubmission)

    async def test_get_multiple_submissions_grouped_false(self, m):
        register_uris({"section": ["list_multiple_submissions"]}, m)

        submissions = self.section.get_multiple_submissions(grouped=False)
        submission_list = [submission async for submission in submissions]

        self.assertEqual(len(submission_list), 2)
        self.assertIsInstance(submission_list[0], Submission)

    async def test_get_multiple_submissions_grouped_invalid(self, m):
        with self.assertRaises(ValueError) as cm:
            self.section.get_multiple_submissions(grouped="blargh")

        self.assertIn("Parameter `grouped` must", cm.exception.args[0])

    async def test_submissions_bulk_update(self, m):
        register_uris({"section": ["update_submissions"]}, m)
        register_uris({"progress": ["course_progress"]}, m)
        progress = await self.section.submissions_bulk_update(
            grade_data={"1": {"1": {"posted_grade": 97}, "2": {"posted_grade": 98}}}
        )
        self.assertIsInstance(progress, Progress)
        self.assertTrue(progress.context_type == "Course")
        progress = await progress.query()
        self.assertTrue(progress.context_type == "Course")
