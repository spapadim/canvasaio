import unittest
from os.path import isfile

from aioresponses import aioresponses

from canvasaio import Canvas
from canvasaio.file import File
from tests import settings
from tests.util import cleanup_file
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestFile(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            register_uris(
                {"course": ["get_by_id", "list_course_files", "list_course_files2"]}, m
            )

            self.course = await self.canvas.get_course(1)
            self.file = await self.course.get_files()[0]

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.file)
        self.assertIsInstance(string, str)

    # delete()
    async def test_delete_file(self, m):
        register_uris({"file": ["delete_file"]}, m)

        deleted_file = await self.file.delete()

        self.assertIsInstance(deleted_file, File)
        self.assertTrue(hasattr(deleted_file, "display_name"))
        self.assertEqual(deleted_file.display_name, "Bad File.docx")

    # download()
    async def test_download_file(self, m):
        register_uris({"file": ["file_download"]}, m)
        try:
            await self.file.download("canvasaio_file_download_test.txt")
            self.assertTrue(isfile("canvasaio_file_download_test.txt"))
            with open("canvasaio_file_download_test.txt") as downloaded_file:
                self.assertEqual(downloaded_file.read(), '"file contents are here"')
        finally:
            cleanup_file("canvasaio_file_download_test.txt")

    # contents()
    async def test_contents_file(self, m):
        register_uris({"file": ["file_contents"]}, m)
        contents = await self.file.get_contents()
        self.assertEqual(contents, '"Hello there"')
