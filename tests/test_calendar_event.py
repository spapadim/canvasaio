import unittest

from aioresponses import aioresponses

from canvasaio import Canvas
from canvasaio.calendar_event import CalendarEvent
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestCalendarEvent(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            register_uris({"calendar_event": ["get_calendar_event"]}, m)

            self.calendar_event = await self.canvas.get_calendar_event(567)

    async def asyncTearDown(self):
        await self.canvas.close()

    # delete()
    async def test_delete_calendar_event(self, m):
        register_uris({"calendar_event": ["delete_calendar_event"]}, m)

        deleted_calendar_event = await self.calendar_event.delete()

        self.assertIsInstance(deleted_calendar_event, CalendarEvent)
        self.assertTrue(hasattr(deleted_calendar_event, "title"))
        self.assertEqual(deleted_calendar_event.title, "Test Event 3")

    # edit()
    async def test_edit_calendar_event(self, m):
        register_uris({"calendar_event": ["edit_calendar_event"]}, m)

        title = "New Name"
        edited_calendar_event = await self.calendar_event.edit(
            calendar_event={"title": title}
        )

        self.assertIsInstance(edited_calendar_event, CalendarEvent)
        self.assertTrue(hasattr(edited_calendar_event, "title"))
        self.assertEqual(edited_calendar_event.title, title)

    # __str__()
    def test__str__(self, m):
        string = str(self.calendar_event)
        self.assertIsInstance(string, str)
