#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from luckydonaldUtils.logger import logging
from .views.api.v4_5.generated.models import *
from telethon import Button

__author__ = 'luckydonald'

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if


async def to_telethon(o, client):
    if isinstance(o, ReplyKeyboardMarkupModel):
        buttons = []
        for row in o.keyboard:
            buttons.append([])
            for button in row:
                buttons[-1].append(await to_telethon(button, client=client))
            # end for
        # end for
        return buttons
    if isinstance(o, InlineKeyboardButtonModel):
        if o.url:
            if o.text:
                return Button.url(text=o.text, url=o.url)
            # end if
            return Button.url(text=o.url, url=o.url)
        if o.login_url:
            assert isinstance(o.login_url, LoginUrlModel)
            return Button.auth(
                text=o.text, bot=o.login_url.bot_username,
                write_access=o.login_url.request_write_access,
                fwd_text=o.login_url.forward_text,
            )
        if o.callback_data:
            if o.text:
                return Button.inline(text=o.text, data=o.callback_data)
            # end if
            return Button.inline(text=o.callback_data, data=o.callback_data)
        if o.switch_inline_query:
            return Button.switch_inline(query=o.switch_inline_query, same_peer=False)
        if o.switch_inline_query_current_chat:
            return Button.switch_inline(query=o.switch_inline_query, same_peer=True)
        if o.callback_game:
            raise NotImplementedError('later, alligator')
        if o.pay:
            raise NotImplementedError('later, alligator')
    raise TypeError('Nope.')
# end def
