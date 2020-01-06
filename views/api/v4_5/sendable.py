#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum
from tools import r_success
from typing import Union
from fastapi import APIRouter as Blueprint, HTTPException
from constants import TOKEN_VALIDATION
from serializer import to_web_api, get_entity
from fastapi.params import Query
from telethon.tl.types import TypeSendMessageAction
from telethon.client.chats import _ChatAction
from luckydonaldUtils.logger import logging
from telethon.tl.functions.messages import SetTypingRequest

__author__ = 'luckydonald'


logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if


routes = Blueprint()  # Basically a Blueprint


@routes.api_route('/{token}/sendMessage', methods=["GET", "POST"], tags=["send"])
async def send_message(
    token: str = TOKEN_VALIDATION,
    chat_id: Union[int, str] = Query(..., description="Unique identifier for the target chat or username of the target channel (in the format @channelusername)", regex=r"@[a-zA-Z][a-zA-Z0-9_]{2,}"),
    text: str = Query(..., description="Text of the message to be sent"),
    parse_mode: Union[str, None] = Query(None, description="Send Markdown or HTML, if you want Telegram apps to show bold, italic, fixed-width text or inline URLs in your bot's message."),
    disable_web_page_preview: bool = Query(False, description="Disables link previews for links in this message"),
    disable_notification: bool = Query(False, description="Sends the message silently. Users will receive a notification with no sound."),
    reply_to_message_id: Union[int, None] = Query(None, description="If the message is a reply, ID of the original message"),
    reply_markup: Union[str, None] = Query(None, description="Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user."),
):
    from main import _get_bot
    bot = await _get_bot(token)
    try:
        entity = await get_entity(bot, chat_id)
        # end try
    except ValueError:
        raise HTTPException(404, detail="chat not found?")
    # end try

    await bot.get_dialogs()
    msg = await bot.send_message(
        entity=entity,
        message=text,
        parse_mode=parse_mode,
        link_preview=not disable_web_page_preview,
        silent=disable_notification,
        reply_to=reply_to_message_id,
        buttons=reply_markup,
    )
    data = await to_web_api(msg, bot)
    return r_success(data.to_array())
# end def


class ChatAction(Enum):
    TYPING = "typing"
    UPLOAD_PHOTO = "upload_photo"
    RECORD_VIDEO = "record_video"
    UPLOAD_VIDEO = "upload_video"
    RECORD_AUDIO = "record_audio"
    UPLOAD_AUDIO = "upload_audio"
    UPLOAD_DOCUMENT = "upload_document"
    FIND_LOCATION = "find_location"
    RECORD_VIDEO_NOTE = "record_video_note"
    UPLOAD_VIDEO_NOTE = "upload_video_note"

    # extra:
    PLAY_GAME = "play_game"
    CHOOSE_CONTACT = "choose_contact"
    CANCEL = "cancel"
# end class


actions_api_to_telethon_mapping = {
    ChatAction.TYPING: "typing",
    ChatAction.UPLOAD_PHOTO: "photo",
    ChatAction.RECORD_VIDEO: "record-video",
    ChatAction.UPLOAD_VIDEO: "video",
    ChatAction.RECORD_AUDIO: "record-audio",
    ChatAction.UPLOAD_AUDIO: "audio",
    ChatAction.UPLOAD_DOCUMENT: "document",
    ChatAction.FIND_LOCATION: "location",
    ChatAction.RECORD_VIDEO_NOTE: "record-round",
    ChatAction.UPLOAD_VIDEO_NOTE: "round",
    # extra:
    ChatAction.CANCEL: "cancel",
    ChatAction.PLAY_GAME: "game",
    ChatAction.CHOOSE_CONTACT: "contact",
}


@routes.api_route('/{token}/sendChatAction', methods=["GET", "POST"], tags=['send'])
async def send_chat_action(
    token: str = TOKEN_VALIDATION,
    chat_id: Union[int, str] = Query(..., description="Unique identifier for the target chat or username of the target channel (in the format @channelusername)", regex=r"@[a-zA-Z][a-zA-Z0-9_]{2,}"),
    action: ChatAction = Query(..., description='Type of action to broadcast. Choose one, depending on what the user is about to receive: "typing" for text messages, "upload_photo" for photos, "record_video" or "upload_video" for "videos", "record_audio" or "upload_audio" for audio files, "upload_document" for general files, "find_location" for location data, "record_video_note" or "upload_video_note" for video notes. Additionally added by this API implementation are "play_game", "choose_contact" and "cancel".'),
):
    from main import _get_bot
    bot = await _get_bot(token)
    try:
        entity = await get_entity(bot, chat_id)
        # end try
    except ValueError:
        raise HTTPException(404, detail="chat not found?")
    # end try
    client = bot

    action: str = actions_api_to_telethon_mapping[action]
    # noinspection PyProtectedMember
    action: TypeSendMessageAction = _ChatAction._str_mapping[action.lower()]
    await client(
        request=SetTypingRequest(
            peer=entity,
            action=action,
        )
    )

    return r_success()
# end def
