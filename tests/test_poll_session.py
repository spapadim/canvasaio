import unittest

from aioresponses import aioresponses

from canvasaio.exceptions import RequiredFieldMissing
from canvasaio import Canvas
from canvasaio.poll_session import PollSession
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestPollSession(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            requires = {
                "user": ["get_by_id"],
                "poll": ["get_poll"],
                "poll_session": ["get_session"],
            }
            register_uris(requires, m)

            self.user = await self.canvas.get_user(1)
            self.poll = await self.canvas.get_poll(1)
            self.poll.poll_session = await self.poll.get_session(1)

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.poll.poll_session)
        self.assertIsInstance(string, str)

    # get_sessions()
    async def test_get_sessions(self, m):
        register_uris({"poll_session": ["get_sessions"]}, m)

        session_list = self.poll.get_sessions()

        self.assertIsInstance(await session_list[0], PollSession)
        self.assertIsInstance(await session_list[1], PollSession)

    # get_session()
    async def test_get_session(self, m):
        register_uris({"poll_session": ["get_session"]}, m)

        choice_by_id = await self.poll.get_session(1)
        self.assertIsInstance(choice_by_id, PollSession)
        self.assertTrue(choice_by_id.is_published)
        self.assertFalse(choice_by_id.has_public_results)
        self.assertEqual(choice_by_id.created_at, "2014-01-07T15:16:18Z")
        self.assertEqual(len(choice_by_id.results), 3)
        self.assertEqual(choice_by_id.poll_submissions, None)

        choice_by_obj = await self.poll.get_session(choice_by_id)
        self.assertIsInstance(choice_by_obj, PollSession)
        self.assertTrue(choice_by_obj.is_published)
        self.assertFalse(choice_by_obj.has_public_results)
        self.assertEqual(choice_by_obj.created_at, "2014-01-07T15:16:18Z")
        self.assertEqual(len(choice_by_obj.results), 3)
        self.assertEqual(choice_by_obj.poll_submissions, None)

    # create_session()
    async def test_create_session(self, m):
        register_uris({"poll_session": ["create_session"]}, m)

        new_session_cid = await self.poll.create_session([{"course_id": 1}])
        self.assertIsInstance(new_session_cid, PollSession)
        self.assertEqual(new_session_cid.course_id, 1)

        new_session_cid_sid = await self.poll.create_session(
            [{"course_id": 1}, {"course_section_id": 1}]
        )
        self.assertIsInstance(new_session_cid_sid, PollSession)
        self.assertEqual(new_session_cid_sid.course_id, 1)
        self.assertEqual(new_session_cid_sid.course_section_id, 1)

        new_session_cid_hpr = await self.poll.create_session(
            [{"course_id": 1}, {"has_public_results": False}]
        )
        self.assertIsInstance(new_session_cid_hpr, PollSession)
        self.assertEqual(new_session_cid_hpr.course_id, 1)
        self.assertFalse(new_session_cid_hpr.has_public_results)

        new_session_cid_sid_hpr = await self.poll.create_session(
            [{"course_id": 1}, {"course_section_id": 1}, {"has_public_results": False}]
        )
        self.assertIsInstance(new_session_cid_sid_hpr, PollSession)
        self.assertEqual(new_session_cid_sid_hpr.course_id, 1)
        self.assertEqual(new_session_cid_sid_hpr.course_section_id, 1)
        self.assertFalse(new_session_cid_sid_hpr.has_public_results)

    # create_session()
    async def test_create_session_fail(self, m):
        with self.assertRaises(RequiredFieldMissing):
            await self.poll.create_session(poll_session={})

    # update()
    async def test_update(self, m):
        register_uris({"poll_session": ["update"]}, m)

        updated_session_cid = await self.poll.poll_session.update([{"course_id": 2}])
        self.assertIsInstance(updated_session_cid, PollSession)
        self.assertEqual(updated_session_cid.course_id, 2)

        updated_session_cid_sid = await self.poll.poll_session.update(
            [{"course_id": 2}, {"course_section_id": 2}]
        )
        self.assertIsInstance(updated_session_cid_sid, PollSession)
        self.assertEqual(updated_session_cid_sid.course_id, 2)
        self.assertEqual(updated_session_cid_sid.course_section_id, 2)

        updated_session_cid_hpr = await self.poll.poll_session.update(
            [{"course_id": 2}, {"has_public_results": True}]
        )
        self.assertIsInstance(updated_session_cid_hpr, PollSession)
        self.assertEqual(updated_session_cid_hpr.course_id, 2)
        self.assertTrue(updated_session_cid_hpr.has_public_results)

        updated_session_cid_sid_hpr = await self.poll.poll_session.update(
            [{"course_id": 2}, {"course_section_id": 2}, {"has_public_results": True}]
        )
        self.assertIsInstance(updated_session_cid_sid_hpr, PollSession)
        self.assertEqual(updated_session_cid_sid_hpr.course_id, 2)
        self.assertEqual(updated_session_cid_sid_hpr.course_section_id, 2)
        self.assertTrue(updated_session_cid_sid_hpr.has_public_results)

    # update()
    async def test_update_fail(self, m):
        with self.assertRaises(RequiredFieldMissing):
            await self.poll.poll_session.update(poll_session={})

    # delete()
    async def test_delete(self, m):
        register_uris({"poll_session": ["delete"]}, m)

        result = await self.poll.poll_session.delete()
        self.assertTrue(result)

    # open()
    async def test_open(self, m):
        register_uris({"poll_session": ["open"]}, m)

        opened_session = await self.poll.poll_session.open()

        self.assertIsInstance(opened_session, PollSession)
        self.assertTrue(opened_session.is_published)

    # close()
    async def test_close(self, m):
        register_uris({"poll_session": ["close"]}, m)

        closed_session = await self.poll.poll_session.close()

        self.assertIsInstance(closed_session, PollSession)
        self.assertFalse(closed_session.is_published)

    # get_open_poll_sessions()
    async def test_get_open_poll_sessions(self, m):
        register_uris({"poll_session": ["get_open_poll_sessions"]}, m)

        response = self.user.get_open_poll_sessions()
        open_sessions = [session async for session in response]

        self.assertIsInstance(open_sessions[0], PollSession)
        self.assertTrue(open_sessions[0].is_published)

        self.assertIsInstance(open_sessions[0], PollSession)
        self.assertTrue(open_sessions[0].is_published)

    # get_closed_poll_sessions()
    async def test_get_closed_poll_sessions(self, m):
        register_uris({"poll_session": ["get_closed_poll_sessions"]}, m)

        response = self.user.get_closed_poll_sessions()
        closed_sessions = [session async for session in response]

        self.assertIsInstance(closed_sessions[0], PollSession)
        self.assertFalse(closed_sessions[0].is_published)

        self.assertIsInstance(closed_sessions[0], PollSession)
        self.assertFalse(closed_sessions[0].is_published)
