#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Union, Any, List

from fastapi.params import Path, Query
from luckydonaldUtils.logger import logging
from fastapi import APIRouter as Blueprint

__author__ = 'luckydonald'

from serializer import to_web_api, get_entity

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if


routes = Blueprint()  # Basically a Blueprint


@routes.api_route('/{token}/sendMessage', methods=["GET", "POST"])
async def send_message(
    token: str = Path(..., description="the bot's unique authentication token", min_length=1),
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
    from main import r_success
    data = await to_web_api(msg, bot)
    return r_success(data.to_array())
# end def
