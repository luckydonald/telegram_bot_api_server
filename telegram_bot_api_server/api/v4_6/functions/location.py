#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Union, Optional
from fastapi import Query, APIRouter, HTTPException
from luckydonaldUtils.logger import logging
from telethon.errors import BotMethodInvalidError

from telethon.tl.types import (
    InputMediaGeoPoint as TInputMediaGeoPoint,
    InputGeoPoint as TInputGeoPoint,
    InputMediaGeoLive as TInputMediaGeoLive,
    InputGeoPointEmpty as TInputGeoPointEmpty,
    InputMediaVenue as TInputMediaVenue,
)

__author__ = 'luckydonald'

from ....tools.fastapi_issue_884_workaround import Json, parse_obj_as
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


@routes.api_route('/{token}/sendLocation', methods=['GET', 'POST'], tags=['official', 'send', 'location'])
async def send_location(
    token: str = TOKEN_VALIDATION,
    chat_id: Union[int, str] = Query(..., description='Unique identifier for the target chat or username of the target channel (in the format @channelusername)'),
    latitude: float = Query(..., description='Latitude of the location', gt=-90, lt=90),
    longitude: float = Query(..., description='Longitude of the location', gt=-180, lt=180),
    live_period: Optional[int] = Query(None, description='Period in seconds for which the location will be updated (see Live Locations, should be between 60 and 86400.', gt=60, le=86400),
    disable_notification: Optional[bool] = Query(None, description='Sends the message silently. Users will receive a notification with no sound.'),
    reply_to_message_id: Optional[int] = Query(None, description='If the message is a reply, ID of the original message'),
    reply_markup: Optional[Json[InlineKeyboardMarkupModel]] = Query(None, description='Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.'),
) -> JSONableResponse:
    """
    Use this method to send point on the map. On success, the sent Message is returned.

    https://core.telegram.org/bots/api#sendlocation
    """
    # dict -> models
    reply_markup: Optional[Union[
        InlineKeyboardMarkupModel, ReplyKeyboardMarkupModel, ReplyKeyboardRemoveModel, ForceReplyModel]] = parse_obj_as(
        Optional[Union[InlineKeyboardMarkupModel, ReplyKeyboardMarkupModel, ReplyKeyboardRemoveModel, ForceReplyModel]],
        obj=reply_markup,
    )

    # get client
    from ....main import _get_bot
    bot = await _get_bot(token)

    # models -> bot
    buttons = await to_telethon(reply_markup, bot)

    try:
        entity = await get_entity(bot, chat_id)
    except BotMethodInvalidError:
        assert isinstance(chat_id, int) or (isinstance(chat_id, str) and len(chat_id) > 0 and chat_id[0] == '@')
        entity = chat_id
    except ValueError:
        raise HTTPException(404, detail="chat not found?")
    # end try

    # https://t.me/TelethonChat/33530
    if live_period:
        # end live location
        file = TInputMediaGeoLive(
            geo_point=TInputGeoPoint(
                lat=latitude,
                long=longitude,
            ),
            period=live_period,
        )
    else:
        # send normal location
        file = TInputMediaGeoPoint(
            geo_point=TInputGeoPoint(
                lat=latitude,
                long=longitude,
            )
        )
    # end if
    # noinspection PyTypeChecker
    result = await bot.send_file(
        entity=entity,
        file=file,
        silent=disable_notification,
        reply_to=reply_to_message_id,
        buttons=buttons,
    )
    data = await to_web_api(result, bot)
    return r_success(data.to_array())
# end def


@routes.api_route('/{token}/editMessageLiveLocation', methods=['GET', 'POST'], tags=['official', 'edit', 'location'])
async def edit_message_live_location(
    token: str = TOKEN_VALIDATION,
    latitude: float = Query(..., description='Latitude of new location', gt=-90, lt=90),
    longitude: float = Query(..., description='Longitude of new location', gt=-180, lt=180),
    chat_id: Optional[Union[int, str]] = Query(None, description='Required if inline_message_id is not specified. Unique identifier for the target chat or username of the target channel (in the format @channelusername)'),
    message_id: Optional[int] = Query(None, description='Required if inline_message_id is not specified. Identifier of the message to edit'),
    inline_message_id: Optional[str] = Query(None, description='Required if chat_id and message_id are not specified. Identifier of the inline message'),
    reply_markup: Optional[Json[InlineKeyboardMarkupModel]] = Query(None, description='A JSON-serialized object for a new inline keyboard.'),
) -> JSONableResponse:
    """
    Use this method to edit live location messages. A location can be edited until its live_period expires or editing is explicitly disabled by a call to stopMessageLiveLocation. On success, if the edited message was sent by the bot, the edited Message is returned, otherwise True is returned.

    https://core.telegram.org/bots/api#editmessagelivelocation
    """
    if inline_message_id:
        raise NotImplementedError('later, probably.')
    # end if

    reply_markup: Optional[InlineKeyboardMarkupModel] = parse_obj_as(
        Optional[InlineKeyboardMarkupModel],
        obj=reply_markup,
    )
    # models -> bot
    buttons = await to_telethon(reply_markup, None)

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

    # https://t.me/TelethonChat/33562

    # noinspection PyTypeChecker
    result = await bot.edit_message(
        file=TInputMediaGeoLive(
            geo_point=TInputGeoPoint(
                lat=latitude,
                long=longitude,
            ),
        ),
        entity=entity,
        message=message_id,
        buttons=buttons,
    )
    data = await to_web_api(result, bot)
    return r_success(data.to_array())
