#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Union

from luckydonaldUtils.encoding import to_native
from luckydonaldUtils.exceptions import assert_type_or_raise
from luckydonaldUtils.logger import logging
from pytgbot.api_types.receivable.inline import InlineQuery
from pytgbot.api_types.receivable.media import ChatPhoto, UserProfilePhotos, PhotoSize, MessageEntity, Location, Voice
from pytgbot.api_types.receivable.media import Audio
from pytgbot.api_types.receivable.media import Sticker, VideoNote
from pytgbot.api_types.receivable.media import Contact, Venue, Video, Document, Animation
from pytgbot.api_types.receivable.passport import PassportData, EncryptedCredentials, EncryptedPassportElement
from pytgbot.api_types.receivable.payments import ShippingQuery, PreCheckoutQuery, OrderInfo, Invoice, SuccessfulPayment
from pytgbot.api_types.receivable.peer import User, Chat
from pytgbot.api_types.receivable.stickers import MaskPosition
from pytgbot.api_types.receivable.updates import Message, Update, CallbackQuery
from telethon.tl.types import User as TUser, Dialog
from telethon.tl.patched import Message as TMessage
from telethon.tl.types import UserProfilePhoto as TUserProfilePhoto
from telethon.tl.types import Document as TDocument
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
from telethon.tl.types import UpdateNewChannelMessage as TUpdateNewChannelMessage
from telethon.tl.types import UpdateEditChannelMessage as TUpdateEditChannelMessage
from telethon.tl.types import UpdateBotInlineQuery as TUpdateBotInlineQuery
from telethon.tl.types import UpdateBotCallbackQuery as TUpdateBotCallbackQuery
from telethon.tl.types import UpdateBotShippingQuery as TUpdateBotShippingQuery
from telethon.tl.types import UpdateBotPrecheckoutQuery as TUpdateBotPrecheckoutQuery
from telethon.tl.types import GeoPointEmpty as TGeoPointEmpty
from telethon.tl.types import GeoPoint as TGeoPoint
from telethon.tl.types import PaymentRequestedInfo as TPaymentRequestedInfo
from telethon.tl.types import Channel as TChannel
from telethon.tl.types import MessageMediaContact as TMessageMediaContact
from telethon.tl.types import MessageMediaVenue as TMessageMediaVenue
from telethon.tl.types import MessageMediaInvoice as TMessageMediaInvoice
from telethon.tl.types import DocumentAttributeImageSize as TDocumentAttributeImageSize
from telethon.tl.types import DocumentAttributeAnimated as TDocumentAttributeAnimated
from telethon.tl.types import DocumentAttributeSticker as TDocumentAttributeSticker
from telethon.tl.types import DocumentAttributeVideo as TDocumentAttributeVideo
from telethon.tl.types import DocumentAttributeAudio as TDocumentAttributeAudio
from telethon.tl.types import DocumentAttributeFilename as TDocumentAttributeFilename
from telethon.tl.types import DocumentAttributeHasStickers as TDocumentAttributeHasStickers
from telethon.tl.types import PhotoSize as TPhotoSize
from telethon.tl.types import PhotoSizeEmpty as TPhotoSizeEmpty
from telethon.tl.types import PhotoCachedSize as TPhotoCachedSize
from telethon.tl.types import PhotoStrippedSize as TPhotoStrippedSize
from telethon.tl.types import MaskCoords as TMaskCoords
from telethon.tl.types import InputStickerSetID as TInputStickerSetID
from telethon.tl.types import InputStickerSetEmpty as TInputStickerSetEmpty
from telethon.tl.types import InputStickerSetShortName as TInputStickerSetShortName
from telethon.tl.types import InputStickerSetAnimatedEmoji as TInputStickerSetAnimatedEmoji
from telethon.tl.types import Photo as TPhoto
from telethon.tl.patched import MessageService as TMessageService
from telethon.tl.types import PeerChannel as TPeerChannel
# ignoring: TMessageActionEmpty, TMessageActionHistoryClear, TMessageActionGameScore
# ingoring: TMessageActionPaymentSent, TMessageActionPhoneCall, TMessageActionScreenshotTaken
# ingoring: TMessageActionCustomAction, TMessageActionSecureValuesSent, TMessageActionContactSignUp
from telethon.tl.types import MessageActionChatEditTitle as TMessageActionChatEditTitle  # new_chat_title
from telethon.tl.types import MessageActionChatEditPhoto as TMessageActionChatEditPhoto  # new_chat_photo
from telethon.tl.types import MessageActionChatDeletePhoto as TMessageActionChatDeletePhoto  # delete_chat_photo
from telethon.tl.types import MessageActionChatAddUser as TMessageActionChatAddUser  # new_chat_members
from telethon.tl.types import MessageActionChatDeleteUser as TMessageActionChatDeleteUser  # left_chat_member
from telethon.tl.types import MessageActionChatJoinedByLink as TMessageActionChatJoinedByLink  # new_chat_members
from telethon.tl.types import MessageActionChannelCreate as TMessageActionChannelCreate  # supergroup_chat_created, channel_chat_created
from telethon.tl.types import MessageActionChatCreate as TMessageActionChatCreate  # supergroup_chat_created, channel_chat_created
from telethon.tl.types import MessageActionChatMigrateTo as TMessageActionChatMigrateTo  # migrate_to_chat_id
from telethon.tl.types import MessageActionChannelMigrateFrom as TMessageActionChannelMigrateFrom  # migrate_from_chat_id
from telethon.tl.types import MessageActionPinMessage as TMessageActionPinMessage  # pinned_message
from telethon.tl.types import MessageActionPaymentSentMe as TMessageActionPaymentSentMe  # successful_payment
from telethon.tl.types import MessageActionCustomAction as TMessageActionCustomAction  # TODO
from telethon.tl.types import MessageActionBotAllowed as TMessageActionBotAllowed  # connected_website
from telethon.tl.types import MessageActionSecureValuesSentMe as TMessageActionSecureValuesSentMe  # passport_data
from telethon.tl.types import SecureValue as TSecureValue
from telethon.tl.types import SecureCredentialsEncrypted as TSecureCredentialsEncrypted
from telethon.utils import pack_bot_file_id, get_peer_id

