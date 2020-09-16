import unittest

from aioresponses import aioresponses

from canvasaio import Canvas
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestNotificationPreference(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            register_uris(
                {
                    "user": ["get_by_id", "list_comm_channels"],
                    "communication_channel": ["get_preference"],
                },
                m,
            )

            self.user = await self.canvas.get_user(1)
            self.comm_chan = await self.user.get_communication_channels()[0]
            self.notif_pref = await self.comm_chan.get_preference("new_announcement")

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.notif_pref)
        self.assertIsInstance(string, str)
