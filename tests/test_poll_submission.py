import unittest

from aioresponses import aioresponses

from canvasaio.exceptions import RequiredFieldMissing
from canvasaio import Canvas
from canvasaio.poll_submission import PollSubmission
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestPollSubmission(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            requires = {
                "poll": ["get_poll"],
                "poll_session": ["get_session"],
                "poll_submission": ["get_submission"],
            }
            register_uris(requires, m)

            self.poll = await self.canvas.get_poll(1)
            self.poll.poll_session = await self.poll.get_session(1)
            self.poll.poll_session.poll_submission = (
                await self.poll.poll_session.get_submission(1)
            )

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.poll.poll_session.poll_submission)
        self.assertIsInstance(string, str)

    # get_submission()
    async def test_get_submission(self, m):
        register_uris({"poll_submission": ["get_submission"]}, m)

        choice_by_id = await self.poll.poll_session.get_submission(1)
        self.assertIsInstance(choice_by_id, PollSubmission)
        self.assertTrue(hasattr(choice_by_id, "id"))
        self.assertTrue(hasattr(choice_by_id, "poll_choice_id"))
        self.assertTrue(hasattr(choice_by_id, "user_id"))
        self.assertTrue(hasattr(choice_by_id, "created_at"))

        choice_by_obj = await self.poll.poll_session.get_submission(choice_by_id)
        self.assertIsInstance(choice_by_obj, PollSubmission)
        self.assertTrue(hasattr(choice_by_obj, "id"))
        self.assertTrue(hasattr(choice_by_obj, "poll_choice_id"))
        self.assertTrue(hasattr(choice_by_obj, "user_id"))
        self.assertTrue(hasattr(choice_by_obj, "created_at"))

    # create_submission()
    async def test_create_submission(self, m):
        register_uris({"poll_submission": ["create_submission"]}, m)

        new_submission = await self.poll.poll_session.create_submission(
            [{"poll_choice_id": 1}]
        )
        self.assertIsInstance(new_submission, PollSubmission)
        self.assertEqual(new_submission.poll_choice_id, 1)

    # create_submission()
    async def test_create_submission_fail(self, m):
        with self.assertRaises(RequiredFieldMissing):
            await self.poll.poll_session.create_submission(poll_submissions={})
