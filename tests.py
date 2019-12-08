import json
import unittest, asynctest
from datetime import timezone

from telethon.tl.types import *
import datetime

false = False
true = True

class FakeClient(object):
    def get_entity(self, obj):
        return {
            ""
        }[obj]

class MyTestCase(asynctest.TestCase):
    async def test_supergroup_add_other_user(self):
        event = UpdateNewChannelMessage(
            message=MessageService(
                id=3496,
                to_id=PeerChannel(
                    channel_id=1032895287
                ),
                date=datetime(2019, 12, 7, 18, 22, 54, tzinfo=timezone.utc),
                action=MessageActionChatAddUser(users=[357231198]),
                out=False,
                mentioned=False,
                media_unread=False,
                silent=False,
                post=False,
                legacy=False,
                from_id=10717954,
                reply_to_msg_id=None
            ),
            pts=4320,
            pts_count=1
        )
        from serializer import to_web_api
        x = await to_web_api(event, None)

        y = {
            "message": {
                "chat": {
                    "id": -1001032895287,
                    "title": "Test Supergroup [test] #PUBLIC",
                    "type": "supergroup"
                },
                "date": 1575742974,
                "from": {
                    "first_name": "luckydonald",
                    "id": 10717954,
                    "is_bot": False,
                    "language_code": "en",
                    "username": "luckydonald"
                },
                "message_id": 3510,
                # "new_chat_member": {
                #     "first_name": "Bonbotics",
                #     "id": 357231198,
                #     "is_bot": False,
                #     "username": "bonbotics"
                # },
                "new_chat_members": [
                    {
                        "first_name": "Bonbotics",
                        "id": 357231198,
                        "is_bot": False,
                        "username": "bonbotics"
                    }
                ],
                # "new_chat_participant": {
                #     "first_name": "Bonbotics",
                #     "id": 357231198,
                #     "is_bot": False,
                #     "username": "bonbotics"
                # }
            },
            "update_id": 4320
        }
        self.assertEqual(
            json.dumps(x.to_array(), indent=2, sort_keys=True),
            json.dumps(y, indent=2, sort_keys=True),
            'generated vs real one'
        )

    # end def

    async def test_channel_rename(self):
        event = UpdateNewChannelMessage(
            message=MessageService(
                id=168, to_id=PeerChannel(
                    channel_id=1443587969
                ),
                date=datetime(2019, 12, 7, 23, 31, tzinfo=timezone.utc),
                action=MessageActionChatEditTitle(title='Derp [test]'),
                out=False,
                mentioned=False,
                media_unread=False,
                silent=False,
                post=False,
                legacy=False,
                from_id=10717954,
                reply_to_msg_id=None
            ),
            pts=171,
            pts_count=1)

        from serializer import to_web_api
        x = await to_web_api(event, None)

        y = {
            "message": {
                "chat": {
                    "id": -1001443587969,
                    "title": "Derp [test]",
                    "type": "supergroup"
                },
                "date": 1575761460,
                "from": {
                    "first_name": "luckydonald",
                    "id": 10717954,
                    "is_bot": False,
                    "language_code": "en",
                    "username": "luckydonald"
                },
                "message_id": 168,
                "new_chat_title": "Derp [test]"
            },
            "update_id": 862109754
        }
        self.assertEqual(
            json.dumps(x.to_array(), indent=2, sort_keys=True),
            json.dumps(y, indent=2, sort_keys=True),
            'generated vs real one'
        )
    # end def

    async def test_channel_message(self):
        event = UpdateNewChannelMessage(
            message=Message(
                id=184,
                to_id=PeerChannel(
                    channel_id=1443587969
                ),
                date=datetime.datetime(2019, 12, 8, 1, 22, 38, tzinfo=datetime.timezone.utc),
                message='🧑\u200d💻',
                out=False,
                mentioned=False,
                media_unread=False,
                silent=False,
                post=False,
                from_scheduled=False,
                legacy=False,
                edit_hide=False,
                from_id=10717954,
                fwd_from=None,
                via_bot_id=None,
                reply_to_msg_id=None,
                media=None,
                reply_markup=None,
                entities=[],
                views=None,
                edit_date=None,
                post_author=None,
                grouped_id=None,
                restriction_reason=[]
            ),
            pts=187,
            pts_count=1
        )

        from serializer import to_web_api
        x = await to_web_api(event, None)

        y = {
            "message": {
                "chat": {
                    "id": -1001443587969,
                    "title": "Derp [test] rename",
                    "type": "supergroup"
                },
                "date": 1575768158,
                "from": {
                    "first_name": "luckydonald",
                    "id": 10717954,
                    "is_bot": false,
                    "language_code": "en",
                    "username": "luckydonald"
                },
                "message_id": 184,
                "text": "🧑‍💻"
            },
            "update_id": 184
        }
        self.assertEqual(
            json.dumps(x.to_array(), indent=2, sort_keys=True),
            json.dumps(y, indent=2, sort_keys=True),
            'generated vs real one'
        )
    # end def
# end class

if __name__ == '__main__':
    unittest.main()
