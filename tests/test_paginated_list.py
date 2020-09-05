import unittest

from aioresponses import aioresponses

from canvasaio import Canvas
from canvasaio.enrollment_term import EnrollmentTerm
from canvasaio.paginated_list import PaginatedList
from canvasaio.user import User
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestPaginatedList(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)
        self.requester = self.canvas._Canvas__requester

    async def asyncTearDown(self):
        await self.canvas.close()

    # various length lists
    async def test_paginated_list_empty(self, m):
        register_uris({"paginated_list": ["empty"]}, m)

        pag_list = PaginatedList(User, self.requester, "GET", "empty_list")
        item_list = [item async for item in pag_list]
        self.assertEqual(len(item_list), 0)

    async def test_paginated_list_single(self, m):
        register_uris({"paginated_list": ["single"]}, m)

        pag_list = PaginatedList(User, self.requester, "GET", "single_item")
        item_list = [item async for item in pag_list]
        self.assertEqual(len(item_list), 1)
        self.assertIsInstance(item_list[0], User)

    async def test_paginated_list_two_one_page(self, m):
        register_uris({"paginated_list": ["2_1_page"]}, m)

        pag_list = PaginatedList(User, self.requester, "GET", "two_objects_one_page")
        item_list = [item async for item in pag_list]
        self.assertEqual(len(item_list), 2)
        self.assertIsInstance(item_list[0], User)

    async def test_paginated_list_four_two_pages(self, m):
        register_uris({"paginated_list": ["4_2_pages_p1", "4_2_pages_p2"]}, m)

        pag_list = PaginatedList(User, self.requester, "GET", "four_objects_two_pages")
        item_list = [item async for item in pag_list]
        self.assertEqual(len(item_list), 4)
        self.assertIsInstance(item_list[0], User)

    async def test_paginated_list_six_three_pages(self, m):
        requires = {"paginated_list": ["6_3_pages_p1", "6_3_pages_p2", "6_3_pages_p3"]}
        register_uris(requires, m)

        pag_list = PaginatedList(User, self.requester, "GET", "six_objects_three_pages")
        item_list = [item async for item in pag_list]
        self.assertEqual(len(item_list), 6)
        self.assertIsInstance(item_list[0], User)

    # reusing iterator
    async def test_iterator(self, m):
        requires = {"paginated_list": ["6_3_pages_p1", "6_3_pages_p2", "6_3_pages_p3"]}
        register_uris(requires, m)

        pag_list = PaginatedList(User, self.requester, "GET", "six_objects_three_pages")
        list_1 = [item async for item in pag_list]
        list_2 = [item async for item in pag_list]
        self.assertEqual(list_1, list_2)

    # get item
    async def test_getitem_first(self, m):
        requires = {"paginated_list": ["6_3_pages_p1", "6_3_pages_p2", "6_3_pages_p3"]}
        register_uris(requires, m)

        pag_list = PaginatedList(User, self.requester, "GET", "six_objects_three_pages")
        first_item = await pag_list[0]
        self.assertIsInstance(first_item, User)

    async def test_getitem_second_page(self, m):
        requires = {"paginated_list": ["6_3_pages_p1", "6_3_pages_p2", "6_3_pages_p3"]}
        register_uris(requires, m)

        pag_list = PaginatedList(User, self.requester, "GET", "six_objects_three_pages")
        third_item = await pag_list[2]
        self.assertIsInstance(third_item, User)

    # slicing
    async def test_slice_beginning(self, m):
        requires = {"paginated_list": ["6_3_pages_p1", "6_3_pages_p2", "6_3_pages_p3"]}
        register_uris(requires, m)

        pag_list = PaginatedList(User, self.requester, "GET", "six_objects_three_pages")
        first_two_items = pag_list[:2]
        item_list = [item async for item in first_two_items]
        self.assertEqual(len(item_list), 2)
        self.assertIsInstance(item_list[0], User)
        self.assertTrue(hasattr(item_list[0], "id"))
        self.assertEqual(item_list[0].id, "1")

    async def test_slice_middle(self, m):
        requires = {"paginated_list": ["6_3_pages_p1", "6_3_pages_p2", "6_3_pages_p3"]}
        register_uris(requires, m)

        pag_list = PaginatedList(User, self.requester, "GET", "six_objects_three_pages")
        middle_two_items = pag_list[2:4]
        item_list = [item async for item in middle_two_items]
        self.assertEqual(len(item_list), 2)
        self.assertIsInstance(item_list[0], User)
        self.assertTrue(hasattr(item_list[0], "id"))
        self.assertEqual(item_list[0].id, "3")

    async def test_slice_end(self, m):
        requires = {"paginated_list": ["6_3_pages_p1", "6_3_pages_p2", "6_3_pages_p3"]}
        register_uris(requires, m)

        pag_list = PaginatedList(User, self.requester, "GET", "six_objects_three_pages")
        middle_two_items = pag_list[4:6]
        item_list = [item async for item in middle_two_items]
        self.assertEqual(len(item_list), 2)
        self.assertIsInstance(item_list[0], User)
        self.assertTrue(hasattr(item_list[0], "id"))
        self.assertEqual(item_list[0].id, "5")

    async def test_slice_oversize(self, m):
        requires = {"paginated_list": ["4_2_pages_p1", "4_2_pages_p2"]}
        register_uris(requires, m)

        pag_list = PaginatedList(User, self.requester, "GET", "four_objects_two_pages")
        oversized_slice = pag_list[0:10]
        item_list = [item async for item in oversized_slice]
        self.assertEqual(len(item_list), 4)

    async def test_slice_out_of_bounds(self, m):
        requires = {"paginated_list": ["4_2_pages_p1", "4_2_pages_p2"]}
        register_uris(requires, m)

        pag_list = PaginatedList(User, self.requester, "GET", "four_objects_two_pages")
        out_of_bounds = pag_list[4:5]
        item_list = [item async for item in out_of_bounds]
        self.assertEqual(len(item_list), 0)

    # __repr__()
    def test_repr(self, m):
        requires = {"paginated_list": ["6_3_pages_p1", "6_3_pages_p2", "6_3_pages_p3"]}
        register_uris(requires, m)

        pag_list = PaginatedList(User, self.requester, "GET", "six_objects_three_pages")
        self.assertEqual(pag_list.__repr__(), "<PaginatedList of type User>")

    async def test_root_element_incorrect(self, m):
        register_uris({"account": ["get_enrollment_terms"]}, m)

        pag_list = PaginatedList(
            EnrollmentTerm, self.requester, "GET", "accounts/1/terms", _root="wrong"
        )

        with self.assertRaises(ValueError):
            await pag_list[0]

    async def test_root_element(self, m):
        register_uris({"account": ["get_enrollment_terms"]}, m)

        pag_list = PaginatedList(
            EnrollmentTerm,
            self.requester,
            "GET",
            "accounts/1/terms",
            _root="enrollment_terms",
        )

        self.assertIsInstance(await pag_list[0], EnrollmentTerm)

    async def test_negative_index(self, m):
        # Regression test for https://github.com/ucfopen/canvasapi/issues/305
        # Ensure that we can't use negative indexing, even after loading a page

        register_uris({"paginated_list": ["4_2_pages_p1", "4_2_pages_p2"]}, m)
        pag_list = PaginatedList(User, self.requester, "GET", "four_objects_two_pages")
        await pag_list[0]

        with self.assertRaises(IndexError):
            await pag_list[-1]

    async def test_negative_index_for_slice_start(self, m):
        # Regression test for https://github.com/ucfopen/canvasapi/issues/305
        # Ensure that we can't slice using a negative index as the start item

        register_uris({"paginated_list": ["4_2_pages_p1", "4_2_pages_p2"]}, m)
        pag_list = PaginatedList(User, self.requester, "GET", "four_objects_two_pages")
        await pag_list[0]

        with self.assertRaises(IndexError):
            pag_list[-1:1]

    async def test_negative_index_for_slice_end(self, m):
        # Regression test for https://github.com/ucfopen/canvasapi/issues/305
        # Ensure that we can't slice using a negative index as the end item

        register_uris({"paginated_list": ["4_2_pages_p1", "4_2_pages_p2"]}, m)
        pag_list = PaginatedList(User, self.requester, "GET", "four_objects_two_pages")
        await pag_list[0]

        with self.assertRaises(IndexError):
            pag_list[:-1]
