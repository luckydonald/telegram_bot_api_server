#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum
from io import BytesIO
from os import path
from typing import Union, Optional, List

import httpx
from fastapi import APIRouter as Blueprint, HTTPException, UploadFile
from fastapi.params import Query
from starlette.requests import Request
from telethon.errors import BotMethodInvalidError
from telethon.tl.types import TypeSendMessageAction, InputStickerSetShortName, InputMessageID
from telethon.client.chats import _ChatAction
from luckydonaldUtils.files.mime import get_file_suffix
from luckydonaldUtils.logger import logging
from telethon.tl.functions.messages import SetTypingRequest, GetStickerSetRequest

from ....tools.fastapi_issue_884_workaround import Json, parse_obj_as
from ....tools.responses import r_success, JSONableResponse, r_error
from ....constants import TOKEN_VALIDATION
from ....deserializer import to_telethon
from ....serializer import to_web_api, get_entity
from ..generated.models import ForceReplyModel, InlineKeyboardMarkupModel, ReplyKeyboardMarkupModel, ReplyKeyboardRemoveModel
from ..custom_models import InputFileModel, AttachUrl

__author__ = 'luckydonald'
DOWNLOAD_MAX_SIZE = 10 * 1024 * 1024

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if


routes = Blueprint()  # Basically a Blueprint


@routes.api_route('/{token}/sendPhoto', methods=['GET', 'POST'], tags=['official'])
async def send_photo(
    token: str = TOKEN_VALIDATION,
    chat_id: Union[int, str] = Query(..., description='Unique identifier for the target chat or username of the target channel (in the format @channelusername)'),
    photo: 'InputFileModel' = Query(..., description='Photo to send. Pass a file_id as String to send a photo that exists on the Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get a photo from the Internet, or upload a new photo using multipart/form-data. More info on Sending Files »'),
    caption: Optional[str] = Query(None, description='Photo caption (may also be used when resending photos by file_id), 0-1024 characters'),
    parse_mode: Optional[str] = Query(None, description='Send Markdown or HTML, if you want Telegram apps to show bold, italic, fixed-width text or inline URLs in the media caption.'),
    disable_notification: Optional[bool] = Query(None, description='Sends the message silently. Users will receive a notification with no sound.'),
    reply_to_message_id: Optional[int] = Query(None, description='If the message is a reply, ID of the original message'),
    reply_markup: Optional[Json[Union['InlineKeyboardMarkupModel', 'ReplyKeyboardMarkupModel', 'ReplyKeyboardRemoveModel', 'ForceReplyModel']]] = Query(None, description='Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.'),
    request: Request=None,
) -> JSONableResponse:
    """
    Use this method to send photos. On success, the sent Message is returned.

    https://core.telegram.org/bots/api#sendphoto
    """
    photo: Union[InputFileModel, str] = parse_obj_as(
        Union[InputFileModel, str],
        obj=photo,
    )
    reply_markup: Optional[Union[InlineKeyboardMarkupModel, ReplyKeyboardMarkupModel, ReplyKeyboardRemoveModel, ForceReplyModel]] = parse_obj_as(
        Optional[Union[InlineKeyboardMarkupModel, ReplyKeyboardMarkupModel, ReplyKeyboardRemoveModel, ForceReplyModel]],
        obj=reply_markup,
    )

    from ....main import _get_bot
    bot = await _get_bot(token)

    try:
        entity = await get_entity(bot, chat_id)
    except BotMethodInvalidError:
        assert isinstance(chat_id, int) or (isinstance(chat_id, str) and len(chat_id) > 0 and chat_id[0] == '@')
        entity = chat_id
    except ValueError:
        raise HTTPException(404, detail="chat not found?")
    # end try

    if isinstance(photo, str):
        # url, attachment or file_id
        if photo.startswith('attach://'):
            field = photo[9:]
            # new we need to qurey the resulting field
            form = await request.form()
            if not form[field]:
                from pydantic import MissingError
                from fastapi.exceptions import RequestValidationError
                from pydantic.error_wrappers import ErrorWrapper

                raise RequestValidationError(
                    errors=[
                        ErrorWrapper(
                            MissingError(), loc=('form', field)
                        ),
                    ],
                )
            # end if
            photo = form[field]
            try:
                UploadFile.validate(photo)
            except ValueError as e:
                from pydantic import MissingError
                from fastapi.exceptions import RequestValidationError
                from pydantic.error_wrappers import ErrorWrapper

                raise RequestValidationError(
                    errors=[
                        ErrorWrapper(
                            e, loc=('form', field)
                        ),
                    ],
                )
            # end try
        elif photo.startswith('http'):  # either http:// and https://
            from urllib.parse import urlparse
            parsed_url = urlparse(photo)
            filename = path.basename(parsed_url.path)
            async with httpx.AsyncClient() as client:
                try:
                    async with client.stream('GET', photo) as response:
                        if response.status_code != 200:
                            return r_error(
                                400,
                                description="BAD REQUEST: failed to get HTTP URL content (non 200 status code)",
                                result={'reason': 'status_code', 'status_code': response.status_code},
                            )
                        # end if
                        content_length = response.headers.get('Content-Length', None)
                        if content_length:
                            try:
                                content_length = int(content_length)
                                if content_length > DOWNLOAD_MAX_SIZE:
                                    return r_error(
                                        400,
                                        description="BAD REQUEST: failed to get HTTP URL content (Content-Length too large)",
                                        result={'reason': 'size'},
                                    )
                                # end if
                            except ValueError:
                                pass
                            # end try
                        # end if

                        size = 0
                        file_bytes = BytesIO()
                        file_bytes.name = filename
                        async for chunk in response.aiter_bytes():
                            size += len(chunk)
                            file_bytes.write(chunk)
                            if size > DOWNLOAD_MAX_SIZE:
                                return r_error(
                                    400,
                                    description="BAD REQUEST: failed to get HTTP URL content (download too large)",
                                    result={'reason': 'size'},
                                )
                            # end if
                        # end for
                        file_bytes.seek(0)
                        photo = file_bytes
                    # end with
                except httpx.exceptions.HTTPError as e:
                    return r_error(
                        400,
                        description="BAD REQUEST: failed to get HTTP URL content (connection error)",
                        result={'reason': 'get'},
                    )
                # end try
            # end with
        # end if
    # end if

    buttons = await to_telethon(reply_markup, bot)

    result = await bot.send_file(
        entity=entity,
        file=photo,
        force_document=False,
        caption=caption,
        parse_mode=parse_mode,
        silent=disable_notification,
        reply_to=reply_to_message_id,
        buttons=buttons,
    )
    data = await to_web_api(result, bot)
    return r_success(data.to_array())
# end def
