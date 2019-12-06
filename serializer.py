#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from builtins import object
from datetime import datetime

from luckydonaldUtils.logger import logging
from pytgbot.api_types.receivable.media import ChatPhoto, UserProfilePhotos, PhotoSize, MessageEntity
from pytgbot.api_types.receivable.peer import User, Chat
from pytgbot.api_types.receivable.updates import Message
from telethon.tl.types import User as TUser
from telethon.tl.types import Message as TMessage
from telethon.tl.types import UserProfilePhoto as TUserProfilePhoto
from telethon.tl.types import MessageEntityBlockquote as TMessageEntityBlockquote
from telethon.tl.types import MessageEntityBold as TMessageEntityBold
from telethon.tl.types import MessageEntityBotCommand as TMessageEntityBotCommand
from telethon.tl.types import MessageEntityCashtag as TMessageEntityCashtag
from telethon.tl.types import MessageEntityCode as TMessageEntityCode
from telethon.tl.types import MessageEntityEmail as TMessageEntityEmail
from telethon.tl.types import MessageEntityHashtag as TMessageEntityHashtag
from telethon.tl.types import MessageEntityItalic as TMessageEntityItalic
from telethon.tl.types import MessageEntityMention as TMessageEntityMention
from telethon.tl.types import MessageEntityMentionName as TMessageEntityMentionName
from telethon.tl.types import MessageEntityPhone as TMessageEntityPhone
from telethon.tl.types import MessageEntityPre as TMessageEntityPre
from telethon.tl.types import MessageEntityStrike as TMessageEntityStrike
from telethon.tl.types import MessageEntityTextUrl as TMessageEntityTextUrl
from telethon.tl.types import MessageEntityUnderline as TMessageEntityUnderline
from telethon.tl.types import MessageEntityUnknown as TMessageEntityUnknown
from telethon.tl.types import MessageEntityUrl as TMessageEntityUrl
from telethon.utils import pack_bot_file_id

__author__ = 'luckydonald'

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if


def load_user(id: int) -> User:
    # TODO.
    return User(
        id=id,
        is_bot=False,
        first_name=f"user#{id}",
        # last_name=None,
        # username=None,
        # language_code=None,
    )
# end def


def load_message(id: int) -> Message:
    # TODO.
    return Message(
        message_id=id,
        date=0,
        chat=Chat(0, 'private'),
    )
# end def


