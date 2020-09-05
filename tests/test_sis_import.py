import unittest

from aioresponses import aioresponses

from canvasaio import Canvas
from canvasaio.progress import Progress
from canvasaio.sis_import import SisImport
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestSisImportGroup(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            requires = {
                "account": ["get_by_id", "get_role"],
                "sis_import": ["get_by_id"],
            }
            register_uris(requires, m)

            self.account = await self.canvas.get_account(1)
            self.sis_import = await self.account.get_sis_import(2)

    async def asyncTearDown(self):
        await self.canvas.close()

    # abort()
    async def test_abort_sis_import(self, m):
        register_uris({"sis_import": ["abort_sis_import"]}, m)

        aborted_sis_import = await self.sis_import.abort()

        self.assertIsInstance(aborted_sis_import, SisImport)

        self.assertTrue(
            aborted_sis_import.workflow_state == "aborted"
            if aborted_sis_import.progress < 100
            else True
        )

    # restore_states()
    async def test_restore_states(self, m):
        register_uris({"sis_import": ["restore_sis_import_states"]}, m)

        restore_state_progress = await self.sis_import.restore_states()

        self.assertIsInstance(restore_state_progress, Progress)
        self.assertEqual(restore_state_progress.context_id, self.sis_import.id)
        self.assertEqual(restore_state_progress.context_type, "SisBatch")
        self.assertEqual(restore_state_progress.tag, "sis_batch_state_restore")
