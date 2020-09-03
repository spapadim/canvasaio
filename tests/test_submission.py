import unittest
import uuid

from aioresponses import aioresponses

from canvasaio import Canvas
from canvasaio.peer_review import PeerReview
from canvasaio.submission import GroupedSubmission, Submission
from tests import settings
from tests.util import cleanup_file, register_uris, aioresponse_mock


@aioresponse_mock
class TestSubmission(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):

        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            register_uris(
                {
                    "course": ["get_by_id", "get_assignment_by_id"],
                    "section": ["get_by_id"],
                    "submission": ["get_by_id_course"],
                },
                m,
            )

            self.course = await self.canvas.get_course(1)
            self.assignment = await self.course.get_assignment(1)
            self.submission = await self.assignment.get_submission(1)

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.submission)
        self.assertIsInstance(string, str)

    # create_submission_peer_review()
    async def test_create_submission_peer_review(self, m):
        register_uris({"submission": ["create_submission_peer_review"]}, m)

        created_peer_review = await self.submission.create_submission_peer_review(1)

        self.assertIsInstance(created_peer_review, PeerReview)
        self.assertEqual(created_peer_review.user_id, 7)

    # delete_submission_peer_review()
    async def test_delete_submission_peer_review(self, m):
        register_uris({"submission": ["delete_submission_peer_review"]}, m)

        deleted_peer_review = await self.submission.delete_submission_peer_review(1)

        self.assertIsInstance(deleted_peer_review, PeerReview)
        self.assertEqual(deleted_peer_review.user_id, 7)

    # edit()
    async def test_edit(self, m):
        register_uris({"submission": ["edit"]}, m)

        self.assertFalse(hasattr(self.submission, "excused"))

        await self.submission.edit(submission={"excuse": True})

        self.assertIsInstance(self.submission, Submission)
        self.assertTrue(hasattr(self.submission, "excused"))
        self.assertTrue(self.submission.excused)

    # get_submission_peer_reviews()
    async def test_get_submission_peer_reviews(self, m):
        register_uris({"submission": ["list_submission_peer_reviews"]}, m)

        submission_peer_reviews = self.submission.get_submission_peer_reviews()
        submission_peer_review_list = [
            peer_review async for peer_review in submission_peer_reviews
        ]

        self.assertEqual(len(submission_peer_review_list), 2)
        self.assertIsInstance(submission_peer_review_list[0], PeerReview)

    # mark_read()
    async def test_mark_read(self, m):
        register_uris({"course": ["mark_submission_as_read"]}, m)

        marked_read = await self.submission.mark_read()
        self.assertTrue(marked_read)

    # mark_unread()
    async def test_mark_unread(self, m):
        register_uris({"course": ["mark_submission_as_unread"]}, m)

        marked_unread = await self.submission.mark_unread()
        self.assertTrue(marked_unread)

    # upload_comment()
    async def test_upload_comment(self, m):
        register_uris(
            {"submission": ["upload_comment", "upload_comment_final", "edit"]}, m
        )

        filename = "testfile_submission_{}".format(uuid.uuid4().hex)

        try:
            with open(filename, "w+") as file:
                response = await self.submission.upload_comment(file)

            self.assertTrue(response[0])
            self.assertIsInstance(response[1], dict)
            self.assertIn("url", response[1])
        finally:
            cleanup_file(filename)


class TestGroupedSubmission(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        self.grouped_submission = GroupedSubmission(
            self.canvas._Canvas__requester,
            {
                "user_id": 1,
                "submissions": [
                    {
                        "id": 1,
                        "assignment_id": 1,
                        "user_id": 1,
                        "html_url": "https://example.com/courses/1/assignments/1/submissions/1",
                        "submission_type": "online_upload",
                    }
                ],
            },
        )

    async def asyncTearDown(self):
        await self.canvas.close()

    # __init__()
    def test__init__no_submission_key(self):
        grouped_submission = GroupedSubmission(
            self.canvas._Canvas__requester, {"user_id": 1}
        )

        self.assertIsInstance(grouped_submission, GroupedSubmission)
        self.assertTrue(hasattr(grouped_submission, "submissions"))
        self.assertIsInstance(grouped_submission.submissions, list)
        self.assertEqual(len(grouped_submission.submissions), 0)

    # __str__()
    def test__str__(self):
        string = str(self.grouped_submission)
        self.assertIsInstance(string, str)
        self.assertEqual(string, "1 submission(s) for User #1")
