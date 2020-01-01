#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio

import typing
from random import randint
from typing import Type, Union, List

import aiohttp
from luckydonaldUtils.exceptions import assert_type_or_raise
from luckydonaldUtils.logger import logging
from pytgbot.api_types.receivable.updates import Update, Message
from telethon import TelegramClient, events
from telethon.network import ConnectionTcpFull, Connection
from telethon.sessions import Session
from telethon.tl.types import TypeUpdate, UpdateChannelMessageViews, UpdateChannel

from serializer import to_web_api

__author__ = 'luckydonald'

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if


class TelegramClientWebhook(TelegramClient):
    """
    A TelegramClient which remember it's API_KEY and WEBHOOK
    """

    api_key: str
    webhook_url: str
    update_id: int

    def __init__(
        self: 'TelegramClient',
        session: Union[str, Session],
        api_id: int,
        api_hash: str,
        api_key: str,
        webhook_url: str,
        *,
        connection: Type[Connection] = ConnectionTcpFull,
        use_ipv6: bool = False,
        proxy: Union[tuple, dict] = None,
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
        base_logger: Union[str, logging.Logger] = None
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
        self.update_id = self.create_random_update_id()
    # end def

    def create_random_update_id(self):
        """
        Reset the update id.

        Update identifiers start from a certain positive number and increase sequentially.
        If there are no new updates for at least a week, then identifier of the next update
        will be chosen randomly instead of sequentially.
        :return:
        """
        return randint(0, 2147483647)
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
            # raise events.StopPropagation
        # end def

        @self.on(events.Raw)
        async def got_some_update(event: events.NewMessage):
            """Process incomming Updates."""
            logger.info(f'account {self.api_key!r} got message: {event!s}')
            if isinstance(event, (UpdateChannelMessageViews, UpdateChannel)):
                logger.info(f'Skipping Update type {type(event)}')
                return
            # end if
            from datetime import datetime
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            with open(f'logs/update_{now}.py', 'w') as f:
                f.write('from telethon.tl.types import *\nfrom telethon.tl.patched import *\nimport datetime\n\n')
                f.write(str(event))
            # end with
            assert_type_or_raise(
                event,
                *TypeUpdate.__args__,
                parameter_name='event'
            )
            try:
                update: Update = await to_web_api(event, client=self)  # provide the client so we can lookup chats and users.
            except TypeError as e:
                logger.exception('Serializing element failed')

                with open(f'logs/update_{now    }.txt', 'w') as f:
                    f.write(str(e))
                # end with

                # await event.respond()
                raise events.StopPropagation
            # end def

            from datetime import datetime
            import json
            with open(f'logs/update_{now}.json', 'w') as f:
                json.dump(update.to_array(), f)
            # end with

            await self.send_event(update)
            # await event.respond()

            self.update_id += 1
            if self.update_id > 2147483647:
                self.update_id = self.create_random_update_id()
            # end if
            raise events.StopPropagation
        # end def
    # end def
# end class
