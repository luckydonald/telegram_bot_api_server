#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter
from luckydonaldUtils.logger import logging

__author__ = 'luckydonald'

from ....tools.responses import JSONableResponse, r_success
from ....constants import TOKEN_VALIDATION
from ....serializer import to_web_api

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if

routes = APIRouter()  # Basically a Blueprint


@routes.api_route('/{token}/getMe', methods=['GET', 'POST'], tags=['official'])
async def get_me(
    token: str = TOKEN_VALIDATION,
) -> JSONableResponse:
    """
    A simple method for testing your bot's auth token. Requires no parameters. Returns basic information about the bot in form of a User object.

    https://core.telegram.org/bots/api#getme
    """

    from ....main import _get_bot
    bot = await _get_bot(token)

    result = await bot.get_me()
    data = await to_web_api(result, bot, get_me_user=True)
    return r_success(data.to_array())
# end def
