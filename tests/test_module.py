import unittest

from aioresponses import aioresponses

from canvasaio import Canvas
from canvasaio.exceptions import RequiredFieldMissing
from canvasaio.module import Module, ModuleItem
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestModule(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            register_uris({"course": ["get_by_id", "get_module_by_id"]}, m)

            self.course = await self.canvas.get_course(1)
            self.module = await self.course.get_module(1)

    async def asyncTearDown(self):
        await self.canvas.close()

    # edit()
    async def test_edit_module(self, m):
        register_uris({"module": ["edit"]}, m)

        name = "New Name"
        edited_module = await self.module.edit(module={"name": name})

        self.assertIsInstance(edited_module, Module)
        self.assertTrue(hasattr(edited_module, "name"))
        self.assertEqual(edited_module.name, name)
        self.assertTrue(hasattr(edited_module, "course_id"))
        self.assertEqual(edited_module.course_id, self.course.id)

    # delete()
    async def test_delete_module(self, m):
        register_uris({"module": ["delete"]}, m)

        deleted_module = await self.module.delete()

        self.assertIsInstance(deleted_module, Module)
        self.assertTrue(hasattr(deleted_module, "course_id"))
        self.assertEqual(deleted_module.course_id, self.course.id)

    # relock()
    async def test_relock(self, m):
        register_uris({"module": ["relock"]}, m)

        relocked_module = await self.module.relock()

        self.assertIsInstance(relocked_module, Module)
        self.assertTrue(hasattr(relocked_module, "course_id"))
        self.assertEqual(relocked_module.course_id, self.course.id)

    # get_module_items()
    async def test_get_module_items(self, m):
        register_uris({"module": ["list_module_items", "list_module_items2"]}, m)

        module_items = self.module.get_module_items()
        module_item_list = [module_item async for module_item in module_items]

        self.assertEqual(len(module_item_list), 4)
        self.assertIsInstance(module_item_list[0], ModuleItem)
        self.assertTrue(hasattr(module_item_list[0], "course_id"))
        self.assertEqual(module_item_list[0].course_id, self.course.id)

    # get_module_item()
    async def test_get_module_item(self, m):
        register_uris({"module": ["get_module_item_by_id"]}, m)

        module_item_by_id = await self.module.get_module_item(1)

        self.assertIsInstance(module_item_by_id, ModuleItem)
        self.assertTrue(hasattr(module_item_by_id, "course_id"))
        self.assertEqual(module_item_by_id.course_id, self.course.id)

        module_item_by_obj = await self.module.get_module_item(module_item_by_id)

        self.assertIsInstance(module_item_by_obj, ModuleItem)
        self.assertTrue(hasattr(module_item_by_obj, "course_id"))
        self.assertEqual(module_item_by_obj.course_id, self.course.id)

    # create_module_item()
    async def test_create_module_item(self, m):
        register_uris({"module": ["create_module_item"]}, m)

        module_item = await self.module.create_module_item(
            module_item={"type": "Assignment", "content_id": 1}
        )

        self.assertIsInstance(module_item, ModuleItem)
        self.assertTrue(hasattr(module_item, "course_id"))
        self.assertEqual(module_item.course_id, self.course.id)

    async def test_create_module_item_fail1(self, m):
        with self.assertRaises(RequiredFieldMissing):
            await self.module.create_module_item(module_item={"content_id": 1})

    async def test_create_module_item_fail2(self, m):
        with self.assertRaises(RequiredFieldMissing):
            await self.module.create_module_item(module_item={"type": "Assignment"})

    async def test_create_module_item_unrequired_success(self, m):
        register_uris({"module": ["create_module_item"]}, m)

        module_item = await self.module.create_module_item(module_item={"type": "SubHeader"})
        self.assertIsInstance(module_item, ModuleItem)

    # __str__
    def test__str__(self, m):
        string = str(self.module)
        self.assertIsInstance(string, str)


@aioresponse_mock
class TestModuleItem(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            requires = {
                "course": ["get_by_id", "get_module_by_id"],
                "module": ["get_module_item_by_id"],
            }
            register_uris(requires, m)

            self.course = await self.canvas.get_course(1)
            self.module = await self.course.get_module(1)
            self.module_item = await self.module.get_module_item(1)

    async def asyncTearDown(self):
        await self.canvas.close()

    # edit()
    async def test_edit_module_item(self, m):
        register_uris({"module": ["edit_module_item"]}, m)

        title = "New Title"
        edited_module_item = await self.module_item.edit(module_item={"title": title})

        self.assertIsInstance(edited_module_item, ModuleItem)
        self.assertTrue(hasattr(edited_module_item, "title"))
        self.assertEqual(edited_module_item.title, title)
        self.assertTrue(hasattr(edited_module_item, "course_id"))
        self.assertEqual(edited_module_item.course_id, self.course.id)

    # delete()
    async def test_delete(self, m):
        register_uris({"module": ["delete_module_item"]}, m)

        deleted_module_item = await self.module_item.delete()

        self.assertIsInstance(deleted_module_item, ModuleItem)
        self.assertTrue(hasattr(deleted_module_item, "course_id"))
        self.assertEqual(deleted_module_item.course_id, self.course.id)

    # complete(course_id, True)
    async def test_complete(self, m):
        register_uris({"module": ["complete_module_item"]}, m)

        completed_module_item = await self.module_item.complete()

        self.assertIsInstance(completed_module_item, ModuleItem)
        self.assertTrue(hasattr(completed_module_item, "completion_requirement"))
        self.assertTrue(hasattr(completed_module_item, "course_id"))
        self.assertEqual(completed_module_item.course_id, self.course.id)

    # complete(course_id, False)
    async def test_uncomplete(self, m):
        register_uris({"module": ["uncomplete_module_item"]}, m)

        completed_module_item = await self.module_item.uncomplete()

        self.assertIsInstance(completed_module_item, ModuleItem)
        self.assertTrue(hasattr(completed_module_item, "completion_requirement"))
        self.assertTrue(hasattr(completed_module_item, "course_id"))
        self.assertEqual(completed_module_item.course_id, self.course.id)

    def test__str__(self, m):
        string = str(self.module_item)
        self.assertIsInstance(string, str)
