#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Union, Any, List

from fastapi.params import Path, Query
from luckydonaldUtils.logger import logging
from fastapi import APIRouter as Blueprint

__author__ = 'luckydonald'

from pydantic import Field

from serializer import to_web_api

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if


routes = Blueprint()  # Basically a Blueprint

@routes.api_route('/bot{token}/sendMessage', methods=["GET", "POST", "DELETE"])
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
    msg = await bot.send_message(
        entity=chat_id,
        message=text,
        parse_mode=parse_mode,
        link_preview=not disable_web_page_preview,
        silent=disable_notification,
        reply_to=reply_to_message_id,
        buttons=reply_markup,
    )
    from main import r_success
    """
    {
      "ok": true,
      "result": {
        "message_id": 217,
        "from": {
          "id": 133378542,
          "is_bot": true,
          "first_name": "Test Bot i do tests with",
          "username": "test4458bot"
        },
        "chat": {
          "id": -1001443587969,
          "title": "Derp [test] rename",
          "type": "supergroup"
        },
        "date": 1578018257,
        "text": "test"
      }
    }
    """
    data = await to_web_api(msg, bot)
    return r_success(data.to_array())
# end def
