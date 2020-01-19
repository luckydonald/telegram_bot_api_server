#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Query
from luckydonaldUtils.logger import logging

__author__ = 'luckydonald'

from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import InputStickerSetShortName

from ....tools.responses import JSONableResponse, r_success
from ....constants import TOKEN_VALIDATION
from ....serializer import to_web_api

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if

routes = APIRouter()  # Basically a Blueprint


@routes.api_route('/{token}/getStickerSet', methods=['GET', 'POST'], tags=['official', 'sticker'])
async def get_sticker_set(
    token: str = TOKEN_VALIDATION,
    name: str = Query(..., description='Name of the sticker set'),
) -> JSONableResponse:
    """
    Use this method to get a sticker set. On success, a StickerSet object is returned.

    https://core.telegram.org/bots/api#getstickerset
    """
    from ....main import _get_bot
    bot = await _get_bot(token)

    result = await bot(GetStickerSetRequest(stickerset=InputStickerSetShortName(name)))
    data = await to_web_api(result, bot)
    return r_success(data.to_array())
# end def
