#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio

import typing

import aiohttp
from luckydonaldUtils.exceptions import assert_type_or_raise
from luckydonaldUtils.logger import logging
from pytgbot.api_types.receivable.updates import Update, Message
from telethon import TelegramClient, events
from telethon.network import ConnectionTcpFull, Connection
from telethon.sessions import Session
from telethon.tl.types import TypeUpdate, UpdateChannelMessageViews

from serializer import to_web_api

__author__ = 'luckydonald'

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if


class TelegramClientWebhook(TelegramClient):
    api_key: str
    webhook_url: str
    """
    A TelegramClient which remember it's API_KEY and WEBHOOK
    """
    def __init__(
        self: 'TelegramClient',
        session: typing.Union[str, Session],
        api_id: int,
        api_hash: str,
        api_key: str,
        webhook_url: str,
        *,
        connection: typing.Type[Connection] = ConnectionTcpFull,
        use_ipv6: bool = False,
        proxy: typing.Union[tuple, dict] = None,
        timeout: int = 10,
        request_retries: int = 5,
        connection_retries: int = 5,
        retry_delay: int = 1,
        auto_reconnect: bool = True,
        sequential_updates: bool = False,
        flood_sleep_threshold: int = 60,
        device_model: str = None,
        system_version: str = None,
        app_version: str = None,
        lang_code: str = 'en',
        system_lang_code: str = 'en',
        loop: asyncio.AbstractEventLoop = None,
        base_logger: typing.Union[str, logging.Logger] = None
    ):
        super().__init__(
            session,
            api_id,
            api_hash,
            connection=connection,
            use_ipv6=use_ipv6,
            proxy=proxy,
            timeout=timeout,
            request_retries=request_retries,
            connection_retries=connection_retries,
            retry_delay=retry_delay,
            auto_reconnect=auto_reconnect,
            sequential_updates=sequential_updates,
            flood_sleep_threshold=flood_sleep_threshold,
            device_model=device_model,
            system_version=system_version,
            app_version=app_version,
            lang_code=lang_code,
            system_lang_code=system_lang_code,
            loop=loop,
            base_logger=base_logger
        )
        self.api_key = api_key
        self.webhook_url = webhook_url
    # end def

    async def send_event(self, data: Update):
        json = data.to_array()
        logger.debug(f"Sending event: {json!r}")
        return None
        async with aiohttp.ClientSession() as session:
            async with session.post(self.webhook_url, json=json) as response:
                logger.info("Response: " + repr(await response.text()))
            # end with
        # end with
    # end def

    def register_webhook_methods(self):
        @self.on(events.NewMessage(pattern='/start'))
        async def start(event):
            """Send a message when the command /start is issued."""
            await event.respond('Hi!')
            raise events.StopPropagation
        # end def

        @self.on(events.Raw)
        async def got_some_update(event: events.NewMessage):
            """Process incomming Updates."""
            logger.info(f'account {self.api_key!r} got message: {type(event)!r}')
            assert_type_or_raise(
                event,
                *TypeUpdate.__args__,
                parameter_name='event'
            )
            if isinstance(event, (UpdateChannelMessageViews,)):
                logger.info(f'Skipping Update type {type(event)}')
                return
            try:
                update: Update = await to_web_api(event)
            except TypeError as e:
                logger.exception('Serializing element failed')

                from datetime import datetime
                with open(f'update_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt', 'w') as f:
                    f.write(str(e))
                # end with

                # await event.respond()
                raise events.StopPropagation
            # end def

            from datetime import datetime
            import json
            with open(f'update_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.json', 'w') as f:
                json.dump(update.to_array(), f)
            # end with

            await self.send_event(update)
            # await event.respond()
            raise events.StopPropagation
        # end def
# end class
