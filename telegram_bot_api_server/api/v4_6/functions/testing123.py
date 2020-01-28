#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import List

from fastapi import APIRouter, Query
from fastapi.params import Path, Header
from luckydonaldUtils.logger import logging

__author__ = 'luckydonald'

from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import InputStickerSetShortName
# from pydantic import Json

# from ....tools.fastapi_issue_884_workaround import Json, parse_obj_as
from ....tools.responses import JSONableResponse, r_success
from ....constants import TOKEN_VALIDATION
from ....serializer import to_web_api, get_entity
from ....deserializer import to_telethon
from ..generated.models import *

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if

routes = APIRouter()  # Basically a Blueprint


from pydantic import BaseModel

class TestModel(BaseModel):
    name: str
    description: str
    price: float
    tax: float
# end class

from ....tools.fastapi_issue_884_workaround import Json


@routes.api_route('/testing', methods=['GET', 'POST'], tags=['debug', 'will_be_removed'])
async def test_func(
    foo: str,
    moop: Json[List['TestModel']] = Query(..., description='Name of the sticker set'),
    # reply_markup: Optional[Union[Json['InlineKeyboardMarkupModel'], Json['ReplyKeyboardMarkupModel'], Json['ReplyKeyboardRemoveModel'], Json['ForceReplyModel']]] = Query(None, description='Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.'),
) -> JSONableResponse:
    """
    Use this method to get a sticker set. On success, a StickerSet object is returned.

    https://core.telegram.org/bots/api#getstickerset
    """
    # model loading and verification

    return {'data': moop}
# end def


@routes.api_route('/test1', methods=['GET', 'POST'], tags=['official', 'message', 'send'])
async def test1(
    moop: Json[TestModel] = Query(..., description='Something something'),
    foo: str = Query(...),
):
    return {'woop': moop, 'lol': foo}
# end def


@routes.api_route('/test2/{moop}', methods=['GET', 'POST'], tags=['official', 'message', 'send'])
async def test2(
    moop: Json[TestModel] = Path(..., description='Something something'),
    foo: str = Query(...),
):
    return {'woop': moop, 'lol': foo}
# end def


@routes.api_route('/test3', methods=['GET', 'POST'], tags=['official', 'message', 'send'])
async def test3(
    moop: Json[TestModel] = Header(..., description='Something something'),
    foo: str = Query(...),
):
    return {'woop': moop, 'lol': foo}
# end def
