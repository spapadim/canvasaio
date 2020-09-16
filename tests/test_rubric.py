import unittest

from aioresponses import aioresponses

from canvasaio import Canvas
from canvasaio.rubric import RubricAssociation
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestGradingStandard(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            register_uris({"course": ["get_by_id", "get_rubric_single"]}, m)

            self.course = await self.canvas.get_course(1)
            self.rubric = await self.course.get_rubric(1)

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.rubric)
        self.assertIsInstance(string, str)


@aioresponse_mock
class TestRubricAssociation(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            register_uris(
                {
                    "course": [
                        "get_by_id",
                        "create_rubric_with_association",
                        "create_rubric_association",
                    ]
                },
                m,
            )

            self.course = await self.canvas.get_course(1)
            self.rubric = await self.course.create_rubric()
            self.association = await self.course.create_rubric_association()

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.rubric["rubric_association"])
        self.assertIsInstance(string, str)

    # update
    async def test_update(self, m):
        register_uris({"rubric": ["update_rubric_association"]}, m)

        self.assertEqual(self.association.id, 4)

        rubric_association = await self.association.update()

        self.assertEqual(rubric_association, self.association)
        self.assertEqual(rubric_association.id, 5)
        self.assertIsInstance(rubric_association, RubricAssociation)
        self.assertEqual(rubric_association.association_type, "Assignment")

    # delete
    async def test_delete(self, m):
        register_uris({"rubric": ["delete_rubric_association"]}, m)

        rubric_association = await self.association.delete()

        self.assertIsInstance(rubric_association, RubricAssociation)
        self.assertEqual(rubric_association.id, 4)
        self.assertEqual(rubric_association.association_type, "Assignment")