def to_web_api(object, as_chat=False):
    if isinstance(object, TUser):
        if as_chat:
            return Chat(
                id=object.id,
                type='private',
                # title=None,
                first_name=object.first_name,
                last_name=object.last_name,
                username=object.username,
                # TODO: all_members_are_administrators=,
                photo=to_web_api(object.photo),
                # description=None,
                # invite_link=None,
                # pinned_message=None,
                # sticker_set_name=None,
                # can_set_sticker_set=None,
            )
        return User(
            id=object.id,
            is_bot=object.bot,
            first_name=object.first_name,
            last_name=object.last_name,
            username=object.username,
            language_code=object.lang_code,
        )
    # end if
    if isinstance(object, TUserProfilePhoto):
        if as_chat:
            return ChatPhoto(
                small_file_id=to_web_api(object.photo_small),
                big_file_id=to_web_api(object.photo_big),
            )
        return UserProfilePhotos(
            total_count=2,
            photos=[
                PhotoSize(
                    file_id=pack_bot_file_id(object.photo_big),
                    width=0,  # TODO somehow look up more data.
                    height=0  # TODO somehow look up more data.
                ),
                PhotoSize(
                    file_id=pack_bot_file_id(object.photo_small),
                    width=0,  # TODO somehow look up more data.
                    height=0  # TODO somehow look up more data.
                ),
            ],
        )
    if isinstance(object, TMessage):
        return Message(
            message_id=object.id,
            date=to_web_api(object.date),
            chat=to_web_api(object.chat, as_chat=True),
            from_peer=to_web_api(object.sender),
            # forward_from=to_web_api(object.fwd_from.), # TODO: look up by id
            # forward_from_chat=to_web_api(object.fwd_from.from_id), # TODO: look up by id
            # TODO: forward_signature=,
            forward_date=to_web_api(object.fwd_from.date) if object.fwd_from else None,
            # TODO: reply_to_message=to_web_api(object.reply_to_msg_id)  # TODO: load
            edit_date=to_web_api(object.edit_date),
            # TODO: media_group_id=,
            author_signature=object.fwd_from.post_author if object.fwd_from else None,
            text=object.text,
            entities=to_web_api(object.entities),
        )
    if isinstance(object, TMessageEntityBlockquote):
        return MessageEntity(
            type='blockquote',  # Todo
            offset=object.offset,
            length=object.length,
        )
    if isinstance(object, TMessageEntityBold):
        return MessageEntity(
            type='bold',
            offset=object.offset,
            length=object.length,
        )
    if isinstance(object, TMessageEntityBotCommand):
        return MessageEntity(
            type='bot_command',
            offset=object.offset,
            length=object.length,
        )
    if isinstance(object, TMessageEntityCashtag):
        return MessageEntity(
            type='cashtag',
            offset=object.offset,
            length=object.length,
        )
    if isinstance(object, TMessageEntityCode):
        return MessageEntity(
            type='code',
            offset=object.offset,
            length=object.length,
        )
    if isinstance(object, TMessageEntityEmail):
        return MessageEntity(
            type='email',
            offset=object.offset,
            length=object.length,
        )
    if isinstance(object, TMessageEntityHashtag):
        return MessageEntity(
            type='hashtag',
            offset=object.offset,
            length=object.length,
        )
    if isinstance(object, TMessageEntityItalic):
        return MessageEntity(
            type='italic',
            offset=object.offset,
            length=object.length,
        )
    if isinstance(object, TMessageEntityMention):  # @username
        return MessageEntity(
            type='mention',
            offset=object.offset,
            length=object.length,
        )
    if isinstance(object, TMessageEntityMentionName):
        return MessageEntity(
            type='text_mention',
            offset=object.offset,
            length=object.length,
            user=load_user(id=object.user_id),  # TODO: load user
        )
    if isinstance(object, TMessageEntityPhone):
        return MessageEntity(
            type='phone_number',
            offset=object.offset,
            length=object.length,
        )
    if isinstance(object, TMessageEntityPre):
        return MessageEntity(
            type='pre',
            offset=object.offset,
            length=object.length,
        )
    if isinstance(object, TMessageEntityStrike):
        return MessageEntity(
            type='strikethrough',  # Todo
            offset=object.offset,
            length=object.length,
        )
    if isinstance(object, TMessageEntityTextUrl):
        return MessageEntity(
            type='text_link',
            offset=object.offset,
            length=object.length,
            url=object.url,
        )
    if isinstance(object, TMessageEntityUnderline):
        return MessageEntity(
            type='underline',  # Todo
            offset=object.offset,
            length=object.length,
        )
    if isinstance(object, TMessageEntityUnknown):
        return MessageEntity(
            type='unknown',
            offset=object.offset,
            length=object.length,
        )
    if isinstance(object, TMessageEntityUrl):
        return MessageEntity(
            type='url',
            offset=object.offset,
            length=object.length,
        )
    if isinstance(object, datetime):
        return int(object.timestamp())
    if isinstance(object, tuple):
        return tuple(to_web_api(list(object)))
    if isinstance(object, list):
        return [to_web_api(x) for x in object]
    if isinstance(object, dict):
        return {k: to_web_api(v) for k, v in object.items()}
    if isinstance(object, (bool, str, int, float)):
        return object
    if object is None:
        return None
    raise TypeError(f'Type not handled: {type(object)} with value {object!r}')
# end def
