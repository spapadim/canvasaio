import unittest

from aioresponses import aioresponses

from canvasaio import Canvas
from canvasaio.tab import Tab
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestTab(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            register_uris(
                {
                    "course": ["get_by_id", "list_tabs"],
                    "group": ["get_by_id", "list_tabs"],
                },
                m,
            )

            self.course = await self.canvas.get_course(1)

            tabs = self.course.get_tabs()
            self.tab = await tabs[1]

            self.group = await self.canvas.get_group(1)
            group_tabs = self.group.get_tabs()
            self.tab_group = await group_tabs[1]

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.tab)
        self.assertIsInstance(string, str)

    # update()
    async def test_update_course(self, m):
        register_uris({"course": ["update_tab"]}, m)

        new_position = 3
        await self.tab.update(position=new_position)

        self.assertIsInstance(self.tab, Tab)
        self.assertEqual(self.tab.position, 3)

    async def test_update_group(self, m):
        with self.assertRaises(ValueError):
            await self.tab_group.update(position=1)
