import unittest

from aioresponses import aioresponses

from canvasaio import Canvas
from canvasaio.outcome_import import OutcomeImport
from tests import settings
from tests.util import aioresponse_mock


@aioresponse_mock
class TestOutcomeImport(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        self.outcome_import = OutcomeImport(
            self.canvas._Canvas__requester, {"id": 1, "workflow_state": 1}
        )

    async def asyncTearDown(self):
        await self.canvas.close()

    def test_str(self, m):

        test_str = str(self.outcome_import)
        self.assertIsInstance(test_str, str)
