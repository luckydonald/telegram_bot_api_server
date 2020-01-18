#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Union, Optional
from fastapi import Query, APIRouter, HTTPException
from pydantic import Json
from luckydonaldUtils.logger import logging

__author__ = 'luckydonald'

from .....tools.responses import JSONableResponse, r_success
from .....constants import TOKEN_VALIDATION
from .....serializer import to_web_api, get_entity

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if

routes = APIRouter()  # Basically a Blueprint


@routes.api_route('/{token}/sendLocation', methods=['GET', 'POST'], tags=['official'])
async def send_location(
    token: str = TOKEN_VALIDATION,
    chat_id: Union[int, str] = Query(..., description='Unique identifier for the target chat or username of the target channel (in the format @channelusername)'),
    latitude: float = Query(..., description='Latitude of the location'),
    longitude: float = Query(..., description='Longitude of the location'),
    live_period: Optional[int] = Query(None, description='Period in seconds for which the location will be updated (see Live Locations, should be between 60 and 86400.'),
    disable_notification: Optional[bool] = Query(None, description='Sends the message silently. Users will receive a notification with no sound.'),
    reply_to_message_id: Optional[int] = Query(None, description='If the message is a reply, ID of the original message'),
    reply_markup: Json = Query(None, description='Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.'),
) -> JSONableResponse:
    """
    Use this method to send point on the map. On success, the sent Message is returned.

    https://core.telegram.org/bots/api#sendlocation
    """
    from .....main import _get_bot
    bot = await _get_bot(token)

    try:
        entity = await get_entity(bot, chat_id)
    except ValueError:
        raise HTTPException(404, detail="chat not found?")
    # end try

    result = await bot.send_location(
        entity=entity,
        latitude=latitude,
        longitude=longitude,
        live_period=live_period,
        disable_notification=disable_notification,
        reply_to_message_id=reply_to_message_id,
        reply_markup=reply_markup,
    )
    data = await to_web_api(result, bot)
    return r_success(data.to_array())
# end def
