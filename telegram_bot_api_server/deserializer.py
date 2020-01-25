#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from luckydonaldUtils.logger import logging
from telethon.tl.custom import Button

from .api.v4_6.generated.models import *

__author__ = 'luckydonald'

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if


async def to_telethon(o, client, markup: ReplyKeyboardMarkupModel = None):
    """
    :type  markup: ReplyKeyboardMarkupModel
    :param markup: `KeyboardButtonModel`s need access to `resize_keyboard`, `one_time_keyboard` and `selective`.
    """
    if isinstance(o, ReplyKeyboardMarkupModel):
        buttons = []
        for row in o.keyboard:
            buttons.append([])
            for button in row:
                buttons[-1].append(await to_telethon(button, client=client, markup=o))
            # end for
        # end for
        return buttons
    if isinstance(o, InlineKeyboardMarkupModel):
        buttons = []
        for row in o.inline_keyboard:
            buttons.append([])
            for button in row:
                if isinstance(button, dict):
                    button = InlineKeyboardButtonModel.parse_obj(button)
                # end if
                buttons[-1].append(await to_telethon(button, client=client))
            # end for
        # end for
        return buttons
    if isinstance(o, KeyboardButtonModel):
        assert o.text
        assert markup
        if o.request_poll:
            assert isinstance(o.request_poll, KeyboardButtonPollTypeModel)
            return Button.request_poll(
                text=o.text,
                force_quiz=o.request_poll.type == 'quiz',
                resize=markup.resize_keyboard,
                single_use=markup.one_time_keyboard,
                selective=markup.selective,
            )
        # end if
        if o.request_contact:
            assert o.text
            assert markup
            return Button.request_phone(
                o.text,
                resize=markup.resize_keyboard,
                single_use=markup.one_time_keyboard,
                selective=markup.selective,
            )
        # end if
        if o.request_location:
            assert o.text
            assert markup
            return Button.request_location(
                o.text,
                resize=markup.resize_keyboard,
                single_use=markup.one_time_keyboard,
                selective=markup.selective,
            )
        # end if
        raise TypeError(f'KeyboardButtonModel not handled: {type(o)} with value {o!r}: {o!s}')
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
    if o is None:
        return None
    raise TypeError(f'Type not handled: {type(o)} with value {o!r}: {o!s}')
# end def
