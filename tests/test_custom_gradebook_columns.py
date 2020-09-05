import unittest
from urllib.parse import quote

from aioresponses import aioresponses, CallbackResult

from canvasaio import Canvas
from canvasaio.custom_gradebook_columns import ColumnData
from canvasaio.paginated_list import PaginatedList
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestCustomGradebookColumn(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            register_uris({"course": ["get_by_id", "get_custom_columns"]}, m)

            self.course = await self.canvas.get_course(1)
            self.gradebook_column = await self.course.get_custom_columns()[1]

    async def asyncTearDown(self) -> None:
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.gradebook_column)
        self.assertIsInstance(string, str)

    # delete()
    async def test_delete(self, m):
        register_uris({"custom_gradebook_columns": ["delete"]}, m)

        success = await self.gradebook_column.delete()
        self.assertTrue(success)

    # get_column_entries()
    async def test_get_column_entries(self, m):
        register_uris({"custom_gradebook_columns": ["get_column_entries"]}, m)

        column_entries = self.gradebook_column.get_column_entries()

        self.assertIsInstance(column_entries, PaginatedList)

        column_entries = [entry async for entry in column_entries]

        self.assertIsInstance(column_entries[0], ColumnData)
        self.assertTrue(hasattr(column_entries[0], "gradebook_column_id"))
        self.assertEqual(
            column_entries[0].gradebook_column_id, self.gradebook_column.id
        )

    # reorder_custom_columns()
    async def test_reorder_custom_columns(self, m):
        # Custom callback to test that params are set correctly
        async def callback(url, data, **kwargs):
            self.assertEqual(1, len(data._fields))
            field_type_options, field_headers, field_value = data._fields[0]
            self.assertEqual("order", field_type_options["name"])
            self.assertEqual("1,2,3", field_value)
            return CallbackResult(status=200, body='{"reorder": true, "order": [1, 2, 3]}')

        m.add(
            settings.BASE_URL + "/api/v1/courses/1/custom_gradebook_columns/reorder",
            method="POST",
            callback=callback,
        )

        order = [1, 2, 3]
        columns = await self.gradebook_column.reorder_custom_columns(order=order)
        self.assertTrue(columns)

    async def test_reorder_custom_columns_tuple(self, m):
        register_uris({"custom_gradebook_columns": ["reorder_custom_columns"]}, m)

        order = (1, 2, 3)
        columns = await self.gradebook_column.reorder_custom_columns(order=order)
        self.assertTrue(columns)

    async def test_reorder_custom_columns_comma_separated_string(self, m):
        register_uris({"custom_gradebook_columns": ["reorder_custom_columns"]}, m)

        order = "1,2,3"
        gradebook = await self.gradebook_column.reorder_custom_columns(order=order)
        self.assertTrue(gradebook)

    async def test_reorder_custom_columns_invalid_input(self, m):
        order = "invalid string"
        with self.assertRaises(ValueError):
            await self.gradebook_column.reorder_custom_columns(order=order)

    # update_custom_column()
    async def test_update_custom_column(self, m):
        register_uris({"custom_gradebook_columns": ["update_custom_column"]}, m)

        new_title = "Example title"
        await self.gradebook_column.update_custom_column(column={"title": new_title})
        self.assertEqual(self.gradebook_column.title, new_title)


@aioresponse_mock
class TestColumnData(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            requires = {
                "course": ["get_by_id", "get_custom_columns"],
                "custom_gradebook_columns": ["get_column_entries"],
            }
            register_uris(requires, m)

            self.course = await self.canvas.get_course(1)
            self.gradebook_column = await self.course.get_custom_columns()[1]
            self.data = await self.gradebook_column.get_column_entries()[1]

    async def asyncTearDown(self) -> None:
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.data)
        self.assertIsInstance(string, str)

    # update_column_data()
    async def test_update_column_data(self, m):
        register_uris({"custom_gradebook_columns": ["update_column_data"]}, m)

        new_content = "Updated content"
        await self.data.update_column_data(column_data={"content": new_content})
        self.assertEqual(self.data.content, new_content)
