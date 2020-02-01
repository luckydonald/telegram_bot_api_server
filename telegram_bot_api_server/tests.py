import json
import unittest

import asynctest

from telethon.tl.types import *
from telethon.tl.patched import *
from telethon.tl.patched import Message
import datetime
from typing import Dict, Any, Tuple

from test_dict_diff import DictDiffer
from telegram_bot_api_server import serializer
from telegram_bot_api_server.serializer import to_web_api

# replace functions so we can use our fake client
serializer.get_entity = lambda c, o: c.get_entity(o)
async def get_reply_message_mock_proxy(e: Message, client_user_id: int):
    e._client: FakeClient
    return e._client.get_reply_message(e)
# end def
serializer.get_reply_message = get_reply_message_mock_proxy

false = False
true = True


RECYCLE_PEERS: Dict[int, TypePeer] = {
    10717954: User(id=10717954, is_self=False, contact=False, mutual_contact=False, deleted=False, bot=False, bot_chat_history=False, bot_nochats=False, verified=False, restricted=False, min=False, bot_inline_geo=False, support=False, scam=False, access_hash=-2993714178598625124, first_name='luckydonald', last_name=None, username='luckydonald', phone=None, photo=UserProfilePhoto(photo_id=46033262366284583, photo_small=FileLocationToBeDeprecated(volume_id=263834989, local_id=209571), photo_big=FileLocationToBeDeprecated(volume_id=263834989, local_id=209573), dc_id=2), status=UserStatusRecently(), bot_info_version=None, restriction_reason=[], bot_inline_placeholder=None, lang_code='en'),
    133378542: User(id=133378542, is_self=True, contact=False, mutual_contact=False, deleted=False, bot=True, bot_chat_history=True, bot_nochats=False, verified=False, restricted=False, min=False, bot_inline_geo=False, support=False, scam=False, access_hash=8294665920163040443, first_name='Test Bot i do tests with', last_name=None, username='test4458bot', phone=None, photo=None, status=None, bot_info_version=13, restriction_reason=[], bot_inline_placeholder='This bot is for testing purposes.', lang_code=None),
    357231198: User(id=357231198, is_self=False, contact=False, mutual_contact=False, deleted=False, bot=False, bot_chat_history=False, bot_nochats=False, verified=False, restricted=False, min=False, bot_inline_geo=False, support=False, scam=False, access_hash=-6861545086171769827, first_name='Bonbotics', last_name=None, username='bonbotics', phone=None, photo=None, status=None, bot_info_version=None, restriction_reason=[], bot_inline_placeholder=None, lang_code='en'),
    -1001443587969: Channel(id=1443587969, title='Derp [test] rename', photo=ChatPhoto(photo_small=FileLocationToBeDeprecated(volume_id=226613135, local_id=158488), photo_big=FileLocationToBeDeprecated(volume_id=226613135, local_id=158490), dc_id=2), date=datetime.datetime(2019, 6, 16, 22, 38, 57, tzinfo=datetime.timezone.utc), version=0, creator=False, left=False, broadcast=False, verified=False, megagroup=True, restricted=False, signatures=False, min=False, scam=False, has_link=False, has_geo=False, slowmode_enabled=False, access_hash=-7101147752375680853, username=None, restriction_reason=[], admin_rights=None, banned_rights=None, default_banned_rights=ChatBannedRights(until_date=datetime.datetime(2038, 1, 19, 3, 14, 7, tzinfo=datetime.timezone.utc), view_messages=False, send_messages=False, send_media=False, send_stickers=False, send_gifs=False, send_games=False, send_inline=False, embed_links=False, send_polls=False, change_info=False, invite_users=False, pin_messages=False), participants_count=None),
    -1001391635462: Channel(id=1391635462, title='〠 R2Test 〠', photo=ChatPhotoEmpty(), date=datetime.datetime(2019, 4, 4, 8, 47, 30, tzinfo=datetime.timezone.utc), version=0, creator=False, left=True, broadcast=True, verified=False, megagroup=False, restricted=False, signatures=False, min=False, scam=False, has_link=False, has_geo=False, slowmode_enabled=False, access_hash=-3128376223792150891, username='R2Test', restriction_reason=[], admin_rights=None, banned_rights=None, default_banned_rights=None, participants_count=None),
    -1001127537892: Channel(id=1127537892, title='Programmer Humor', photo=ChatPhoto(photo_small=FileLocationToBeDeprecated(volume_id=226613135, local_id=158488), photo_big=FileLocationToBeDeprecated(volume_id=226613135, local_id=158490), dc_id=2), date=datetime.datetime(2019, 6, 16, 22, 38, 57, tzinfo=datetime.timezone.utc), version=0, creator=False, left=False, broadcast=False, verified=False, megagroup=False, restricted=False, signatures=False, min=False, scam=False, has_link=False, has_geo=False, slowmode_enabled=False, access_hash=-7101147752375680853, username='programmer_humor', restriction_reason=[], admin_rights=None, banned_rights=None, default_banned_rights=ChatBannedRights(until_date=datetime.datetime(2038, 1, 19, 3, 14, 7, tzinfo=datetime.timezone.utc), view_messages=False, send_messages=False, send_media=False, send_stickers=False, send_gifs=False, send_games=False, send_inline=False, embed_links=False, send_polls=False, change_info=False, invite_users=False, pin_messages=False), participants_count=None),
    -1001032895287: Channel(id=1032895287, title='Test Supergroup [test] #PUBLIC', photo=ChatPhoto(photo_small=FileLocationToBeDeprecated(volume_id=250821814, local_id=86989), photo_big=FileLocationToBeDeprecated(volume_id=250821814, local_id=86991), dc_id=2), date=datetime.datetime(2016, 11, 20, 16, 54, 19, tzinfo=datetime.timezone.utc), version=0, creator=False, left=False, broadcast=False, verified=False, megagroup=True, restricted=False, signatures=False, min=False, scam=False, has_link=False, has_geo=False, slowmode_enabled=False, access_hash=-6678057645738742952, username=None, restriction_reason=[], admin_rights=ChatAdminRights(change_info=True, post_messages=False, edit_messages=False, delete_messages=True, ban_users=True, invite_users=True, pin_messages=True, add_admins=True), banned_rights=None, default_banned_rights=ChatBannedRights(until_date=datetime.datetime(2038, 1, 19, 3, 14, 7, tzinfo=datetime.timezone.utc), view_messages=False, send_messages=False, send_media=False, send_stickers=False, send_gifs=False, send_games=False, send_inline=False, embed_links=False, send_polls=False, change_info=True, invite_users=False, pin_messages=True), participants_count=None)
}

