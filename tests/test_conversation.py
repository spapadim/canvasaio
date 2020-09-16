import unittest

from aioresponses import aioresponses

from canvasaio import Canvas
from canvasaio.conversation import Conversation
from tests import settings
from tests.util import register_uris, aioresponse_mock


@aioresponse_mock
class TestConversation(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with aioresponses() as m:
            register_uris({"conversation": ["get_by_id"]}, m)

            self.conversation = await self.canvas.get_conversation(1)

    async def asyncTearDown(self):
        await self.canvas.close()

    # __str__()
    def test__str__(self, m):
        string = str(self.conversation)
        self.assertIsInstance(string, str)

    # edit()
    async def test_edit(self, m):
        register_uris({"conversation": ["edit_conversation"]}, m)

        new_subject = "conversations api example"
        success = await self.conversation.edit(subject=new_subject)
        self.assertTrue(success)

    async def test_edit_fail(self, m):
        requires = {"conversation": ["get_by_id_2", "edit_conversation_fail"]}
        register_uris(requires, m)

        temp_convo = await self.canvas.get_conversation(2)
        self.assertFalse(await temp_convo.edit())

    # delete()
    async def test_delete(self, m):
        register_uris({"conversation": ["delete_conversation"]}, m)

        success = await self.conversation.delete()
        self.assertTrue(success)

    async def test_delete_fail(self, m):
        requires = {"conversation": ["get_by_id_2", "delete_conversation_fail"]}
        register_uris(requires, m)

        temp_convo = await self.canvas.get_conversation(2)
        self.assertFalse(await temp_convo.delete())

    # add_recipients()
    async def test_add_recipients(self, m):
        register_uris({"conversation": ["add_recipients"]}, m)

        recipients = {"bob": 1, "joe": 2}
        string_bob = "Bob was added to the conversation by Hank TA"
        string_joe = "Joe was added to the conversation by Hank TA"
        result = await self.conversation.add_recipients(
            [recipients["bob"], recipients["joe"]]
        )
        self.assertTrue(hasattr(result, "messages"))
        self.assertEqual(len(result.messages), 2)
        self.assertEqual(result.messages[0]["body"], string_bob)
        self.assertEqual(result.messages[1]["body"], string_joe)

    # add_message()
    async def test_add_message(self, m):
        register_uris({"conversation": ["add_message"]}, m)

        test_string = "add_message test body"
        result = await self.conversation.add_message(test_string)
        self.assertIsInstance(result, Conversation)
        self.assertEqual(len(result.messages), 1)
        self.assertEqual(result.messages[0]["id"], 3)

    # delete_message()
    async def test_delete_message(self, m):
        register_uris({"conversation": ["delete_message"]}, m)

        id_list = [1]
        result = await self.conversation.delete_messages(id_list)
        self.assertIn("subject", result)
        self.assertEqual(result["id"], 1)
