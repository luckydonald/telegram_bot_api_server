import json
import unittest, asynctest
from datetime import timezone

from telethon.tl.types import *
from telethon.tl.patched import *
import datetime
from typing import Dict

from serializer import to_web_api

false = False
true = True


class FakeClient(object):
    def __init__(self, lookups: Dict[int, TypePeer], update_id: int):
        self.lookups = lookups
        self.update_id = update_id
    # end if

    async def get_entity(self, peer_id):
        return self.lookups[peer_id]
    # end def
# end clas


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

        expected = {
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

        result = await to_web_api(event, None)
        result = result.to_array()

        self.assertEqual(
            json.dumps(result,   indent=2, sort_keys=True),
            json.dumps(expected, indent=2, sort_keys=True),
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
            pts_count=1
        )

        expected = {
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

        result = await to_web_api(event, None)
        result = result.to_array()

        self.assertEqual(
            json.dumps(expected, indent=2, sort_keys=True),
            json.dumps(result,   indent=2, sort_keys=True),
            'real one vs generated one'
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

        expected = {
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

        result = await to_web_api(event, None)
        result = result.to_array()

        self.assertEqual(
            json.dumps(expected, indent=2, sort_keys=True),
            json.dumps(result,   indent=2, sort_keys=True),
            'real one vs generated one'
        )
    # end def

    async def test_channel_message_2(self):
        event = UpdateNewChannelMessage(
            message=Message(
                id=20101,
                to_id=PeerChannel(channel_id=1127537892),
                date=datetime.datetime(2019, 12, 8, 12, 26, 9, tzinfo=datetime.timezone.utc),
                message='No-nonsense sorting algorithm\nhttps://redd.it/e7sjqu\n\nby @programmer_humor',
                out=False,
                mentioned=False,
                media_unread=False,
                silent=False,
                post=True,
                from_scheduled=False,
                legacy=False,
                edit_hide=False,
                from_id=None,
                fwd_from=None,
                via_bot_id=None,
                reply_to_msg_id=None,
                media=MessageMediaPhoto(
                    photo=Photo(
                        id=5433926979075288090,
                        access_hash=-8890268965132848980,
                        file_reference=b'\x02C4\xdc\xe4\x00\x00N\x85]\xec\xeb\xe1\x8f\x89\xd1\xac\x8eJ\xe7\xfe\xa5\x96\xea\xdea\x88\xf4\x13',
                        date=datetime.datetime(2019, 12, 8, 12, 26, 9, tzinfo=datetime.timezone.utc),
                        sizes=[
                            PhotoStrippedSize(type='i', bytes=b'\x01\x16(\xae\xbffq\x12\xe7\x07o\xcf\xc7z\xaf\xb8c\x18\x1f\x95H\xbfpp:g\xa7\xff\x00Z\x8c}>\x98\xff\x00\xebP\x04LC6x\x1e\xc0Sj~\xbd\x87\xe5\xff\x00\xd6\xa3\x19\xed\xfa\x7f\xf5\xa9\x81\x05\x14\xf7,\t\xc8\xc0\xfaQ@\r\xdf\xc7o\xc8R\xee>\xdf\x90\xa2\x8a\x007\x1fo\xc8Sh\xa2\x80\n(\xa2\x80?'),
                            PhotoSize(type='m', location=FileLocationToBeDeprecated(volume_id=257712969, local_id=167617), w=320, h=176, size=16636),
                            PhotoSize(type='x', location=FileLocationToBeDeprecated(volume_id=257712969, local_id=167615), w=720, h=395, size=34533)
                        ],
                        dc_id=2,
                        has_stickers=False
                    ),
                    ttl_seconds=None
                ),
                reply_markup=None,
                entities=[
                    MessageEntityUrl(offset=30, length=22),
                    MessageEntityMention(offset=57, length=17)
                ],
                views=1,
                edit_date=None,
                post_author=None,
                grouped_id=None,
                restriction_reason=[]
            ),
            pts=20134,
            pts_count=1
        )

        expected = {
            "message": "see test_channel_message_2_forwareded, just witout the forward.",
            "update_id": 184
        }

        result = await to_web_api(event, None)
        result = result.to_array()

        self.assertEqual(
            json.dumps(expected, indent=2, sort_keys=True),
            json.dumps(result,   indent=2, sort_keys=True),
            'real one vs generated one'
        )
    # end def

    async def test_channel_message_2_forward_from_channel(self):
        """
        Same as test_channel_message_2, but forwarded to another channel.
        :return:
        """
        client = FakeClient(
            lookups={
                10717954: User(id=10717954, is_self=False, contact=False, mutual_contact=False, deleted=False, bot=False, bot_chat_history=False, bot_nochats=False, verified=False, restricted=False, min=False, bot_inline_geo=False, support=False, scam=False, access_hash=-2993714178598625124, first_name='luckydonald', last_name=None, username='luckydonald', phone=None, photo=UserProfilePhoto(photo_id=46033262366284583, photo_small=FileLocationToBeDeprecated(volume_id=263834989, local_id=209571), photo_big=FileLocationToBeDeprecated(volume_id=263834989, local_id=209573), dc_id=2), status=UserStatusRecently(), bot_info_version=None, restriction_reason=[], bot_inline_placeholder=None, lang_code='en'),
                -1001443587969: Channel(id=1443587969, title='Derp [test] rename', photo=ChatPhoto(photo_small=FileLocationToBeDeprecated(volume_id=226613135, local_id=158488), photo_big=FileLocationToBeDeprecated(volume_id=226613135, local_id=158490), dc_id=2), date=datetime.datetime(2019, 6, 16, 22, 38, 57, tzinfo=datetime.timezone.utc), version=0, creator=False, left=False, broadcast=False, verified=False, megagroup=True, restricted=False, signatures=False, min=False, scam=False, has_link=False, has_geo=False, slowmode_enabled=False, access_hash=-7101147752375680853, username=None, restriction_reason=[], admin_rights=None, banned_rights=None, default_banned_rights=ChatBannedRights(until_date=datetime.datetime(2038, 1, 19, 3, 14, 7, tzinfo=datetime.timezone.utc), view_messages=False, send_messages=False, send_media=False, send_stickers=False, send_gifs=False, send_games=False, send_inline=False, embed_links=False, send_polls=False, change_info=False, invite_users=False, pin_messages=False), participants_count=None),
                -1001127537892: Channel(id=1127537892, title='Programmer Humor', photo=ChatPhoto(photo_small=FileLocationToBeDeprecated(volume_id=226613135, local_id=158488), photo_big=FileLocationToBeDeprecated(volume_id=226613135, local_id=158490), dc_id=2), date=datetime.datetime(2019, 6, 16, 22, 38, 57, tzinfo=datetime.timezone.utc), version=0, creator=False, left=False, broadcast=False, verified=False, megagroup=False, restricted=False, signatures=False, min=False, scam=False, has_link=False, has_geo=False, slowmode_enabled=False, access_hash=-7101147752375680853, username='programmer_humor', restriction_reason=[], admin_rights=None, banned_rights=None, default_banned_rights=ChatBannedRights(until_date=datetime.datetime(2038, 1, 19, 3, 14, 7, tzinfo=datetime.timezone.utc), view_messages=False, send_messages=False, send_media=False, send_stickers=False, send_gifs=False, send_games=False, send_inline=False, embed_links=False, send_polls=False, change_info=False, invite_users=False, pin_messages=False), participants_count=None),
            },
            update_id=445804458
        )
        event = UpdateNewChannelMessage(
            message=Message(
                id=197,
                to_id=PeerChannel(channel_id=1443587969),
                date=datetime.datetime(2019, 12, 8, 12, 33, 53, tzinfo=datetime.timezone.utc),
                message='No-nonsense sorting algorithm\nhttps://redd.it/e7sjqu\n\nby @programmer_humor',
                out=False,
                mentioned=False,
                media_unread=False,
                silent=False,
                post=False,
                from_scheduled=False,
                legacy=False,
                edit_hide=False,
                from_id=10717954,
                fwd_from=MessageFwdHeader(
                    date=datetime.datetime(2019, 12, 8, 12, 26, 9, tzinfo=datetime.timezone.utc),
                    from_id=None,
                    from_name=None,
                    channel_id=1127537892,
                    channel_post=20101,
                    post_author=None,
                    saved_from_peer=None,
                    saved_from_msg_id=None
                ),
                via_bot_id=None,
                reply_to_msg_id=None,
                media=MessageMediaPhoto(
                    photo=Photo(
                        id=5433926979075288090,
                        access_hash=-8890268965132848980,
                        file_reference=b'\x02V\x0bg\x81\x00\x00\x00\xc5]\xec\xed\xb1\x83\x97\x8c\x8e\x03\x93;\xc2\xac\xedAO\xdc\x9e\xea\x84',
                        date=datetime.datetime(2019, 12, 8, 12, 26, 9, tzinfo=datetime.timezone.utc),
                        sizes=[
                            PhotoStrippedSize(type='i', bytes=b'\x01\x16(\xae\xbffq\x12\xe7\x07o\xcf\xc7z\xaf\xb8c\x18\x1f\x95H\xbfpp:g\xa7\xff\x00Z\x8c}>\x98\xff\x00\xebP\x04LC6x\x1e\xc0Sj~\xbd\x87\xe5\xff\x00\xd6\xa3\x19\xed\xfa\x7f\xf5\xa9\x81\x05\x14\xf7,\t\xc8\xc0\xfaQ@\r\xdf\xc7o\xc8R\xee>\xdf\x90\xa2\x8a\x007\x1fo\xc8Sh\xa2\x80\n(\xa2\x80?'),
                            PhotoSize(type='m', location=FileLocationToBeDeprecated(volume_id=257712969, local_id=167617), w=320, h=176, size=16636),
                            PhotoSize(type='x', location=FileLocationToBeDeprecated(volume_id=257712969, local_id=167615), w=720, h=395, size=34533)
                        ],
                        dc_id=2,
                        has_stickers=False
                    ),
                    ttl_seconds=None
                ),
                reply_markup=None,
                entities=[
                    MessageEntityUrl(offset=30, length=22),
                    MessageEntityMention(offset=57, length=17)
                ],
                views=366,
                edit_date=None,
                post_author=None,
                grouped_id=None,
                restriction_reason=[]
            ),
            pts=200,
            pts_count=1
        )

        expected = {
            "message": {
                "caption": "No-nonsense sorting algorithm\nhttps://redd.it/e7sjqu\n\nby @programmer_humor",
                "caption_entities": [
                    {
                        "length": 22,
                        "offset": 30,
                        "type": "url"
                    },
                    {
                        "length": 17,
                        "offset": 57,
                        "type": "mention"
                    }
                ],
                "chat": {
                    "id": -1001443587969,
                    "title": "Derp [test] rename",
                    "type": "supergroup"
                },
                "date": 1575808433,
                "forward_date": 1575807969,
                "forward_from_chat": {
                    "id": -1001127537892,
                    "title": "Programmer Humor",
                    "type": "channel",
                    "username": "programmer_humor"
                },
                "forward_from_message_id": 20101,
                "from": {
                    "first_name": "luckydonald",
                    "id": 10717954,
                    "is_bot": false,
                    "language_code": "en",
                    "username": "luckydonald"
                },
                "message_id": 197,
                "photo": [
                    {
                        "file_id": "AgADAgADGqwxG8wvaUsOaSFi8QJtVkljXA8ABAEAAwIAA20AA8GOAgABFgQ",
                        "file_size": 16636,
                        "height": 176,
                        "width": 320
                    },
                    {
                        "file_id": "AgADAgADGqwxG8wvaUsOaSFi8QJtVkljXA8ABAEAAwIAA3gAA7-OAgABFgQ",
                        "file_size": 34533,
                        "height": 395,
                        "width": 720
                    }
                ]
            },
            "update_id": 445804458
        }

        from serializer import to_web_api
        result = await to_web_api(event, client)
        result = result.to_array()

        # for i, result_photo in enumerate(expected["message"]["photo"]):
        #     expected_photo = result["message"]["photo"][i]
        #     self.assertEquals(len(expected_photo['file_id']), len(result_photo['file_id']), "length should be same")
        #     # now delete the file id's as we don't like that to butcher up the comparision
        #     del result_photo['file_id']
        #     del expected_photo['file_id']
        # # end if

        self.assertEqual(
            json.dumps(expected, indent=2, sort_keys=True),
            json.dumps(result,   indent=2, sort_keys=True),
            'real one vs generated one'
        )
    # end def

    async def test_channel_forward_from_user(self):
        client = FakeClient(
            lookups={
                10717954: User(id=10717954, is_self=False, contact=False, mutual_contact=False, deleted=False, bot=False, bot_chat_history=False, bot_nochats=False, verified=False, restricted=False, min=False, bot_inline_geo=False, support=False, scam=False, access_hash=-2993714178598625124, first_name='luckydonald', last_name=None, username='luckydonald', phone=None, photo=UserProfilePhoto(photo_id=46033262366284583, photo_small=FileLocationToBeDeprecated(volume_id=263834989, local_id=209571), photo_big=FileLocationToBeDeprecated(volume_id=263834989, local_id=209573), dc_id=2), status=UserStatusRecently(), bot_info_version=None, restriction_reason=[], bot_inline_placeholder=None, lang_code='en'),
                -1001443587969: Channel(id=1443587969, title='Derp [test] rename', photo=ChatPhoto(photo_small=FileLocationToBeDeprecated(volume_id=226613135, local_id=158488), photo_big=FileLocationToBeDeprecated(volume_id=226613135, local_id=158490), dc_id=2), date=datetime.datetime(2019, 6, 16, 22, 38, 57, tzinfo=datetime.timezone.utc), version=0, creator=False, left=False, broadcast=False, verified=False, megagroup=True, restricted=False, signatures=False, min=False, scam=False, has_link=False, has_geo=False, slowmode_enabled=False, access_hash=-7101147752375680853, username=None, restriction_reason=[], admin_rights=None, banned_rights=None, default_banned_rights=ChatBannedRights(until_date=datetime.datetime(2038, 1, 19, 3, 14, 7, tzinfo=datetime.timezone.utc), view_messages=False, send_messages=False, send_media=False, send_stickers=False, send_gifs=False, send_games=False, send_inline=False, embed_links=False, send_polls=False, change_info=False, invite_users=False, pin_messages=False), participants_count=None),
                133378542: User(id=133378542, is_self=True, contact=False, mutual_contact=False, deleted=False, bot=True, bot_chat_history=True, bot_nochats=False, verified=False, restricted=False, min=False, bot_inline_geo=False, support=False, scam=False, access_hash=8294665920163040443, first_name='Test Bot i do tests with', last_name=None, username='test4458bot', phone=None, photo=None, status=None, bot_info_version=13, restriction_reason=[], bot_inline_placeholder='This bot is for testing purposes.', lang_code=None),
            },
            update_id=445804458
        )
        event = UpdateNewChannelMessage(
            message=Message(
                id=207,
                to_id=PeerChannel(channel_id=1443587969),
                date=datetime.datetime(2019, 12, 8, 15, 53, 50, tzinfo=datetime.timezone.utc),
                message='💚 Container forward_whitelist is now healthy',
                out=False,
                mentioned=False,
                media_unread=False,
                silent=False,
                post=False,
                from_scheduled=False,
                legacy=False,
                edit_hide=False,
                from_id=10717954,
                fwd_from=MessageFwdHeader(
                    date=datetime.datetime(2019, 6, 15, 4, 53, 16, tzinfo=datetime.timezone.utc),
                    from_id=133378542,
                    from_name=None,
                    channel_id=None,
                    channel_post=None,
                    post_author=None,
                    saved_from_peer=None,
                    saved_from_msg_id=None
                ),
                via_bot_id=None,
                reply_to_msg_id=None,
                media=None,
                reply_markup=None,
                entities=[
                    MessageEntityCode(offset=13, length=17)
                ],
                views=None,
                edit_date=None,
                post_author=None,
                grouped_id=None,
                restriction_reason=[]
            ),
            pts=211,
            pts_count=1
        )

        expected = {
            "message": {
                "chat": {
                    "id": -1001443587969,
                    "title": "Derp [test] rename",
                    "type": "supergroup"
                },
                "date": 1575820430,
                "entities": [
                    {
                        "length": 17,
                        "offset": 13,
                        "type": "code"
                    }
                ],
                "forward_date": 1560574396,
                "forward_from": {
                    "first_name": "Test Bot i do tests with",
                    "id": 133378542,
                    "is_bot": true,
                    "username": "test4458bot"
                },
                "from": {
                    "first_name": "luckydonald",
                    "id": 10717954,
                    "is_bot": false,
                    "language_code": "en",
                    "username": "luckydonald"
                },
                "message_id": 207,
                "text": "💚 Container forward_whitelist is now healthy"
            },
            "update_id": 445804458
        }

        from serializer import to_web_api
        result = await to_web_api(event, client)
        result = result.to_array()

        # for i, result_photo in enumerate(expected["message"]["photo"]):
        #     expected_photo = result["message"]["photo"][i]
        #     self.assertEquals(len(expected_photo['file_id']), len(result_photo['file_id']), "length should be same")
        #     # now delete the file id's as we don't like that to butcher up the comparision
        #     del result_photo['file_id']
        #     del expected_photo['file_id']
        # # end if

        self.assertEqual(
            json.dumps(expected, indent=2, sort_keys=True),
            json.dumps(result,   indent=2, sort_keys=True),
            'real one vs generated one'
        )
    # end def
# end class

if __name__ == '__main__':
    unittest.main()
