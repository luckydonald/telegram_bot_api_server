#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum
from io import BytesIO
from os import path, SEEK_END, SEEK_SET
from tempfile import SpooledTemporaryFile, TemporaryFile
from typing import Union, Optional, List

import httpx
from fastapi import APIRouter as Blueprint, HTTPException, UploadFile
from fastapi.params import Query, Param, File
from pydantic.fields import FieldInfo
from starlette.concurrency import run_in_threadpool
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
    file = photo
    file: Union[InputFileModel, str] = parse_obj_as(
        Union[InputFileModel, str],
        obj=file,
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

    given_file = file
    if isinstance(given_file, str):
        # url, attachment or file_id
        # noinspection PyProtectedMember
        if given_file.startswith('attach://'):
            field = given_file[9:]
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
            # noinspection PyTypeChecker
            file: UploadFile = form[field]
            try:
                UploadFile.validate(file)
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
            file_name = file.filename
            original_file: UploadFile = file
            underlying_file: SpooledTemporaryFile = original_file.file
            # underlying_file is a file-like object, and has .seek and .tell available.
            # determine the size by jumping to the end and reading the position
            await run_in_threadpool(underlying_file.seek, 0, SEEK_END)
            file_size = await run_in_threadpool(underlying_file.tell)
            # reset to position 0 to be able to read it again later.
            await run_in_threadpool(underlying_file.seek, 0, SEEK_SET)
            # check that size
            if file_size > DOWNLOAD_MAX_SIZE:
                return r_error(
                    400,
                    description="BAD REQUEST: failed to get HTTP URL content (File size too large)",
                    result={'reason': 'size', 'size': file_size},
                )
            # end if

            real_file: Union[BytesIO, TemporaryFile] = underlying_file._file
            if isinstance(file, BytesIO):
                file: BytesIO = real_file
            else:
                file: BytesIO = BytesIO(real_file.read())
            # end if
            file.name = file_name
        elif given_file.startswith('http'):  # either http:// and https://
            from urllib.parse import urlparse
            parsed_url = urlparse(given_file)
            file_name = path.basename(parsed_url.path)
            async with httpx.AsyncClient() as client:
                try:
                    async with client.stream('GET', given_file) as response:
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
                                        result={'reason': 'size', 'size': content_length},
                                    )
                                # end if
                            except ValueError:
                                pass
                            # end try
                        # end if

                        size = 0
                        downloaded_file = BytesIO()
                        downloaded_file.name = file_name
                        async for chunk in response.aiter_bytes():
                            size += len(chunk)
                            downloaded_file.write(chunk)
                            if size > DOWNLOAD_MAX_SIZE:
                                return r_error(
                                    400,
                                    description="BAD REQUEST: failed to get HTTP URL content (download too large)",
                                    result={'reason': 'size'},
                                )
                            # end if
                        # end for
                        downloaded_file.seek(0)
                        file: BytesIO = downloaded_file
                    # end with
                except httpx.exceptions.HTTPError as e:
                    return r_error(
                        400,
                        description="BAD REQUEST: failed to get HTTP URL content (connection error)",
                        result={'reason': 'get'},
                    )
                # end try
            # end with
        else:
            file: str = given_file
        # end if
    # end if

    buttons = await to_telethon(reply_markup, bot)

    result = await bot.send_file(
        entity=entity,
        file=file,
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
