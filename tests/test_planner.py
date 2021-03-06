import unittest

from aioresponses import aioresponses

from canvasaio.exceptions import RequiredFieldMissing
from canvasaio import Canvas
from canvasaio.planner import PlannerNote, PlannerOverride
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestPlannerNote(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            register_uris({"planner": ["single_planner_note"]}, m)
            self.note = await self.canvas.get_planner_note(1)

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.note)
        self.assertIsInstance(string, str)

    # get_planner_notes()
    async def test_get_planner_notes(self, m):
        register_uris({"planner": ["multiple_planner_notes"]}, m)

        response = self.canvas.get_planner_notes()
        notes = [note async for note in response]

        self.assertEqual(len(list(notes)), 2)
        self.assertEqual(notes[0].title, "Breathe")
        self.assertIsInstance(notes[0], PlannerNote)
        self.assertTrue(hasattr(notes[1], "todo_date"))

    # get_planner_note()
    async def test_get_planner_note(self, m):
        register_uris({"planner": ["single_planner_note"]}, m)

        note_by_id = await self.canvas.get_planner_note(1)
        self.assertIsInstance(note_by_id, PlannerNote)
        self.assertEqual(note_by_id.id, 1)
        self.assertEqual(note_by_id.title, "Take a nap")
        self.assertEqual(note_by_id.todo_date, "2018-05-09T10:12:00Z")

        note_by_obj = await self.canvas.get_planner_note(note_by_id)
        self.assertIsInstance(note_by_obj, PlannerNote)
        self.assertEqual(note_by_obj.id, 1)
        self.assertEqual(note_by_obj.title, "Take a nap")
        self.assertEqual(note_by_obj.todo_date, "2018-05-09T10:12:00Z")

    # get_planner_note()
    async def test_get_planner_note_fail(self, m):
        with self.assertRaises(RequiredFieldMissing):
            await self.canvas.get_planner_note(planner_note=None)

    # create_planner_note()
    async def test_create_planner_note(self, m):
        register_uris({"planner": ["create_planner_note"]}, m)

        note_create_1 = await self.canvas.create_planner_note(title="Perform photosynthesis")
        self.assertIsInstance(note_create_1, PlannerNote)
        self.assertTrue(hasattr(note_create_1, "title"))

        note_create_2 = await self.canvas.create_planner_note(
            title="Perform photosynthesis", todo_date="2019-09-05T12:10:30Z"
        )
        self.assertIsInstance(note_create_2, PlannerNote)
        self.assertTrue(hasattr(note_create_2, "title"))
        self.assertEqual(note_create_2.todo_date, "2019-09-05T12:10:30Z")

    # update()
    async def test_update(self, m):
        register_uris({"planner": ["update_planner_note"]}, m)

        note_update_1 = await self.note.update(title="Go to restroom")
        self.assertIsInstance(note_update_1, PlannerNote)
        self.assertEqual(note_update_1.title, "Go to restroom")

        note_update_2 = await self.note.update(
            title="Go to restroom", todo_date="2020-01-07T15:16:18Z"
        )
        self.assertIsInstance(note_update_2, PlannerNote)
        self.assertEqual(note_update_2.title, "Go to restroom")
        self.assertEqual(note_update_2.todo_date, "2020-01-07T15:16:18Z")

    # delete_poll()
    async def test_delete(self, m):
        register_uris({"planner": ["delete_planner_note"]}, m)

        note_delete = await self.note.delete()
        self.assertIsInstance(note_delete, PlannerNote)
        self.assertEqual(note_delete.id, 1)
        self.assertEqual(note_delete.title, "Go to restroom")
        self.assertEqual(note_delete.todo_date, "2020-01-07T15:16:18Z")


@aioresponse_mock
class TestPlannerOverride(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            register_uris({"planner": ["single_planner_override"]}, m)
            self.override = await self.canvas.get_planner_override(1)

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.override)
        self.assertIsInstance(string, str)

    # get_planner_overrides()
    async def test_get_planner_overrides(self, m):
        register_uris({"planner": ["multiple_planner_overrides"]}, m)

        response = self.canvas.get_planner_overrides()
        overrides = [override async for override in response]

        self.assertEqual(len(list(overrides)), 2)
        self.assertEqual(overrides[0].plannable_id, 22)
        self.assertIsInstance(overrides[0], PlannerOverride)
        self.assertTrue(hasattr(overrides[1], "marked_complete"))

    # get_planner_override()
    async def test_get_planner_override(self, m):
        register_uris({"planner": ["single_planner_override"]}, m)

        override_by_id = await self.canvas.get_planner_override(1)
        self.assertIsInstance(override_by_id, PlannerOverride)
        self.assertEqual(override_by_id.id, 1)
        self.assertEqual(override_by_id.plannable_id, 11)
        self.assertFalse(override_by_id.marked_complete)

        override_by_obj = await self.canvas.get_planner_override(override_by_id)
        self.assertIsInstance(override_by_obj, PlannerOverride)
        self.assertEqual(override_by_obj.id, 1)
        self.assertEqual(override_by_obj.plannable_id, 11)
        self.assertFalse(override_by_obj.marked_complete)

    async def test_get_planner_override_fail(self, m):
        with self.assertRaises(RequiredFieldMissing):
            await self.canvas.get_planner_override(planner_override=None)

    # create_planner_override()
    async def test_create_planner_override(self, m):
        register_uris({"planner": ["create_planner_override"]}, m)

        override_create = await self.canvas.create_planner_override(
            plannable_type="assignment", plannable_id=69
        )
        self.assertIsInstance(override_create, PlannerOverride)
        self.assertTrue(hasattr(override_create, "plannable_id"))

    # create_planner_override()
    async def test_create_planner_override_fail_1(self, m):
        with self.assertRaises(RequiredFieldMissing):
            await self.canvas.create_planner_override(plannable_type=None, plannable_id=11)

    # create_planner_override()
    async def test_create_planner_override_fail_2(self, m):
        with self.assertRaises(RequiredFieldMissing):
            await self.canvas.create_planner_override(
                plannable_type="assignment", plannable_id=None
            )

    # update()
    async def test_update(self, m):
        register_uris({"planner": ["update_planner_override"]}, m)

        override_update = await self.override.update(marked_complete=True)
        self.assertIsInstance(override_update, PlannerOverride)
        self.assertTrue(override_update.marked_complete)

    # delete_poll()
    async def test_delete(self, m):
        register_uris({"planner": ["delete_planner_override"]}, m)

        override_delete = await self.override.delete()
        self.assertIsInstance(override_delete, PlannerOverride)
        self.assertEqual(override_delete.id, 1)
        self.assertEqual(override_delete.plannable_id, 11)
        self.assertTrue(override_delete.marked_complete)
