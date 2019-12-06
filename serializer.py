#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from builtins import object
from datetime import datetime

from luckydonaldUtils.logger import logging
from pytgbot.api_types.receivable.inline import InlineQuery
from pytgbot.api_types.receivable.media import ChatPhoto, UserProfilePhotos, PhotoSize, MessageEntity, Location
from pytgbot.api_types.receivable.payments import ShippingQuery, PreCheckoutQuery, OrderInfo
from pytgbot.api_types.receivable.peer import User, Chat
from pytgbot.api_types.receivable.updates import Message, Update, CallbackQuery
from telethon.tl.custom import Forward
from telethon.tl.types import User as TUser
from telethon.tl.patched import Message as TMessage
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
from telethon.tl.types import UpdateNewMessage as TUpdateNewMessage
from telethon.tl.types import UpdateEditMessage as TUpdateEditMessage
from telethon.tl.types import UpdateEditChannelMessage as TUpdateEditChannelMessage
from telethon.tl.types import UpdateBotInlineQuery as TUpdateBotInlineQuery
from telethon.tl.types import UpdateBotCallbackQuery as TUpdateBotCallbackQuery
from telethon.tl.types import UpdateBotShippingQuery as TUpdateBotShippingQuery
from telethon.tl.types import UpdateBotPrecheckoutQuery as TUpdateBotPrecheckoutQuery
from telethon.tl.types import GeoPointEmpty as TGeoPointEmpty
from telethon.tl.types import GeoPoint as TGeoPoint
from telethon.tl.types import PaymentRequestedInfo as TPaymentRequestedInfo
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


def load_message(msg_id: int, chat_id: int) -> Message:
    # TODO.
    return Message(
        message_id=msg_id,
        date=0,
        chat=Chat(chat_id, 'private'),
    )
# end def


