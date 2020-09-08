import asynctest


from os import getenv

from pytgbot import Bot

TEST_USER_ID = int(getenv('USER_ID'))
TEST_BOT_ID = int(getenv('BOT_ID'))
TEST_USER_AUTH = getenv('USER_AUTH')  # 'user123@sdsdfsdfs'
TEST_BOT_AUTH = getenv('BOT_AUTH')    # 'bot123:sdsdfsdfs'


class LiveTestCase(asynctest.TestCase):
    def setUp(self) -> None:
        self.api_bot = Bot(TEST_BOT_AUTH)
        self.user_bot = Bot(TEST_USER_AUTH)
    # end def

    async def test_send_location(self):
        self.user_bot.send_message()


if __name__ == '__main__':
    unittest.main()
