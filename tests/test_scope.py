import unittest

from aioresponses import aioresponses

from canvasaio import Canvas
from canvasaio.scope import Scope
from tests import settings
from tests.util import aioresponse_mock


@aioresponse_mock
class TestGradingPeriod(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        self.scope = Scope(
            self.canvas._Canvas__requester, {"resource": "users", "verb": "PUT"}
        )

    async def asyncTearDown(self):
        await self.canvas.close()

    def test_str(self, m):

        test_str = str(self.scope)
        self.assertIsInstance(test_str, str)
