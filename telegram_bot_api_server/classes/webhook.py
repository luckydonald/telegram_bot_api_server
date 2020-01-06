#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio

from abc import abstractmethod
from enum import Enum
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


class UpdateModes(Enum):
    """ Possible modes of operation for a TelegramClientUpdateCollector. """
    WEBHOOK = "webhook"  # does call an url with the updates received
    POLLING = "polling"  # stores the updates received for later retrieval
    SILENT = "silent"  # discards updates.
# end class


class TelegramClientUpdateCollector(TelegramClient):
    """
    A TelegramClient which remember it's API_KEY and depending on `mode` it
    - sends the updates to the stored `webhook_url`
    - stores it in the `updates` list for retrial later
    - does not listen for updates (sending only)
    """

    api_key: str
    mode: UpdateModes
    update_id: int
    webhook_url: Union[str, None]
    updates: List[Update] = []

    def __init__(
        self: 'TelegramClientUpdateCollector',
        session: Union[str, Session],
        # our custom parameters
        api_id: int,
        api_hash: str,
        mode: UpdateModes,
        api_key: Union[str, None] = None,
        webhook_url: Union[str, None] = None,
        parse_mode: Union[str, None] = "html",  # <- Render things nicely
        # now the Telethon parameters
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
        self.parse_mode = parse_mode
        self.mode = mode
        self.update_id = self.create_random_update_id()
        self.webhook_url = webhook_url
    # end def

    @staticmethod
    def create_random_update_id():
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
        logger.debug(f"Processing event: {json!r}")
        if self.mode == UpdateModes.POLLING:
            # Store the updates
            logger.debug('storing event.')
            self.updates.append(data)
        elif self.mode == UpdateModes.WEBHOOK:
            # Send the updates
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=json) as response:
                    logger.info("Response: " + repr(await response.text()))
                # end with
            # end with
        elif self.mode == UpdateModes.SILENT:
            # Ignore the updates
            logger.debug('silently ignoring update.')
        else:
            raise AssertionError(f'self.mode ({self.mode!r}) is unknown.')
        # end if
    # end def

    def register_update_listeners(self):
        @self.on(events.NewMessage(pattern='/start'))
        async def start(event):
            """Send a message when the command /start is issued."""
            await event.respond('Hi from <u><b>tgbotapi_server</b></u>!')
            # raise events.StopPropagation  # don't raise that as we wanna have others chime in as well
        # end def

        @self.on(events.NewMessage(pattern='/bestpony'))
        async def start(event):
            """Send a message when the command /start is issued."""
            await event.respond('Best pony is <b>Littlepip</b>!')
            # raise events.StopPropagation  # don't raise that as we wanna have others chime in as well
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

    def enable_webhook(self, url):
        self.url = url
        self.mode = UpdateModes.WEBHOOK
    # end def

    def enable_polling(self):
        self.updates = []
        self.mode = UpdateModes.POLLING
    # end def

    def enable_silent(self):
        self.mode = UpdateModes.SILENT
# end class