# end def


@routes.api_route('/{token}/stopMessageLiveLocation', methods=['GET', 'POST'], tags=['official', 'edit', 'location'])
async def stop_message_live_location(
    token: str = TOKEN_VALIDATION,
    chat_id: Optional[Union[int, str]] = Query(None, description='Required if inline_message_id is not specified. Unique identifier for the target chat or username of the target channel (in the format @channelusername)'),
    message_id: Optional[int] = Query(None, description='Required if inline_message_id is not specified. Identifier of the message with live location to stop'),
    inline_message_id: Optional[str] = Query(None, description='Required if chat_id and message_id are not specified. Identifier of the inline message'),
    reply_markup: Optional[Json['InlineKeyboardMarkupModel']] = Query(None, description='A JSON-serialized object for a new inline keyboard.'),
) -> JSONableResponse:
    """
    Use this method to stop updating a live location message before live_period expires. On success, if the message was sent by the bot, the sent Message is returned, otherwise True is returned.

    https://core.telegram.org/bots/api#stopmessagelivelocation
    """
    if inline_message_id:
        raise NotImplementedError('later, probably.')
    # end if

    reply_markup: Optional[InlineKeyboardMarkupModel] = parse_obj_as(
        Optional[InlineKeyboardMarkupModel],
        obj=reply_markup,
    )
    # models -> bot
    buttons = await to_telethon(reply_markup, None)

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

    # noinspection PyTypeChecker
    result = await bot.edit_message(
        file=TInputMediaGeoLive(
            geo_point=TInputGeoPointEmpty(),
            stopped=True,
            period=0,
        ),
        entity=entity,
        message=message_id,
        buttons=buttons,
    )
    data = await to_web_api(result, bot)
    return r_success(data.to_array())
# end def


@routes.api_route('/{token}/sendVenue', methods=['GET', 'POST'], tags=['official', 'send', 'location'])
async def send_venue(
    token: str = TOKEN_VALIDATION,
    chat_id: Union[int, str] = Query(..., description='Unique identifier for the target chat or username of the target channel (in the format @channelusername)'),
    latitude: float = Query(..., description='Latitude of the venue'),
    longitude: float = Query(..., description='Longitude of the venue'),
    title: str = Query(..., description='Name of the venue'),
    address: str = Query(..., description='Address of the venue'),
    foursquare_id: Optional[str] = Query(None, description='Foursquare identifier of the venue'),
    foursquare_type: Optional[str] = Query(None, description='Foursquare type of the venue, if known. (For example, "arts_entertainment/default", "arts_entertainment/aquarium" or "food/icecream".)'),
    disable_notification: Optional[bool] = Query(None, description='Sends the message silently. Users will receive a notification with no sound.'),
    reply_to_message_id: Optional[int] = Query(None, description='If the message is a reply, ID of the original message'),
    reply_markup: Optional[Json[Union['InlineKeyboardMarkupModel', 'ReplyKeyboardMarkupModel', 'ReplyKeyboardRemoveModel', 'ForceReplyModel']]] = Query(None, description='Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.'),
) -> JSONableResponse:
    """
    Use this method to send information about a venue. On success, the sent Message is returned.

    https://core.telegram.org/bots/api#sendvenue
    """
    reply_markup: Optional[InlineKeyboardMarkupModel] = parse_obj_as(
        Optional[InlineKeyboardMarkupModel],
        obj=reply_markup,
    )

    # models -> bot
    buttons = await to_telethon(reply_markup, None)

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

    file = TInputMediaVenue(
        geo_point=TInputGeoPoint(
            lat=latitude,
            long=longitude,
        ),
        title=title,
        address=address,
        provider='foursquare' if foursquare_id or foursquare_type else '',
        venue_id=foursquare_id if foursquare_id else '',
        venue_type=foursquare_type if foursquare_type else '',
    )

    # noinspection PyTypeChecker
    result = await bot.send_file(
        entity=entity,
        file=file,
        silent=disable_notification,
        reply_to=reply_to_message_id,
        buttons=buttons,
    )

    data = await to_web_api(result, bot)
    return r_success(data.to_array())
# end def
