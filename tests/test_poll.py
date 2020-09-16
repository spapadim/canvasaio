import unittest

from aioresponses import aioresponses

from canvasaio.exceptions import RequiredFieldMissing
from canvasaio import Canvas
from canvasaio.poll import Poll
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestPoll(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            register_uris({"poll": ["get_poll"]}, m)
            self.poll = await self.canvas.get_poll(1)

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.poll)
        self.assertIsInstance(string, str)

    # get_polls()
    async def test_get_polls(self, m):
        register_uris({"poll": ["get_polls"]}, m)

        polls_list = self.canvas.get_polls()

        self.assertIsInstance(await polls_list[0], Poll)
        self.assertIsInstance(await polls_list[1], Poll)

    # get_poll()
    async def test_get_poll(self, m):
        register_uris({"poll": ["get_poll"]}, m)

        poll_by_id = await self.canvas.get_poll(1)
        self.assertIsInstance(poll_by_id, Poll)
        self.assertEqual(poll_by_id.question, "Is this a question?")
        self.assertEqual(poll_by_id.description, "This is a test.")
        self.assertEqual(poll_by_id.created_at, "2014-01-07T13:10:19Z")

        poll_by_obj = await self.canvas.get_poll(poll_by_id)
        self.assertIsInstance(poll_by_obj, Poll)
        self.assertEqual(poll_by_obj.question, "Is this a question?")
        self.assertEqual(poll_by_obj.description, "This is a test.")
        self.assertEqual(poll_by_obj.created_at, "2014-01-07T13:10:19Z")

    # create_poll()
    async def test_create_poll(self, m):
        register_uris({"poll": ["create_poll"]}, m)

        new_poll_q = await self.canvas.create_poll([{"question": "Is this a question?"}])
        self.assertIsInstance(new_poll_q, Poll)
        self.assertTrue(hasattr(new_poll_q, "question"))

        new_poll_q_d = await self.canvas.create_poll(
            [{"question": "Is this a question?"}, {"description": "This is a test."}]
        )
        self.assertIsInstance(new_poll_q_d, Poll)
        self.assertTrue(hasattr(new_poll_q_d, "question"))
        self.assertTrue(hasattr(new_poll_q_d, "description"))

    # create_poll()
    async def test_create_poll_fail(self, m):
        with self.assertRaises(RequiredFieldMissing):
            await self.canvas.create_poll(poll={})

    # update()
    async def test_update(self, m):
        register_uris({"poll": ["update"]}, m)

        updated_poll_q = await self.poll.update([{"question": "Is this not a question?"}])
        self.assertIsInstance(updated_poll_q, Poll)
        self.assertEqual(updated_poll_q.question, "Is this not a question?")

        updated_poll_q_and_d = await self.poll.update(
            [
                {"question": "Is this not a question?"},
                {"description": "This is not a test."},
            ]
        )
        self.assertIsInstance(updated_poll_q_and_d, Poll)
        self.assertEqual(updated_poll_q_and_d.question, "Is this not a question?")
        self.assertEqual(updated_poll_q_and_d.description, "This is not a test.")

    # update
    async def test_update_fail(self, m):
        with self.assertRaises(RequiredFieldMissing):
            await self.poll.update(poll={})

    # delete_poll()
    async def test_delete(self, m):
        register_uris({"poll": ["delete"]}, m)

        result = await self.poll.delete()
        self.assertTrue(result)