CACHED_MESSAGES: Dict[str, Message] = {
    "-1001032895287#3543": Message(id=3541, to_id=PeerChannel(channel_id=1032895287), date=datetime.datetime(2019, 12, 8, 21, 12, 19, tzinfo=datetime.timezone.utc), message='REPLY TEST 6', out=False, mentioned=False, media_unread=False, silent=False, post=False, from_scheduled=False, legacy=False, edit_hide=False, from_id=10717954, fwd_from=None, via_bot_id=None, reply_to_msg_id=3537, media=None, reply_markup=None, entities=[], views=None, edit_date=None, post_author=None, grouped_id=None, restriction_reason=[])
}


class FakeClient(object):
    def __init__(self, peers: Dict[int, TypePeer], messages: Dict[str, Message], update_id: int):
        self.lookups = peers
        self.messages = messages
        self.update_id = update_id
    # end if

    async def get_entity(self, peer_id):
        return self.lookups[peer_id]
    # end def

    def get_reply_message(self, o: Message):
        return self.messages[f'{o.chat_id}#{o.id}']
    # end def

    @property
    def user_id(self):
        return 4458
    # end def
# end clas


class MyTestCase(asynctest.TestCase):
    array_compare = DictDiffer.unittest_compare()

    async def test_supergroup_add_other_user(self):
        event = UpdateNewChannelMessage(
            message=MessageService(
                id=3496,
                to_id=PeerChannel(
                    channel_id=1032895287
                ),
                date=datetime.datetime(2019, 12, 7, 18, 22, 54, tzinfo=datetime.timezone.utc),
                action=MessageActionChatAddUser(users=[357231198]),
                out=False, mentioned=False, media_unread=False, silent=False, post=False, legacy=False,
                from_id=10717954, reply_to_msg_id=None
            ),
            pts=4320, pts_count=1
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
                "message_id": 3496,
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
                        "language_code": "en",  # Manually added to the unittest. Should we maybe not include that?
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
            "update_id": 44581337
        }

        client = FakeClient(peers=RECYCLE_PEERS, messages=None, update_id=44581337)
        result = await to_web_api(event, client)
        result = result.to_array()

        self.assertEqual(
            json.dumps(expected, indent=2, sort_keys=True),
            json.dumps(result,   indent=2, sort_keys=True),
            'generated vs real one'
        )
    # end def

    async def test_channel_rename(self):
        event = UpdateNewChannelMessage(
            message=MessageService(
                id=168,
                to_id=PeerChannel(
                    channel_id=1443587969
                ),
                date=datetime.datetime(2019, 12, 7, 23, 31, tzinfo=datetime.timezone.utc),
                action=MessageActionChatEditTitle(title='Derp [test]'),
                out=False, mentioned=False, media_unread=False, silent=False, post=False, legacy=False,
                from_id=10717954, reply_to_msg_id=None
            ),
            pts=171, pts_count=1
        )

        expected = {
            "message": {
                "chat": {
                    "id": -1001443587969,
                    "title": "Derp [test] rename",
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
            "update_id": 4458007
        }

        client = FakeClient(peers=RECYCLE_PEERS, messages=None, update_id=4458007)
        result = await to_web_api(event, client)
        result = result.to_array()

        self.array_compare(expected, result)
    # end def

    async def test_channel_message(self):
        event = UpdateNewChannelMessage(
            message=Message(
                id=184,
                to_id=PeerChannel(
                    channel_id=1443587969
                ),
                date=datetime.datetime(2019, 12, 8, 1, 22, 38, tzinfo=datetime.timezone.utc),
                message='🧑\u200d💻', out=False, mentioned=False, media_unread=False, silent=False, post=False,
                from_scheduled=False, legacy=False, edit_hide=False, from_id=10717954, fwd_from=None, via_bot_id=None,
                reply_to_msg_id=None, media=None, reply_markup=None, entities=[], views=None, edit_date=None,
                post_author=None, grouped_id=None, restriction_reason=[]
            ),
            pts=187, pts_count=1
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
            "update_id": 4204458
        }

        client = FakeClient(peers=RECYCLE_PEERS, messages=None, update_id=4204458)
        result = await to_web_api(event, client)
        result = result.to_array()

        self.array_compare(expected, result)
    # end def

    async def test_channel_message_2(self):
        event = UpdateNewChannelMessage(
            message=Message(
                id=20101,
                to_id=PeerChannel(channel_id=1127537892),
                date=datetime.datetime(2019, 12, 8, 12, 26, 9, tzinfo=datetime.timezone.utc),
                message='No-nonsense sorting algorithm\nhttps://redd.it/e7sjqu\n\nby @programmer_humor',
                out=False, mentioned=False, media_unread=False, silent=False, post=True, from_scheduled=False,
                legacy=False, edit_hide=False, from_id=None, fwd_from=None, via_bot_id=None, reply_to_msg_id=None,
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
                views=1, edit_date=None, post_author=None, grouped_id=None, restriction_reason=[]
            ),
            pts=20134, pts_count=1
        )

        expected = {
            "message": "see test_channel_message_2_forwareded, just witout the forward.",
            "update_id": 4458007
        }

        client = FakeClient(peers=RECYCLE_PEERS, messages=None, update_id=4458007)
        result = await to_web_api(event, client)
        result = result.to_array()

        self.array_compare(expected, result)
    # end def

    async def test_channel_message_2_forward_from_channel(self):
        """
        Same as test_channel_message_2, but forwarded to another channel.
        :return:
        """
        event = UpdateNewChannelMessage(
            message=Message(
                id=197,
                to_id=PeerChannel(channel_id=1443587969),
                date=datetime.datetime(2019, 12, 8, 12, 33, 53, tzinfo=datetime.timezone.utc),
                message='No-nonsense sorting algorithm\nhttps://redd.it/e7sjqu\n\nby @programmer_humor',
                out=False, mentioned=False, media_unread=False, silent=False, post=False, from_scheduled=False,
                legacy=False, edit_hide=False, from_id=10717954,
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
                via_bot_id=None,  reply_to_msg_id=None,
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
                        dc_id=2, has_stickers=False
                    ),
                    ttl_seconds=None
                ),
                reply_markup=None,
                entities=[
                    MessageEntityUrl(offset=30, length=22),
                    MessageEntityMention(offset=57, length=17)
                ],
                views=366, edit_date=None, post_author=None, grouped_id=None, restriction_reason=[]
            ),
            pts=200, pts_count=1
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

        client = FakeClient(peers=RECYCLE_PEERS, messages=None, update_id=445804458)
        result = await to_web_api(event, client)
        result = result.to_array()

        # for i, result_photo in enumerate(expected["message"]["photo"]):
        #     expected_photo = result["message"]["photo"][i]
        #     self.assertEquals(len(expected_photo['file_id']), len(result_photo['file_id']), "length should be same")
        #     # now delete the file id's as we don't like that to butcher up the comparision
        #     del result_photo['file_id']
        #     del expected_photo['file_id']
        # # end if

        self.array_compare(expected, result)
    # end def

    async def test_channel_forward_from_user(self):
        client = FakeClient(peers=RECYCLE_PEERS, messages=None, update_id=445804458)
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

        result = await to_web_api(event, client)
        result = result.to_array()

        # for i, result_photo in enumerate(expected["message"]["photo"]):
        #     expected_photo = result["message"]["photo"][i]
        #     self.assertEquals(len(expected_photo['file_id']), len(result_photo['file_id']), "length should be same")
        #     # now delete the file id's as we don't like that to butcher up the comparision
        #     del result_photo['file_id']
        #     del expected_photo['file_id']
        # # end if

        self.array_compare(expected, result)
    # end def

    async def test_channel_forward_video_from_channel_with_signature(self):
        event = UpdateNewChannelMessage(
            message=Message(
                id=211,
                to_id=PeerChannel(channel_id=1443587969),
                date=datetime.datetime(2019, 12, 8, 16, 18, 50, tzinfo=datetime.timezone.utc),
                message="I'm so confused\nhttps://redd.it/cwhfln\nby @R2Test",
                out=False, mentioned=False, media_unread=False, silent=False, post=False, from_scheduled=False,
                legacy=False, edit_hide=False, from_id=10717954,
                fwd_from=MessageFwdHeader(
                    date=datetime.datetime(2019, 8, 28, 12, 36, 2, tzinfo=datetime.timezone.utc),
                    from_id=None,
                    from_name=None,
                    channel_id=1391635462,
                    channel_post=36351,
                    post_author='r2tBot',
                    saved_from_peer=None,
                    saved_from_msg_id=None
                ),
                via_bot_id=None, reply_to_msg_id=None,
                media=MessageMediaDocument(
                    document=Document(
                        id=5995755528964276486,
                        access_hash=-8945241733828268115,
                        file_reference=b'\x02V\x0bg\x81\x00\x00\x00\xd3]\xed"j2\xc2E\xeeq\x8a\xc2\x15\xab\x95\xce\x06\xb7\xde\xb2\x9d',
                        date=datetime.datetime(2019, 8, 28, 5, 27, 20, tzinfo=datetime.timezone.utc),
                        mime_type='video/mp4',
                        size=7611122,
                        dc_id=4,
                        attributes=[
                            DocumentAttributeVideo(duration=43, w=684, h=854, round_message=False, supports_streaming=True),
                            DocumentAttributeFilename(file_name='R7TYwBo.mp4')
                        ],
                        thumbs=[
                            PhotoStrippedSize(type='i', bytes=b'\x01( \xb0\x8c\x92\x0c\xa9\xa8D\xf9\xb9\xf2\xc0\x04z\xd3\x8c\xab\x12\x90\xeac\xee\x00\xfeT\xcbT\x0b!,y\xdbJ\xe3"\x95\xc4wa\xa4\xfb\xac\xb8\xcf\xa5]\x8c\x87\x1dA\xf7\xaa\xf7\x91\xa3\xae\t\xc1\xedT\x91\xa5\xb7<\x0c\x8ac\xb5\xcbW$2\xb4\x8f\xeb\xc5C\x103\r\xcc\xe4(5$\xa3zl\xf5\xa9 \x84"`\xf3R\x90\xd9\x1d\xd3\xc8\xc0\x02\xa1q\xc8\xc1\xa4\x86Uq\x83\xc3T\xcd\x02\xec#\x9e{\xf7\xaa\xac\x86\x17\xe3\x90{\xd0\xd0E\x96\xe2\x8b\xbbu\xa9x\x14QT\x89b\x13QJ\xa1\x874QL\x0f'),
                            PhotoSize(type='m', location=FileLocationToBeDeprecated(volume_id=463406930, local_id=7134), w=256, h=320, size=13003)
                        ]
                    ),
                    ttl_seconds=None),
                reply_markup=None,
                entities=[
                    MessageEntityBold(offset=0, length=15),
                    MessageEntityUrl(offset=16, length=22),
                    MessageEntityMention(offset=42, length=7)
                ], views=1,
                edit_date=None, post_author=None, grouped_id=None, restriction_reason=[]
            ),
            pts=215, pts_count=1
        )

        expected = {
            "message": {
                "caption": "I'm so confused\nhttps://redd.it/cwhfln\nby @R2Test",
                "caption_entities": [
                    {
                        "length": 15,
                        "offset": 0,
                        "type": "bold"
                    },
                    {
                        "length": 22,
                        "offset": 16,
                        "type": "url"
                    },
                    {
                        "length": 7,
                        "offset": 42,
                        "type": "mention"
                    }
                ],
                "chat": {
                    "id": -1001443587969,
                    "title": "Derp [test] rename",
                    "type": "supergroup"
                },
                "date": 1575821930,
                "forward_date": 1566995762,
                "forward_from_chat": {
                    "id": -1001391635462,
                    "title": "〠 R2Test 〠",
                    "type": "channel",
                    "username": "R2Test"
                },
                "forward_from_message_id": 36351,
                "forward_signature": "r2tBot",
                "from": {
                    "first_name": "luckydonald",
                    "id": 10717954,
                    "is_bot": false,
                    "language_code": "en",
                    "username": "luckydonald"
                },
                "message_id": 211,
                "video": {
                    "duration": 43,
                    "file_id": "BAADBAADBgEAAuMzNVPsG0GS6vWgChYE",
                    "file_size": 7611122,
                    "height": 854,
                    "mime_type": "video/mp4",
                    "thumb": {
                        "file_id": "AAQEAAMGAQAC4zM1U-wbQZLq9aAKUgefGwAEAQAHbQAD3hsAAhYE",
                        "file_size": 13003,
                        "height": 320,
                        "width": 256
                    },
                    "width": 684
                }
            },
            "update_id": 13374458
        }

        client = FakeClient(peers=RECYCLE_PEERS, messages=None, update_id=13374458)
        result = await to_web_api(event, client)
        result = result.to_array()

        # for i, result_photo in enumerate(expected["message"]["photo"]):
        #     expected_photo = result["message"]["photo"][i]
        #     self.assertEquals(len(expected_photo['file_id']), len(result_photo['file_id']), "length should be same")
        #     # now delete the file id's as we don't like that to butcher up the comparision
        #     del result_photo['file_id']
        #     del expected_photo['file_id']
        # # end if

        self.array_compare(expected, result)
    # end def

    async def test_channel_post_with_signature(self):
        event = UpdateNewChannelMessage(
            message=Message(
                id=37840,
                to_id=PeerChannel(channel_id=1391635462),
                date=datetime.datetime(2019, 12, 8, 16, 44, 20, tzinfo=datetime.timezone.utc),
                message='test', out=False, mentioned=False, media_unread=False, silent=False, post=True,
                from_scheduled=False, legacy=False, edit_hide=False, from_id=None, fwd_from=None, via_bot_id=None,
                reply_to_msg_id=None, media=None, reply_markup=None, entities=[], views=1, edit_date=None,
                post_author='luckydonald', grouped_id=None, restriction_reason=[]
            ), pts=37885, pts_count=1
        )

        expected = {
            "channel_post": {
                "author_signature": "luckydonald",
                "chat": {
                    "id": -1001391635462,
                    "title": "〠 R2Test 〠",
                    "type": "channel",
                    "username": "R2Test"
                },
                "date": 1575823460,
                "message_id": 37840,
                "text": "test"
            },
            "update_id": 44581234
        }

        client = FakeClient(peers=RECYCLE_PEERS, messages=None, update_id=44581234)
        result = await to_web_api(event, client)
        result = result.to_array()

        # for i, result_photo in enumerate(expected["message"]["photo"]):
        #     expected_photo = result["message"]["photo"][i]
        #     self.assertEquals(len(expected_photo['file_id']), len(result_photo['file_id']), "length should be same")
        #     # now delete the file id's as we don't like that to butcher up the comparision
        #     del result_photo['file_id']
        #     del expected_photo['file_id']
        # # end if

        self.array_compare(expected, result)
    # end def

    async def test_reply_to_user_mention(self):
        msg = Message(
            id=3525,
            to_id=PeerChannel(channel_id=1032895287),
            date=datetime.datetime(2019, 12, 8, 19, 15, 6, tzinfo=datetime.timezone.utc),
            message='Woop.', out=False, mentioned=False, media_unread=False, silent=False, post=False,
            from_scheduled=False, legacy=False, edit_hide=False, from_id=10717954, fwd_from=None, via_bot_id=None,
            reply_to_msg_id=3516, media=None, reply_markup=None, entities=[], views=None, edit_date=None,
            post_author=None, grouped_id=None, restriction_reason=[],
        )
        event = UpdateNewChannelMessage(
            message=msg,
            pts=4351, pts_count=1
        )
        expected = {
            "message": {
                "chat": {
                    "id": -1001032895287,
                    "title": "Test Supergroup [test] #PUBLIC",
                    "type": "supergroup"
                },
                "date": 1575832506,
                "from": {
                    "first_name": "luckydonald",
                    "id": 10717954,
                    "is_bot": false,
                    "language_code": "en",
                    "username": "luckydonald"
                },
                "message_id": 3525,
                "reply_to_message": {
                    "chat": {
                        "id": -1001032895287,
                        "title": "Test Supergroup [test] #PUBLIC",
                        "type": "supergroup"
                    },
                    "date": 1575746583,
                    "entities": [
                        {
                            "length": 9,
                            "offset": 0,
                            "type": "text_mention",
                            "user": {
                                "first_name": "Bonbotics",
                                "id": 357231198,
                                "is_bot": false,
                                "username": "bonbotics"
                            }
                        }
                    ],
                    "from": {
                        "first_name": "Captcha",
                        "id": 629864526,
                        "is_bot": true,
                        "username": "JoinCaptchaBot"
                    },
                    "message_id": 3516,
                    "text": "Bonbotics kicked."
                },
                "text": "Woop."
            },
            "update_id": 862109783
        }

        client = FakeClient(peers=RECYCLE_PEERS, messages=None, update_id=44581234)
        msg._client = client
        result = await to_web_api(event, client)
        result = result.to_array()

        # for i, result_photo in enumerate(expected["message"]["photo"]):
        #     expected_photo = result["message"]["photo"][i]
        #     self.assertEquals(len(expected_photo['file_id']), len(result_photo['file_id']), "length should be same")
        #     # now delete the file id's as we don't like that to butcher up the comparision
        #     del result_photo['file_id']
        #     del expected_photo['file_id']
        # # end if

        self.array_compare(expected, result)
    # end def

    async def test_reply_to_text(self):
        msg = Message(
            id=3543,
            to_id=PeerChannel(channel_id=1032895287),
            date=datetime.datetime(2019, 12, 8, 21, 13, 48, tzinfo=datetime.timezone.utc),
            message='REPLY TEST 7', out=False, mentioned=False, media_unread=False, silent=False, post=False,
            from_scheduled=False, legacy=False, edit_hide=False, from_id=10717954, fwd_from=None, via_bot_id=None,
            reply_to_msg_id=3541, media=None, reply_markup=None, entities=[], views=None, edit_date=None,
            post_author=None, grouped_id=None, restriction_reason=[]
        )
        event = UpdateNewChannelMessage(msg, pts=4369, pts_count=1)

        expected = {
            "message": {
                "chat": {
                    "id": -1001032895287,
                    "title": "Test Supergroup [test] #PUBLIC",
                    "type": "supergroup"
                },
                "date": 1575839628,
                "from": {
                    "first_name": "luckydonald",
                    "id": 10717954,
                    "is_bot": false,
                    "language_code": "en",
                    "username": "luckydonald"
                },
                "message_id": 3543,
                "reply_to_message": {
                    "chat": {
                        "id": -1001032895287,
                        "title": "Test Supergroup [test] #PUBLIC",
                        "type": "supergroup"
                    },
                    "date": 1575839539,
                    "from": {
                        "first_name": "luckydonald",
                        "id": 10717954,
                        "is_bot": false,
                        "language_code": "en",
                        "username": "luckydonald"
                    },
                    "message_id": 3541,
                    "text": "REPLY TEST 6"
                },
                "text": "REPLY TEST 7"
            },
            "update_id": 44581234
        }

        client = FakeClient(peers=RECYCLE_PEERS, messages=CACHED_MESSAGES, update_id=44581234)
        msg._client = client
        result = await to_web_api(event, client)
        result = result.to_array()

        # for i, result_photo in enumerate(expected["message"]["photo"]):
        #     expected_photo = result["message"]["photo"][i]
        #     self.assertEquals(len(expected_photo['file_id']), len(result_photo['file_id']), "length should be same")
        #     # now delete the file id's as we don't like that to butcher up the comparision
        #     del result_photo['file_id']
        #     del expected_photo['file_id']
        # # end if

        self.array_compare(expected, result)
    # end def

    async def test_4_6_anon_poll_update(self):
        # regular anon poll, when pressing the second option.
        o = UpdateMessagePoll(
            poll_id=5298678574432124931,
            results=PollResults(
                min=False,
                results=[
                    PollAnswerVoters(option=b'0', voters=0, chosen=False, correct=False),
                    PollAnswerVoters(option=b'1', voters=1, chosen=True, correct=False),
                    PollAnswerVoters(option=b'2', voters=0, chosen=False, correct=False)
                ],
                total_voters=1,
                recent_voters=[]
            ),
            poll=Poll(
                id=5298678574432124931,
                question='TITLE OF POLL',
                answers=[
                    PollAnswer(text='Option 1', option=b'0'),
                    PollAnswer(text='Second iption', option=b'1'),
                    PollAnswer(text="That's an typo, lol 😂", option=b'2')
                ],
                closed=False,
                public_voters=False,
                multiple_choice=False,
                quiz=False,
            )
        )

        expected = {
            "poll": {
                "allows_multiple_answers": False,
                "id": "5298678574432124931",
                "is_anonymous": True,
                "is_closed": False,
                "options": [
                    {
                        "text": "Option 1",
                        "voter_count": 0
                    },
                    {
                        "text": "Second iption",
                        "voter_count": 1
                    },
                    {
                        "text": "That's an typo, lol 😂",
                        "voter_count": 0
                    }
                ],
                "question": "TITLE OF POLL",
                "total_voter_count": 1,
                "type": "regular"
            },
            "update_id": 862110283
        }

        client = FakeClient(peers=RECYCLE_PEERS, messages=CACHED_MESSAGES, update_id=44581234)
        o._client = client
        o._client.update_id = 862110283
        result = await to_web_api(o, client)
        result = result.to_array()

        self.array_compare(expected, result)
    # end def

    async def test_4_6_nonanon_poll_creation(self):
        # regular non-anon poll, newly created.
        o = UpdateNewChannelMessage(
            message=Message(
                id=356,
                to_id=PeerChannel(channel_id=1443587969),
                date=datetime.datetime(2020, 1, 29, 14, 44, tzinfo=datetime.timezone.utc),
                message='',
                out=False, mentioned=False, media_unread=False, silent=False,
                post=False, from_scheduled=False, legacy=False, edit_hide=False,
                from_id=357231198, fwd_from=None, via_bot_id=None, reply_to_msg_id=None,
                media=MessageMediaPoll(
                    poll=Poll(
                    id=5301227547327987713,
                    question='@luckydonald',
                    answers=[
                        PollAnswer(text='Awesome', option=b'0'),
                        PollAnswer(text='Great', option=b'1')
                    ],
                    closed=False,
                    public_voters=True,
                    multiple_choice=False,
                    quiz=False
                ),
                results=PollResults(min=False, results=[], total_voters=0, recent_voters=[])),
                reply_markup=None,
                entities=[],
                views=None,
                edit_date=None,
                post_author=None,
                grouped_id=None,
                restriction_reason=[]
            ),
            pts=373, pts_count=1
        )

        expected = {
            "message": {
                "chat": {
                    "id": -1001443587969,
                    "title": "Derp [test] rename",
                    "type": "supergroup"
                },
                "date": 1580309040,
                "from": {
                    "first_name": "Bonbotics",
                    "id": 357231198,
                    "language_code": "en",
                    "is_bot": false,
                    "username": "bonbotics"
                },
                "message_id": 356,
                "poll": {
                    "allows_multiple_answers": false,
                    "id": "5301227547327987713",
                    "is_anonymous": false,
                    "is_closed": false,
                    "options": [
                        {
                            "text": "Awesome",
                            "voter_count": 0
                        },
                        {
                            "text": "Great",
                            "voter_count": 0
                        }
                    ],
                    "question": "@luckydonald",
                    "total_voter_count": 0,
                    "type": "regular"
                }
            },
            "update_id": 862110285
        }

        client = FakeClient(peers=RECYCLE_PEERS, messages=CACHED_MESSAGES, update_id=44581234)
        o._client = client
        o._client.update_id = 862110285
        result = await to_web_api(o, client)
        result = result.to_array()

        # for i, result_photo in enumerate(expected["message"]["photo"]):
        #     expected_photo = result["message"]["photo"][i]
        #     self.assertEquals(len(expected_photo['file_id']), len(result_photo['file_id']), "length should be same")
        #     # now delete the file id's as we don't like that to butcher up the comparision
        #     del result_photo['file_id']
        #     del expected_photo['file_id']
        # # end if

        self.array_compare(expected, result)
    # end def

    async def test_4_6_nonanon_quiz(self):
        # quiz non-anon poll, newly created.
        o = UpdateNewChannelMessage(
            message=Message(
                id=3573,
                to_id=PeerChannel(channel_id=1032895287),
                date=datetime.datetime(2020, 1, 31, 10, 58, 57, tzinfo=datetime.timezone.utc),
                message='',
                out=True,
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
                media=MessageMediaPoll(
                    poll=Poll(
                        id=5305467573402337281,
                        question='LOOK MOM A PUBLIC QUIZZZ',
                        answers=[
                            PollAnswer(text='QUIZZZzzzz', option=b'0'),
                            PollAnswer(text='QUI💤', option=b'1'),
                            PollAnswer(text='QUI😴', option=b'2')
                        ],
                        closed=False,
                        public_voters=True,
                        multiple_choice=False,
                        quiz=True
                    ),
                    results=PollResults(
                        min=False,
                        results=[],
                        total_voters=0,
                        recent_voters=[]
                    ),
                ),
                reply_markup=None,
                entities=[],
                views=None,
                edit_date=None,
                post_author=None,
                grouped_id=None,
                restriction_reason=[],
            ),
            pts=4402,
            pts_count=1,
        )

        expected = {
            "message": {
                "chat": {
                    "id": -1001032895287,
                    "title": "Test Supergroup [test] #PUBLIC",
                    "type": "supergroup"
                },
                "date": 1580468337,
                "from": {
                    "first_name": "luckydonald",
                    "id": 10717954,
                    "is_bot": false,
                    "language_code": "en",
                    "username": "luckydonald"
                },
                "message_id": 3573,
                "poll": {
                    "allows_multiple_answers": false,
                    "correct_option_id": 1,
                    "id": "5305467573402337281",
                    "is_anonymous": false,
                    "is_closed": false,
                    "options": [
                        {
                            "text": "QUIZZZzzzz",
                            "voter_count": 0
                        },
                        {
                            "text": "QUI💤",
                            "voter_count": 0
                        },
                        {
                            "text": "QUI😴",
                            "voter_count": 0
                        }
                    ],
                    "question": "LOOK MOM A PUBLIC QUIZZZ",
                    "total_voter_count": 0,
                    "type": "quiz"
                }
            },
            "update_id": 12340069
        }

        client = FakeClient(peers=RECYCLE_PEERS, messages=CACHED_MESSAGES, update_id=12340069)
        o._client = client
        o._client.update_id = 862110285
        result = await to_web_api(o, client)
        result = result.to_array()

        self.array_compare(expected, result, volatile_fields=['update_id'])
    # end def

    async def test_4_6_nonanon_poll_creation(self):
        # regular non-anon poll, newly created.
        o = UpdateNewChannelMessage(
            message=Message(
                id=356,
                to_id=PeerChannel(channel_id=1443587969),
                date=datetime.datetime(2020, 1, 29, 14, 44, tzinfo=datetime.timezone.utc),
                message='',
                out=False, mentioned=False, media_unread=False, silent=False,
                post=False, from_scheduled=False, legacy=False, edit_hide=False,
                from_id=357231198, fwd_from=None, via_bot_id=None, reply_to_msg_id=None,
                media=MessageMediaPoll(
                    poll=Poll(
                    id=5301227547327987713,
                    question='@luckydonald',
                    answers=[
                        PollAnswer(text='Awesome', option=b'0'),
                        PollAnswer(text='Great', option=b'1')
                    ],
                    closed=False,
                    public_voters=True,
                    multiple_choice=False,
                    quiz=False
                ),
                results=PollResults(min=False, results=[], total_voters=0, recent_voters=[])),
                reply_markup=None,
                entities=[],
                views=None,
                edit_date=None,
                post_author=None,
                grouped_id=None,
                restriction_reason=[]
            ),
            pts=373, pts_count=1
        )

        expected = {
            "message": {
                "chat": {
                    "id": -1001443587969,
                    "title": "Derp [test] rename",
                    "type": "supergroup"
                },
                "date": 1580309040,
                "from": {
                    "first_name": "Bonbotics",
                    "id": 357231198,
                    "language_code": "en",
                    "is_bot": false,
                    "username": "bonbotics"
                },
                "message_id": 356,
                "poll": {
                    "allows_multiple_answers": false,
                    "id": "5301227547327987713",
                    "is_anonymous": false,
                    "is_closed": false,
                    "options": [
                        {
                            "text": "Awesome",
                            "voter_count": 0
                        },
                        {
                            "text": "Great",
                            "voter_count": 0
                        }
                    ],
                    "question": "@luckydonald",
                    "total_voter_count": 0,
                    "type": "regular"
                }
            },
            "update_id": 862110285
        }

        client = FakeClient(peers=RECYCLE_PEERS, messages=CACHED_MESSAGES, update_id=862110285)
        o._client = client
        result = await to_web_api(o, client)
        result = result.to_array()

        # for i, result_photo in enumerate(expected["message"]["photo"]):
        #     expected_photo = result["message"]["photo"][i]
        #     self.assertEquals(len(expected_photo['file_id']), len(result_photo['file_id']), "length should be same")
        #     # now delete the file id's as we don't like that to butcher up the comparision
        #     del result_photo['file_id']
        #     del expected_photo['file_id']
        # # end if

        self.array_compare(expected, result, volatile_fields=['update_id', 'message.poll.correct_option_id'])
    # end def

    async def test_4_6_(self):
        self.skipTest(None)
        # quiz non-anon poll, newly created.
        o = None

        expected = None

        client = FakeClient(peers=RECYCLE_PEERS, messages=CACHED_MESSAGES, update_id=12340069)
        o._client = client
        o._client.update_id = 862110285
        result = await to_web_api(o, client)
        result = result.to_array()

        await self.array_compare(expected, result)
    # end def

    async def array_compare(
        self,
        expected: Dict[str, Any],
        result: Dict[str, Any],
        msg: Optional[str] = 'real one vs generated one',
        volatile_fields: Optional[List[str]] = None,
        optional_fields: Optional[List[str]] = None,
        additional_fields: Optional[List[str]] = None,
        print_correct: bool = True,
    ):
        return DictDiffer.unittest_compare(
            expected, result, msg, volatile_fields, optional_fields, additional_fields, print_correct
        )
# end class