from tools.api import TYPE_CHANNEL, as_channel_id, calculate_file_unique_id

__author__ = 'luckydonald'

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if


MASK_POSITIONS = {
    0: "forehead",
    1: "eyes",
    2: "mouth",
    3: "chin",
}


# TODO: Document, PassportFile, File
async def to_web_api(
    o, client: 'classes.webhook.TelegramClientUpdateCollector',
    user_as_chat=False, prefer_update=True, load_photos=False, include_reply: bool = True,
    file_id: Union[str, None] = None, file_unique_id: Union[str, None] = None,
):
    """
    Converts Telethon objects to Bot API ones.

    :param o: The object to transform to an API representation.
    :param client: The Telethon bot.
    :param user_as_chat: Whether you want a user chat represented as `Chat` or as `User`.
    :param prefer_update: Whether you want a bot's inline query represented as `Update` or as `InlineQuery`.
    :param load_photos: Whether you want a `Chat` object to have the `photo` attribute filled.
    :param include_reply: Whether you want a `Message` object to have the `reply` attribute filled.
    :param file_id: For returning a `PhotoSize` the the `file_id` and `file_unique_id` are needed.
    :param file_unique_id: For returning a `PhotoSize` the the `file_id` and `file_unique_id` are needed.
    """
    if isinstance(o, TUpdateNewMessage):
        return Update(
            update_id=client.update_id,
            message=await to_web_api(o.message, client),
        )
    if isinstance(o, TUpdateEditMessage):
        return Update(
            update_id=client.update_id,
            edited_message=await to_web_api(o.message, client),
        )
    if isinstance(o, TUpdateNewChannelMessage):
        message: Message = await to_web_api(o.message, client)
        if message.chat.type == 'channel':
            return Update(
                update_id=client.update_id,
                channel_post=message,
            )
        # end if
        return Update(
            update_id=client.update_id,
            message=message,
        )
    if isinstance(o, TUpdateEditChannelMessage):
        message: Message = await to_web_api(o.message, client)
        if message.chat.type == 'channel':
            return Update(
                update_id=client.update_id,
                edited_channel_post=message,
            )
        # end if
        return Update(
            update_id=client.update_id,
            edited_message=message,
        )
    if isinstance(o, TUpdateBotInlineQuery):
        if prefer_update:
            return Update(
                update_id=client.update_id,
                inline_query=await to_web_api(o, client, prefer_update=False)
            )
        user = await get_entity(client, o.user_id)
        return InlineQuery(
            id=o.query_id,
            from_peer=await to_web_api(user, client),
            query=o.query,
            offset=o.offset,
            location=await to_web_api(o.geo, client),
        )
    # if isinstance(object, ???):
    #     return Update(
    #         update_id=client.update_id,
    #         chosen_inline_result=await to_web_api(object.message),  # TODO
    #     )
    if isinstance(o, TUpdateBotCallbackQuery):
        if prefer_update:
            return Update(
                update_id=client.update_id,
                callback_query=await to_web_api(o, client, prefer_update=False),
            )
        # end if
        return CallbackQuery(
            id=o.query_id,
            from_peer=await to_web_api(o.peer, client),
            chat_instance=str(o.chat_instance),
            message=load_message(o.msg_id, o.chat_instance),
            # inline_message_id=object TODO
            data=o.data,
            game_short_name=o.game_short_name,
        )
    if isinstance(o, TUpdateBotShippingQuery):
        if prefer_update:
            return Update(
                update_id=client.update_id,
                shipping_query=await to_web_api(o, client, prefer_update=False),
            )
        # end if
        user = await get_entity(client, o.user_id)
        user = await to_web_api(user)
        return ShippingQuery(
            id=o.query_id,
            from_peer=user,
            invoice_payload=o.payload,
            shipping_address=o.shipping_address,
        )
    if isinstance(o, TUpdateBotPrecheckoutQuery):
        if prefer_update:
            return Update(
                update_id=client.update_id,
                pre_checkout_query=await to_web_api(o, client, prefer_update=False),
            )
        # end if
        user = await get_entity(client, o.user_id)
        user = await to_web_api(user)
        return PreCheckoutQuery(
            id=o.query_id,
            from_peer=user,
            currency=o.currency,
            total_amount=o.total_amount,
            invoice_payload=o.payload,
            shipping_option_id=o.shipping_option_id,
            order_info=await to_web_api(o.info, client),
        )
    if isinstance(o, TPhotoSizeEmpty):
        return None
    if isinstance(o, TPhotoSize):
        assert_type_or_raise(file_id, str, parameter_name='file_id')
        assert_type_or_raise(file_unique_id, str, parameter_name='file_unique_id')
        return PhotoSize(
            file_id=file_id,
            file_unique_id=file_unique_id,
            width=o.w,
            height=o.h,
            file_size=o.size,
        )
    if isinstance(o, TPhotoCachedSize):
        assert_type_or_raise(file_id, str, parameter_name='file_id')
        assert_type_or_raise(file_unique_id, str, parameter_name='file_unique_id')
        return PhotoSize(
            file_id=file_id,
            file_unique_id=file_unique_id,
            width=o.w,
            height=o.h,
            file_size=len(o.bytes),
        )
    if isinstance(o, TPhotoStrippedSize):
        assert_type_or_raise(file_id, str, parameter_name='file_id')
        assert_type_or_raise(file_unique_id, str, parameter_name='file_unique_id')
        return PhotoSize(
            file_id=file_id,
            file_unique_id=file_unique_id,
            width=0,  # TODO
            height=0,  # TODO
            file_size=len(o.bytes),
        )
    if isinstance(o, TDocument):
        data = {
            'file_id': pack_bot_file_id(o),
            'calculate_file_unique_id': calculate_file_unique_id(o.id),
            'thumb': None,
        }
        # thumb: TTypePhotoSize = o.thumbs[0]
        # thumb = await to_web_api(thumb, file_id=thumb.location)

        for attr in o.attributes:
            if isinstance(attr, TDocumentAttributeAnimated):
                data['is_animated'] = True
            if isinstance(attr, TDocumentAttributeAudio):
                data['duration'] = attr.duration
                data['voice'] = attr.voice
                data['title'] = attr.title
                data['performer'] = attr.performer
                # data['waveform'] = attr.waveform
            if isinstance(attr, TDocumentAttributeFilename):
                data['file_name'] = attr.file_name
            if isinstance(attr, TDocumentAttributeImageSize):
                data['width'] = attr.w
                data['height'] = attr.h
                # end if
            if isinstance(attr, TDocumentAttributeSticker):
                sticker_set: Union[str, None] = await to_web_api(attr.stickerset, client)
                data['emoji'] = attr.alt
                data['set_name'] = sticker_set
                data['mask'] = attr.mask
                data['mask_position'] = await to_web_api(attr.mask_coords, client)
            # end if
            if isinstance(attr, TDocumentAttributeVideo):
                data['width'] = attr.w
                data['height'] = attr.h
                data['duration'] = attr.duration
            # end if
            data['thumb'] = None  # TODO get this information from somewhere.
            data['mime_type'] = None  # TODO get this information from somewhere.
            data['file_size'] = None  # TODO get this information from somewhere.
        # end for
        for attr in o.attributes:
            if isinstance(attr, TDocumentAttributeSticker):
                return Sticker(
                    file_id=data['file_id'],
                    file_unique_id=data['file_unique_id'],
                    width=data['width'],
                    height=data['height'],
                    is_animated=data.get('is_animated', False),
                    thumb=data.get('thumb'),
                    emoji=data.get('emoji'),
                    set_name=data.get('set_name'),
                    mask_position=data.get('mask_position'),
                    file_size=data.get('file_size'),
                )
            # end if
            if isinstance(attr, TDocumentAttributeAnimated):
                return Animation(
                    file_id=data['file_id'],
                    file_unique_id=data['file_unique_id'],
                    width=data['width'],
                    height=data['height'],
                    duration=data['duration'],
                    thumb=data.get('thumb'),
                    file_name=data.get('file_name'),
                    mime_type=data.get('mime_type'),
                    file_size=data.get('file_size'),
                )
            if isinstance(attr, TDocumentAttributeAudio):
                if attr.voice:
                    return Voice(
                        file_id=data['file_id'],
                        file_unique_id=data['file_unique_id'],
                        duration=data['duration'],
                        mime_type=data.get('mime_type'),
                        file_size=data.get('file_size'),
                    )
                # end if
                return Audio(
                    file_id=data['file_id'],
                    file_unique_id=data['file_unique_id'],
                    duration=data['duration'],
                    performer=data.get('performer'),
                    title=data.get('title'),
                    mime_type=data.get('mime_type'),
                    file_size=data.get('file_size'),
                    thumb=data.get('thumb'),
                )
            if isinstance(attr, TDocumentAttributeVideo):
                if attr.round_message:
                    return VideoNote(
                        file_id=data['file_id'],
                        file_unique_id=data['file_unique_id'],
                        length=data['length'],
                        duration=data['duration'],
                        thumb=data.get('thumb'),
                        file_size=data.get('file_size'),
                    )
                # end if
                return Video(
                    file_id=data['file_id'],
                    file_unique_id=data['file_unique_id'],
                    width=data['width'],
                    height=data['height'],
                    duration=data['duration'],
                    thumb=data.get('thumb'),
                    mime_type=data.get('mime_type'),
                    file_size=data.get('file_size'),
                )
            # end if
            if isinstance(attr, TDocumentAttributeHasStickers):
                raise ValueError(f'Unexpected {type(attr)}')
        # end for
        return Document(
            file_id=data['file_id'],
            file_unique_id=data['file_unique_id'],
            thumb=await to_web_api(o.thumbs[0], client),
            file_name=data.get('file_name'),
            mime_type=data.get('mime_type'),
            file_size=data.get('file_size'),
        )
    if isinstance(o, TMaskCoords):
        return MaskPosition(
            point=MASK_POSITIONS[o.n],  # One of “forehead”, “eyes”, “mouth”, or “chin”.
            x_shift=o.x,
            y_shift=o.y,
            scale=o.zoom,
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
        chat_id = get_peer_id(o)
        if user_as_chat:
            return Chat(
                id=chat_id,
                type='private',
                # title=None,
                first_name=o.first_name,
                last_name=o.last_name,
                username=o.username,
                # TODO: all_members_are_administrators=,
                photo=await to_web_api(o.photo, client) if load_photos else None,
                # description=None,
                # invite_link=None,
                # pinned_message=None,
                # sticker_set_name=None,
                # can_set_sticker_set=None,
            )
        return User(
            id=chat_id,
            is_bot=o.bot,
            first_name=o.first_name,
            last_name=o.last_name,
            username=o.username,
            language_code=o.lang_code,
        )
    # end if
    if isinstance(o, TChannel):
        if o.megagroup:  # or maybe o.broadcast?
            # https://t.me/BotDevelopment/109268
            return Chat(
                id=get_peer_id(o),
                type='supergroup',
                title=o.title,
                username=o.username,
            )
        # end if
        return Chat(
            id=get_peer_id(o),
            type='channel',
            title=o.title,
            username=o.username,
        )
    if isinstance(o, TUserProfilePhoto):
        if user_as_chat:
            return ChatPhoto(
                small_file_id=pack_bot_file_id(o.photo_small),
                small_file_unique_id=calculate_file_unique_id(o.photo_big.local_id),
                big_file_id=pack_bot_file_id(o.photo_big),
                big_file_unique_id=calculate_file_unique_id(o.photo_small.local_id),
            )
        return UserProfilePhotos(
            total_count=2,
            photos=[
                PhotoSize(
                    file_id=pack_bot_file_id(o.photo_big),
                    file_unique_id=calculate_file_unique_id(o.photo_big.local_id),
                    width=0,  # TODO somehow look up more data.
                    height=0  # TODO somehow look up more data.
                ),
                PhotoSize(
                    file_id=pack_bot_file_id(o.photo_small),
                    file_unique_id=calculate_file_unique_id(o.photo_small.local_id),
                    width=0,  # TODO somehow look up more data.
                    height=0  # TODO somehow look up more data.
                ),
            ],
        )
    if isinstance(o, (TMessage, TMessageService)):
        chat = await get_entity(client, o.chat_id)
        chat: Chat = await to_web_api(chat, client, user_as_chat=True)
        from_peer: Union[None, User] = None
        if chat and chat.type != TYPE_CHANNEL:  # supposed to be None for 'channel's.
            if o.sender_id is not None:
                from_peer = await get_entity(client, o.sender_id)
            else:
                from_peer = await get_entity(client, o.input_chat)
            # end if
            from_peer = await to_web_api(from_peer, client)
        # end if
        date = await to_web_api(o.date, client)

        if isinstance(o, TMessage):
            reply = None
            if include_reply and o.is_reply:
                reply = await get_reply_message(o)
                reply = await to_web_api(reply, client, include_reply=False)  # don't have a reply in the reply.
            # end if
            forward_date = None
            forward_from = None
            forward_from_chat = None
            forward_signature = None
            forward_from_message_id = None
            if o.fwd_from:
                forward_date = o.fwd_from.date
                forward_date = await to_web_api(forward_date, client)
                if o.fwd_from.channel_id:
                    # we forwarded from a channel
                    # e.g. 1127537892 -> -1001127537892
                    channel_id = as_channel_id(o.fwd_from.channel_id)

                    forward_from_chat = await get_entity(client, channel_id)
                    forward_from_chat = await to_web_api(forward_from_chat, client)
                    forward_from_message_id = o.fwd_from.channel_post
                # end if
                if o.fwd_from.from_id:
                    forward_from = await get_entity(client, o.fwd_from.from_id)
                    forward_from = await to_web_api(forward_from, client)
                # end if
                forward_signature = o.fwd_from.post_author
            # end if
            author_signature = o.post_author

            entities = None if not o.entities else await to_web_api(o.entities, client)  # [] should be None
            return Message(
                message_id=o.id,
                date=date,
                chat=chat,

                from_peer=from_peer,
                forward_from=forward_from,
                forward_from_chat=forward_from_chat,
                forward_from_message_id=forward_from_message_id,
                forward_signature=forward_signature,
                forward_date=forward_date,
                reply_to_message=reply,
                edit_date=await to_web_api(o.edit_date, client),
                # TODO: media_group_id=,
                author_signature=author_signature,
                text=None if o.media else o.raw_text,
                caption=o.raw_text if o.media else None,
                entities=None if o.media else entities,  # entities can be ether part of a caption or text
                caption_entities=entities if o.media else None,  # entities can be ether part of a caption or text
                document=None if any([o.photo, o.sticker, o.video, o.voice, o.video_note]) else await to_web_api(o.document, client),
                # animation=await to_web_api(o.animation), TODO
                audio=await to_web_api(o.audio, client),
                # game=await to_web_api(o.game), TODO
                photo=await to_web_api(o.photo, client),
                sticker=await to_web_api(o.sticker, client),
                video=None if o.video_note else await to_web_api(o.video, client),
                voice=await to_web_api(o.voice, client),
                video_note=await to_web_api(o.video_note, client),
                contact=await to_web_api(o.contact, client),
                location=await to_web_api(o.geo, client),
                venue=await to_web_api(o.venue, client),
                # pinned_message=, TODO
                invoice=await to_web_api(o.invoice, client),
            )
        else:  # must be TMessageService
            assert isinstance(o, TMessageService)
            # end if
            if isinstance(o.action, TMessageActionChatAddUser):
                users = []
                for user_id in o.action.users:
                    user = await get_entity(client, user_id)
                    user = await to_web_api(user, client)
                    users.append(user)
                # end for
                return Message(
                    message_id=o.id,
                    date=date,
                    chat=chat,
                    from_peer=from_peer,
                    new_chat_members=users,
                    invoice=None,
                )
            # end if
            if isinstance(o.action, TMessageActionChatEditTitle):
                return Message(
                    message_id=o.id,
                    date=date,
                    chat=chat,
                    from_peer=from_peer,
                    new_chat_title=o.action.title,
                    invoice=None,
                )
            # end if
            if isinstance(o.action, TMessageActionChatEditPhoto):
                return Message(
                    message_id=o.id,
                    date=date,
                    chat=chat,
                    from_peer=from_peer,
                    new_chat_photo=await to_web_api(o.action.photo, client),
                    invoice=None,
                )
            # end if
            if isinstance(o.action, TMessageActionChatDeletePhoto):
                return Message(
                    message_id=o.id,
                    date=date,
                    chat=chat,
                    from_peer=from_peer,
                    delete_chat_photo=True,
                    invoice=None,
                )
            if isinstance(o.action, TMessageActionChatDeleteUser):
                user = await get_entity(client, o.action.user_id)
                user = await to_web_api(user)
                return Message(
                    message_id=o.id,
                    date=date,
                    chat=chat,
                    from_peer=from_peer,
                    left_chat_member=user,
                    invoice=None,
                )
            # end if
            if isinstance(o.action, TMessageActionChatJoinedByLink):
                user = await get_entity(client, o.from_id)
                user = await to_web_api(user)
                # TODO is swapping from_peer(inviter_id) and new_chat_members(from_id), is that correct?
                return Message(
                    message_id=o.id,
                    date=date,
                    chat=chat,
                    from_peer=from_peer,
                    new_chat_members=[user],
                    invoice=None,
                )
            # end if
            if isinstance(o.action, (TMessageActionChannelCreate, TMessageActionChatCreate)):
                return Message(
                    message_id=o.id,
                    date=date,
                    chat=chat,
                    from_peer=from_peer,
                    group_chat_created=chat.type == 'group',  # either group, chat or supergroup
                    supergroup_chat_created=chat.type == 'supergroup',  # either group, chat or supergroup
                    channel_chat_created=chat.type == 'chat',  # either group, chat or supergroup
                    invoice=None,
                )
            # end if
            if isinstance(o.action, TMessageActionChatMigrateTo):
                return Message(
                    message_id=o.id,
                    date=date,
                    chat=chat,
                    from_peer=from_peer,
                    migrate_to_chat_id=o.action.channel_id,
                    invoice=None,
                )
            # end if
            if isinstance(o.action, TMessageActionChannelMigrateFrom):
                return Message(
                    message_id=o.id,
                    date=date,
                    chat=chat,
                    from_peer=from_peer,
                    migrate_from_chat_id=o.action.chat_id,
                    invoice=None,
                )
            # end if
            if isinstance(o.action, TMessageActionPinMessage):
                # TODO
                # maybe o.message?
                # or we have to load the message with o.id, like in get_pinned_message()
                # raise ValueError('Pins need to load the message')
                return Message(
                    message_id=o.id,
                    date=date,
                    chat=chat,
                    from_peer=from_peer,
                    pinned_message=load_message(o.to_id, o.from_id),
                    invoice=None,
                )
            # end if
            if isinstance(o.action, TMessageActionPaymentSentMe):
                return Message(
                    message_id=o.id,
                    date=date,
                    chat=chat,
                    from_peer=from_peer,
                    invoice=None,
                    successful_payment=await to_web_api(o.action, client),
                )
            # end if
            if isinstance(o.action, TMessageActionCustomAction):
                raise ValueError(f'Unknown custom action {o.action.message!r} (o.action = TMessageActionCustomAction)')
                return Message(
                    message_id=o.id,
                    date=date,
                    chat=chat,
                    from_peer=from_peer,
                    invoice=None,
                )
            # end if
            if isinstance(o.action, TMessageActionBotAllowed):
                return Message(
                    message_id=o.id,
                    date=date,
                    chat=chat,
                    from_peer=from_peer,
                    invoice=None,
                    connected_website=o.action.domain,
                )
            # end if
            if isinstance(o.action, TMessageActionSecureValuesSentMe):
                return Message(
                    message_id=o.id,
                    date=date,
                    chat=chat,
                    from_peer=from_peer,
                    invoice=None,
                    passport_data=await to_web_api(o.action, client)
                )
            # end if
            if isinstance(o.action, TMessageActionChatAddUser):
                return Message(
                    message_id=o.id,
                    date=date,
                    chat=chat,
                    from_peer=from_peer,
                    invoice=None,
                )
            # end if
            if isinstance(o.action, TMessageActionChatAddUser):
                return Message(
                    message_id=o.id,
                    date=date,
                    chat=chat,
                    from_peer=from_peer,
                    invoice=None,
                )
            # end if
        # end if TMessageService
    if isinstance(o, TMessageActionPaymentSentMe):
        return SuccessfulPayment(
            currency=o.currency,
            total_amount=o.total_amount,
            invoice_payload=o.payload,
            telegram_payment_charge_id=o.charge.id,
            provider_payment_charge_id=o.charge.provider_charge_id,
            shipping_option_id=o.shipping_option_id,
            order_info=await to_web_api(o.info, client) if o.info else None,
        ),
    if isinstance(o, TMessageActionSecureValuesSentMe):
        return PassportData(
            data=await to_web_api(o.values, client),
            credentials=await to_web_api(o.credentials, client),
        ),
    if isinstance(o, TSecureValue):
        raise ValueError('TSecureValue not implemented')
        return EncryptedPassportElement(
            type=await to_web_api(o, client, o.type),
            # One of “personal_details”, “passport”, “driver_license”, “identity_card”, “internal_passport”, “address”, “utility_bill”, “bank_statement”, “rental_agreement”, “passport_registration”, “temporary_registration”, “phone_number”, “email”.
            # TypeSecureValueType = SecureValueTypePersonalDetails,SecureValueTypePassport,SecureValueTypeDriverLicense,SecureValueTypeIdentityCard,SecureValueTypeInternalPassport,SecureValueTypeAddress,SecureValueTypeUtilityBill,SecureValueTypeBankStatement,SecureValueTypeRentalAgreement,SecureValueTypePassportRegistration,SecureValueTypeTemporaryRegistration,SecureValueTypePhone,SecureValueTypeEmail
            hash=to_native(o.hash),
            data=await to_web_api(o.data, client),  # TypeSecureData = SecureData
            phone_number=o.ph,
            email=None,
            files=None,
            front_side=None,
            reverse_side=None,
            selfie=None,
            translation=None,
        )
    if isinstance(o, TSecureCredentialsEncrypted):
        return EncryptedCredentials(
            data=o.data,
            hash=o.hash,
            secret=o.secret,
        )
    if isinstance(o, TPaymentRequestedInfo):
        return OrderInfo(
            name=o.name,
            phone_number=o.phone,
            email=o.email,
            shipping_address=o.shipping_address,
        )
    if isinstance(o, TPeerChannel):
        peer = await get_entity(client, o.channel_id)
        return await to_web_api(peer, client)
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
        user = await get_entity(client, o.user_id)
        user = await to_web_api(user)
        return MessageEntity(
            type='text_mention',
            offset=o.offset,
            length=o.length,
            user=user,
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
    if isinstance(o, TMessageMediaContact):
        return Contact(
            phone_number=o.phone_number,
            first_name=o.first_name,
            last_name=o.last_name,
            user_id=o.user_id,
            vcard=o.vcard,
        )
    if isinstance(o, TMessageMediaVenue):
        return Venue(
            location=await to_web_api(o.geo, client),
            title=o.title,
            address=o.address,
            foursquare_id=o.venue_id if o.venue_type == 'foursquare' else None,
        )
    if isinstance(o, TMessageMediaInvoice):
        return Invoice(
            title=o.title,
            description=o.description,
            start_parameter=o.start_param,
            currency=o.currency,
            total_amount=o.total_amount,
        )
    if isinstance(o, TInputStickerSetID):
        return None
        pass
    if isinstance(o, TInputStickerSetEmpty):
        return ''
    if isinstance(o, TInputStickerSetShortName):
        return o.short_name
    if isinstance(o, TInputStickerSetAnimatedEmoji):
        return None
    if isinstance(o, TPhoto):
        file_id = pack_bot_file_id(o)
        file_unique_id = calculate_file_unique_id(o.id)
        return [
            await to_web_api(size, client, file_id=file_id, file_unique_id=file_unique_id)
            for size in o.sizes
            if not isinstance(size, (TPhotoSizeEmpty, TPhotoStrippedSize))
        ]
    if isinstance(o, datetime):
        return int(o.timestamp())
    if isinstance(o, tuple):
        return tuple(await to_web_api(list(o), client, file_id=file_id, file_unique_id=file_unique_id))
    if isinstance(o, list):
        return [await to_web_api(x, client, file_id=file_id, file_unique_id=file_unique_id) for x in o]
    if isinstance(o, dict):
        return {k: await to_web_api(v, client) for k, v in o.items()}
    if isinstance(o, (bool, str, int, float)):
        return o
    if o is None:
        return None
    raise TypeError(f'Type not handled: {type(o)} with value {o!r}')


async def get_entity(client, peer):
    """ wrapper for debug. """
    logger.debug(f'Loading entity for peer {peer!r}')
    try:
        entity = await client.get_entity(peer)
    except ValueError as e:
        # so we are not a bot, and
        dialog: Dialog
        for dialog in await client.get_dialogs(ignore_migrated=True):
            print(dialog)
            if dialog.id == peer:
                entity = dialog.input_entity
                break
            # elif dialog.peer and dialog.peer.chat_id and dialog.peer.chat_id.id == peer:
            if hasattr(dialog.peer, 'chat_id'):
                found_chat_id = dialog.peer.chat_id
                # entity = dialog.input_entity
            elif hasattr(dialog.peer, 'user_id'):
                found_chat_id = dialog.peer.user_id
                # entity = dialog.input_entity
            elif hasattr(dialog.peer, 'channel_id'):
                found_chat_id = dialog.peer.channel_id
                # entity = dialog.input_entity
            else:
                raise ValueError('Not chat/user/channel id.')
                # full = await client(GetFullUserRequest(entity))
            # end if
            if found_chat_id == peer:
                entity = dialog.input_entity
                break
            # end if
        else:
            raise e
        # end for
    with open(f'logs/peer_{peer!s}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt', 'w') as f:
        f.write('from telethon.tl.types import *\nfrom telethon.tl.patched import *\nimport datetime\n\n')
        f.write(f'input = {peer}\nresult = {entity!s}')
    # end with
    return entity
# end def


async def get_reply_message(e: TMessage):
    """ wrapper for debug. """
    msg = await e.get_reply_message()
    with open(f'logs/msg_{e.chat_id!s}#{e.id}#{e.id}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt', 'w') as f:
        f.write('from telethon.tl.types import *\nfrom telethon.tl.patched import *\nimport datetime\n\n')
        f.write(f'{{\n  "{e.chat_id!s}#{e.id}": {msg!s}\n}}')
    # end with
    return msg
# end def