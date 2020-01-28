#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import httpx
from io import BytesIO
from os import path, SEEK_END, SEEK_SET
from enum import Enum
from typing import Union, Optional, List
from fastapi import APIRouter as Blueprint, HTTPException, UploadFile as FastApiUploadFile
from tempfile import SpooledTemporaryFile, TemporaryFile
from fastapi.params import Query, Param, File
from pydantic.fields import FieldInfo
from telethon.errors import BotMethodInvalidError
from starlette.requests import Request
from starlette.datastructures import UploadFile as StarletteUploadFile
from starlette.concurrency import run_in_threadpool
from telethon.tl.types import DocumentAttributeAudio, DocumentAttributeFilename
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


async def process_file(given_file: Union[str, FastApiUploadFile, StarletteUploadFile], request: Request) -> Union[BytesIO, str, JSONableResponse]:
    if isinstance(given_file, str):
        # url, attachment or file_id
        # noinspection PyProtectedMember
        if given_file.startswith('attach://'):
            field_name = given_file[9:]
            # new we need to qurey the resulting field
            form = await request.form()
            if not form[field_name]:
                from pydantic import MissingError
                from fastapi.exceptions import RequestValidationError
                from pydantic.error_wrappers import ErrorWrapper

                raise RequestValidationError(
                    errors=[
                        ErrorWrapper(
                            MissingError(), loc=('form', field_name)
                        ),
                    ],
                )
            # end if

            try:
                FastApiUploadFile.validate(given_file)
            except ValueError as e:
                from pydantic import MissingError
                from fastapi.exceptions import RequestValidationError
                from pydantic.error_wrappers import ErrorWrapper

                raise RequestValidationError(
                    errors=[
                        ErrorWrapper(
                            e, loc=('form', field_name)
                        ),
                    ],
                )
            # end try
            # noinspection PyTypeChecker
            file: FastApiUploadFile = form[field_name]
            return await process_file(file, request)
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
                        return downloaded_file
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
            # probably a file_id
            return given_file
        # end if
    elif isinstance(given_file, (FastApiUploadFile, StarletteUploadFile)):
        file_name = given_file.filename
        underlying_file: SpooledTemporaryFile = given_file.file
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
        if isinstance(real_file, BytesIO):
            file: BytesIO = real_file
        else:
            file: BytesIO = BytesIO(real_file.read())
        # end if
        file.name = file_name
        return file
    # end if
    return None
# end def


