#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Dict, Union
from aiocron import crontab
from asyncio import get_event_loop
from telethon import TelegramClient
from classes.webhook import TelegramClientWebhook, TelegramClientUpdates, TelegramClientUpdateCollector
from fastapi import FastAPI, APIRouter
from pydantic import AnyHttpUrl
from somewhere import TG_API_ID, TG_API_HASH
from starlette.responses import JSONResponse
from luckydonaldUtils.logger import logging
from pytgbot.api_types.receivable.peer import User


__author__ = 'luckydonald'

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG, date_formatter="%Y-%m-%d %H:%M:%S")
# end if

loop = get_event_loop()
loop.set_debug(True)

bots: Dict[str, Union[TelegramClientWebhook, TelegramClientWebhook, TelegramClient]]
bots: Dict[str, Union[TelegramClientWebhook, TelegramClientWebhook, TelegramClient]] = {
    # "token": TelegramClientWebhook('https://route/to/instance', ...),
}

app = FastAPI()
routes = APIRouter()  # like flask.Blueprint


@routes.get('/bot{token}/setWebhook')
async def set_webhook(token, url: Union[AnyHttpUrl, None] = None):
    global bots
    logger.debug(f'Setting webhook for {token} to {url!r}.')
    if not url:
        return await delete_webhook(token)
    # end if
    if token in bots:
        bot = bots[token]
        if isinstance(bot, TelegramClientWebhook):
            # easy case: we already have a webhook registered and only want to change the url.
            bots[token].webhook_url = url
            return r_success(True, "Webhook was updated")
        # end if -> else
        logger.debug(f'Removing old bot instance: {bot}')
        bot = bots[token]
        del bots[token]
        bot.disconnect()
        del bot
        del bots[token]
        # end if
    # end if

    try:
        logger.debug(f'Launching telegram webhook client for {token}.')
        bot = TelegramClientWebhook(
            session=token, api_id=TG_API_ID, api_hash=TG_API_HASH, api_key=token, webhook_url=url,
        )
        bot.parse_mode = 'html'  # <- Render things nicely
        logger.debug(f'Connecting in the bot {token}.')
        await bot.connect()
        logger.debug(f'Registering all the listeners for {token}.')
        bot.register_update_listeners()
        logger.debug(f'Signing in the bot {token}.')
        await bot.sign_in(bot_token=bot.api_key)
        logger.debug(f'Telegram client for {token} is signed in and ready to use.')
    except Exception as e:
        logger.warning('Registering bot failed', exc_info=True)
        return r_error(500, description=str(e))
    # end try
    bots[token] = bot
    logger.debug(f'Added {token} to the list: {bot!r}.')
    return r_success(True, "Webhook was set")
# end def


@routes.get('/bot{token}/deleteWebhook')
async def delete_webhook(token):
    global bots
    if token in bots:
        bot = bots[token]
        del bots[token]  # delete first to have it removed from the loop
        bot.disconnect()
        return r_success(True, "Webhook was deleted")
    # end if
    return r_success(True, "Webhook was not set")
# end def


@routes.get('/bot{token}/getUpdates')
async def get_updates(token):
    global bots
    logger.debug(f'Setting webhook for {token}...')

    if token in bots:
        bot = bots[token]
        if isinstance(bot, TelegramClientWebhook):
            logger.debug("using bot already registered as webhook")
            return r_error(409, "Conflict: can't use getUpdates method while webhook is active; use deleteWebhook to delete the webhook first")
        elif not isinstance(bot, TelegramClientUpdates):
            # we have an instance not listening for any updates.
            # -> close and delete
            logger.debug(f"using bot neither webhook nor get_updates, deleting bot {bot!r}.")
            del bots[token]
            bot.disconnect()
            del bot
        else:
            logger.debug("bot listening for getUpdates already found.")
        # end if
    # end if

    if token not in bots:
        try:
            logger.debug(f'Launching telegram client for {token}.')
            bot = TelegramClientUpdates(
                session=token, api_id=TG_API_ID, api_hash=TG_API_HASH, api_key=token,
            )
            bot.parse_mode = 'html'  # <- Render things nicely
            logger.debug(f'Connecting in the bot {token}.')
            await bot.connect()
            logger.debug(f'Registering all the listeners for {token}.')
            bot.register_update_listeners()
            logger.debug(f'Signing in the bot {token}.')
            await bot.sign_in(bot_token=bot.api_key)
            logger.debug(f'Telegram client for {token} is signed in and ready to use.')
        except Exception as e:
            logger.warning('Registering bot failed', exc_info=True)
            return r_error(500, description=str(e))
        # end try
        bots[token] = bot
        logger.debug(f'Telegram client for {token} is registered.')
    # end if

    # in any case we wanna return the updates
    return r_success([x.to_array() for x in bots[token].updates])
# end def


async def _get_bot(token: str) -> Union[TelegramClient, TelegramClientUpdates, TelegramClientWebhook]:
    global bots
    if token in bots:
        # easy mode: find existing
        return bots[token]
    # end if

    logger.debug(f'could not find bot for token {token},\nLaunching telegram muted client.')
    bot = TelegramClient(
        session=token, api_id=TG_API_ID, api_hash=TG_API_HASH,
    )
    bot.parse_mode = 'html'  # <- Render things nicely
    logger.debug(f'Connecting in the bot {token}.')
    await bot.connect()
    logger.debug(f'Signing in the bot {token}.')
    await bot.sign_in(bot_token=token)
    logger.debug(f'Telegram client for {token} is signed in and ready to use.')
    assert token not in bots
    bots[token] = bot
    return bot
# end def


@routes.get('/bot{token}/getMe')
async def get_me(request):
    result = User(
        id=133378542,
        is_bot=True,
        first_name="Test Bot i do tests with",
        username="test4458bot",
    ).to_array()
    return r_success(result, None)
# end def


@routes.get('/bot{token}/')
async def not_found(request):
    return r_error(404, "Not Found")
# end def


@crontab('* * * * * */10', start=True)
async def attime():
    logger.debug(f'current listeners: {bots!r}')
# end def


def r_error(error_code=500, description=None):
    return JSONResponse({
        "ok": False,
        "error_code": error_code,
        "description": description
    }, status_code=error_code)
# end def


def r_success(result, description=None, status_code=200):
    return JSONResponse({
        "ok": True,
        "result": result,
        "description": description,
    }, status_code=status_code)
# end def


app.include_router(routes)
from views.api.v4_4.sendable import routes as sendable_routes
app.include_router(sendable_routes)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
# end if