def to_web_api(o, user_as_chat=False, prefer_update=True, load_photos=False):
    if isinstance(o, TUpdateNewMessage):
        return Update(
            update_id=o.pts,
            message=to_web_api(o.message),
        )
    if isinstance(o, TUpdateEditMessage):
        return Update(
            update_id=o.pts,
            edited_message=to_web_api(o.message),
        )
    if isinstance(o, TUpdateEditChannelMessage):
        return Update(
            update_id=o.pts,
            edited_channel_post=to_web_api(o.message),
        )
    if isinstance(o, TUpdateBotInlineQuery):
        if prefer_update:
            return Update(
                update_id=o.query_id,
                inline_query=to_web_api(o, prefer_update=False)
            )
        return InlineQuery(
            id=o.query_id,
            from_peer=load_user(o.user_id),
            query=o.query,
            offset=o.offset,
            location=to_web_api(o.geo),
        )
    # if isinstance(object, ???):
    #     return Update(
    #         update_id=object.pts,
    #         chosen_inline_result=to_web_api(object.message),  # TODO
    #     )
    if isinstance(o, TUpdateBotCallbackQuery):
        if prefer_update:
            return Update(
                update_id=0,
                callback_query=to_web_api(o, prefer_update=False),
            )
        # end if
        return CallbackQuery(
            id=o.query_id,
            from_peer=to_web_api(o.peer),
            chat_instance=str(o.chat_instance),
            message=load_message(o.msg_id, o.chat_instance),
            # inline_message_id=object TODO
            data=o.data,
            game_short_name=o.game_short_name,
        )
    if isinstance(o, TUpdateBotShippingQuery):
        if prefer_update:
            return Update(
                update_id=0,
                shipping_query=to_web_api(o, prefer_update=False),
            )
        return ShippingQuery(
            id=o.query_id,
            from_peer=load_user(o.user_id),
            invoice_payload=o.payload,
            shipping_address=o.shipping_address,
        )
    if isinstance(o, TUpdateBotPrecheckoutQuery):
        if prefer_update:
            return Update(
                update_id=0,
                pre_checkout_query=to_web_api(o, prefer_update=False),
            )
        return PreCheckoutQuery(
            id=o.query_id,
            from_peer=load_user(o.user_id),
            currency=o.currency,
            total_amount=o.total_amount,
            invoice_payload=o.payload,
            shipping_option_id=o.shipping_option_id,
            order_info=to_web_api(o.info),
        )
    if isinstance(o, TGeoPointEmpty):
        return None
    if isinstance(o, TGeoPoint):
        return Location(
            longitude=o.long,
            latitude=o.lat,
        )
    if isinstance(o, TPaymentRequestedInfo):
        return OrderInfo(
            name=o.name,
            phone_number=o.phone,
            email=o.email,
            shipping_address=o.shipping_address,
        )
    if isinstance(o, TUser):
        if user_as_chat:
            return Chat(
                id=o.id,
                type='private',
                # title=None,
                first_name=o.first_name,
                last_name=o.last_name,
                username=o.username,
                # TODO: all_members_are_administrators=,
                photo=to_web_api(o.photo) if load_photos else None,
                # description=None,
                # invite_link=None,
                # pinned_message=None,
                # sticker_set_name=None,
                # can_set_sticker_set=None,
            )
        return User(
            id=o.id,
            is_bot=o.bot,
            first_name=o.first_name,
            last_name=o.last_name,
            username=o.username,
            language_code=o.lang_code,
        )
    # end if
    if isinstance(o, TUserProfilePhoto):
        if user_as_chat:
            return ChatPhoto(
                small_file_id=to_web_api(o.photo_small),
                big_file_id=to_web_api(o.photo_big),
            )
        return UserProfilePhotos(
            total_count=2,
            photos=[
                PhotoSize(
                    file_id=pack_bot_file_id(o.photo_big),
                    width=0,  # TODO somehow look up more data.
                    height=0  # TODO somehow look up more data.
                ),
                PhotoSize(
                    file_id=pack_bot_file_id(o.photo_small),
                    width=0,  # TODO somehow look up more data.
                    height=0  # TODO somehow look up more data.
                ),
            ],
        )
    if isinstance(o, TMessage):
        reply = None
        if o.is_reply:
            reply = await o.get_reply_message()
        # end if
        forward: Forward = o.forward
        forward_from = None
        forward_from_chat = None
        if o.forward:
            forward_from = forward.get_sender()
            forward_from_chat = o.forward.get_chat()
        # end if
        return Message(
            message_id=o.id,
            date=to_web_api(o.date),
            chat=to_web_api(o.chat, user_as_chat=True),
            from_peer=to_web_api(o.sender),
            forward_from=to_web_api(forward_from),
            forward_from_chat=to_web_api(forward_from_chat),
            # TODO: forward_signature=,
            forward_date=to_web_api(o.forward.date) if o.fwd_from else None,
            reply_to_message=to_web_api(reply),
            edit_date=to_web_api(o.edit_date),
            # TODO: media_group_id=,
            author_signature=o.fwd_from.post_author if o.fwd_from else None,
            text=o.text,
            entities=to_web_api(o.entities),
        )
    if isinstance(o, TMessageEntityBlockquote):
        return MessageEntity(
            type='blockquote',  # Todo
            offset=o.offset,
            length=o.length,
        )
    if isinstance(o, TMessageEntityBold):
        return MessageEntity(
            type='bold',
            offset=o.offset,
            length=o.length,
        )
    if isinstance(o, TMessageEntityBotCommand):
        return MessageEntity(
            type='bot_command',
            offset=o.offset,
            length=o.length,
        )
    if isinstance(o, TMessageEntityCashtag):
        return MessageEntity(
            type='cashtag',
            offset=o.offset,
            length=o.length,
        )
    if isinstance(o, TMessageEntityCode):
        return MessageEntity(
            type='code',
            offset=o.offset,
            length=o.length,
        )
    if isinstance(o, TMessageEntityEmail):
        return MessageEntity(
            type='email',
            offset=o.offset,
            length=o.length,
        )
    if isinstance(o, TMessageEntityHashtag):
        return MessageEntity(
            type='hashtag',
            offset=o.offset,
            length=o.length,
        )
    if isinstance(o, TMessageEntityItalic):
        return MessageEntity(
            type='italic',
            offset=o.offset,
            length=o.length,
        )
    if isinstance(o, TMessageEntityMention):  # @username
        return MessageEntity(
            type='mention',
            offset=o.offset,
            length=o.length,
        )
    if isinstance(o, TMessageEntityMentionName):
        return MessageEntity(
            type='text_mention',
            offset=o.offset,
            length=o.length,
            user=load_user(id=o.user_id),  # TODO: load user
        )
    if isinstance(o, TMessageEntityPhone):
        return MessageEntity(
            type='phone_number',
            offset=o.offset,
            length=o.length,
        )
    if isinstance(o, TMessageEntityPre):
        return MessageEntity(
            type='pre',
            offset=o.offset,
            length=o.length,
        )
    if isinstance(o, TMessageEntityStrike):
        return MessageEntity(
            type='strikethrough',  # Todo
            offset=o.offset,
            length=o.length,
        )
    if isinstance(o, TMessageEntityTextUrl):
        return MessageEntity(
            type='text_link',
            offset=o.offset,
            length=o.length,
            url=o.url,
        )
    if isinstance(o, TMessageEntityUnderline):
        return MessageEntity(
            type='underline',  # Todo
            offset=o.offset,
            length=o.length,
        )
    if isinstance(o, TMessageEntityUnknown):
        return MessageEntity(
            type='unknown',
            offset=o.offset,
            length=o.length,
        )
    if isinstance(o, TMessageEntityUrl):
        return MessageEntity(
            type='url',
            offset=o.offset,
            length=o.length,
        )
    if isinstance(o, datetime):
        return int(o.timestamp())
    if isinstance(o, tuple):
        return tuple(to_web_api(list(o)))
    if isinstance(o, list):
        return [to_web_api(x) for x in o]
    if isinstance(o, dict):
        return {k: to_web_api(v) for k, v in o.items()}
    if isinstance(o, (bool, str, int, float)):
        return o
    if o is None:
        return None
    raise TypeError(f'Type not handled: {type(o)} with value {o!r}')
# end def