@routes.api_route('/{token}/sendPhoto', methods=['GET', 'POST'], tags=['official', 'send'])
async def send_photo(
    token: str = TOKEN_VALIDATION,
    chat_id: Union[int, str] = Query(..., description='Unique identifier for the target chat or username of the target channel (in the format @channelusername)'),
    photo: 'InputFileModel' = Query(..., description='Photo to send. Pass a file_id as String to send a photo that exists on the Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get a photo from the Internet, or upload a new photo using multipart/form-data. More info on Sending Files »'),
    caption: Optional[str] = Query(None, description='Photo caption (may also be used when resending photos by file_id), 0-1024 characters'),
    parse_mode: Optional[str] = Query(None, description='Send Markdown or HTML, if you want Telegram apps to show bold, italic, fixed-width text or inline URLs in the media caption.'),
    disable_notification: Optional[bool] = Query(None, description='Sends the message silently. Users will receive a notification with no sound.'),
    reply_to_message_id: Optional[int] = Query(None, description='If the message is a reply, ID of the original message'),
    reply_markup: Optional[Json[Union['InlineKeyboardMarkupModel', 'ReplyKeyboardMarkupModel', 'ReplyKeyboardRemoveModel', 'ForceReplyModel']]] = Query(None, description='Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.'),
    request: Request = None,
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

    file: Union[BytesIO, str] = await process_file(given_file=photo, request=request)
    if isinstance(file, JSONableResponse):
        # abort
        return file
    # end def

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


@routes.api_route('/{token}/sendAudio', methods=['GET', 'POST'], tags=['official', 'send'])
async def send_audio(
    token: str = TOKEN_VALIDATION,
    chat_id: Union[int, str] = Query(..., description='Unique identifier for the target chat or username of the target channel (in the format @channelusername)'),
    audio: 'InputFileModel' = Query(..., description='Audio file to send. Pass a file_id as String to send an audio file that exists on the Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get an audio file from the Internet, or upload a new one using multipart/form-data. More info on Sending Files »'),
    caption: Optional[str] = Query(None, description='Audio caption, 0-1024 characters'),
    parse_mode: Optional[str] = Query(None, description='Send Markdown or HTML, if you want Telegram apps to show bold, italic, fixed-width text or inline URLs in the media caption.'),
    duration: Optional[int] = Query(None, description='Duration of the audio in seconds'),
    performer: Optional[str] = Query(None, description='Performer'),
    title: Optional[str] = Query(None, description='Track name'),
    thumb: Optional[Json[Union['InputFileModel', str]]] = Query(None, description='Thumbnail of the file sent; can be ignored if thumbnail generation for the file is supported server-side. The thumbnail should be in JPEG format and less than 200 kB in size. A thumbnail‘s width and height should not exceed 320. Ignored if the file is not uploaded using multipart/form-data. Thumbnails can’t be reused and can be only uploaded as a new file, so you can pass "attach://<file_attach_name>" if the thumbnail was uploaded using multipart/form-data under <file_attach_name>. More info on Sending Files »'),
    disable_notification: Optional[bool] = Query(None, description='Sends the message silently. Users will receive a notification with no sound.'),
    reply_to_message_id: Optional[int] = Query(None, description='If the message is a reply, ID of the original message'),
    reply_markup: Optional[Json[Union['InlineKeyboardMarkupModel', 'ReplyKeyboardMarkupModel', 'ReplyKeyboardRemoveModel', 'ForceReplyModel']]] = Query(None, description='Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.'),
    request: Request = None,
) -> JSONableResponse:
    """
    Use this method to send audio files, if you want Telegram clients to display them in the music player. Your audio must be in the .MP3 or .M4A format. On success, the sent Message is returned. Bots can currently send audio files of up to 50 MB in size, this limit may be changed in the future.
    For sending voice messages, use the sendVoice method instead.

    https://core.telegram.org/bots/api#sendaudio
    """
    audio: Union[InputFileModel, str] = parse_obj_as(
        Union[InputFileModel, str],
        obj=audio,
    )
    thumb: Optional[Union[InputFileModel, str]] = parse_obj_as(
        Optional[Union[InputFileModel, str]],
        obj=thumb,
    )
    reply_markup: Optional[Union[InlineKeyboardMarkupModel, ReplyKeyboardMarkupModel, ReplyKeyboardRemoveModel, ForceReplyModel]] = parse_obj_as(
        Optional[Union[InlineKeyboardMarkupModel, ReplyKeyboardMarkupModel, ReplyKeyboardRemoveModel, ForceReplyModel]],
        obj=reply_markup,
    )

    # TODO: thumb

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

    file: Union[BytesIO, str] = await process_file(given_file=audio, request=request)
    if isinstance(file, JSONableResponse):
        # abort
        return file
    # end def

    buttons = await to_telethon(reply_markup, bot)

    attributes = []
    if duration or title or performer:
        attributes.append(
            DocumentAttributeAudio(
                duration=duration if duration else 0,
                title=title,
                performer=performer,
                waveform=None,
            )
        )
    # end if
    if isinstance(file, BytesIO):
        attributes.append(
            DocumentAttributeFilename(
                file_name=file.name
            )
        )
    # end if


    result = await bot.send_file(
        entity=entity,
        file=file,
        attributes=attributes,
        caption=caption,
        parse_mode=parse_mode,
        duration=duration,
        performer=performer,
        title=title,
        thumb=thumb,
        disable_notification=disable_notification,
        reply_to_message_id=reply_to_message_id,
        buttons=buttons,
    )
    data = await to_web_api(result, bot)
    return r_success(data.to_array())
# end def
