#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Dict, Union
from aiohttp import web
from aiocron import crontab
from asyncio import get_event_loop
from classes.webhook import TelegramClientWebhook, TelegramClientUpdates, TelegramClientUpdateCollector
from fastapi import FastAPI, APIRouter
from pydantic import AnyHttpUrl
from somewhere import TG_API_ID, TG_API_HASH
from luckydonaldUtils.logger import logging
from pytgbot.api_types.receivable.peer import User


__author__ = 'luckydonald'

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG, date_formatter="%Y-%m-%d %H:%M:%S")
# end if

loop = get_event_loop()
loop.set_debug(True)

webhooks: Dict[str, TelegramClientWebhook]
webhooks: Dict[str, TelegramClientWebhook] = {
    # "token": TelegramClientWebhook('https://route/to/instance', ...),
}

updates: Dict[str, TelegramClientUpdates]
updates: Dict[str, TelegramClientUpdates] = {
    # "token": TelegramClientUpdates(...),
}

app = FastAPI()
routes = APIRouter()  # like flask.Blueprint


@routes.get('/bot{token}/setWebhook')
async def set_webhook(token, url: Union[AnyHttpUrl, None] = None):
    global updates
    global webhooks
    logger.debug(f'Setting webhook for {token}...')
    if not url:
        return await delete_webhook(token)
    # end if
    logger.debug(f'Setting webhook for {token} to {url!r}.')

    if token in webhooks:
        webhooks[token].webhook_url = url
        return r_success(True, "Webhook was updated")
    # end if
    if token in updates:
        logger.debug('Removing getUpdates hook')
        bot = updates[token]
        del updates[token]
        bot.disconnect()
        del bot
        del updates[token]
    # end if
    try:
        logger.debug(f'Launching telegram client for {token}.')
        bot = TelegramClientWebhook(
            session=token, api_id=TG_API_ID, api_hash=TG_API_HASH, api_key=token, webhook_url=url,
        )
        bot.parse_mode = 'html'  # <- Render things nicely
        await bot.connect()
        bot.register_update_listeners()
        await bot.sign_in(bot_token=bot.api_key)
        logger.debug(f'Telegram client for {token} is enqueued.')

        logger.debug(f'Done registering all the listeners for {token}.')
    except Exception as e:
        logger.warning('Registering bot failed', exc_info=True)
        return r_error(500, description=str(e))
    # end try

    webhooks[token] = bot
    logger.debug(f'Added {token} to the list: {bot!r}.')
    return r_success(True, "Webhook was set")
# end def


@routes.get('/bot{token}/deleteWebhook')
async def delete_webhook(token):
    global webhooks
    if token in webhooks:
        bot = webhooks[token]
        del webhooks[token]
        bot.disconnect()
        return r_success(True, "Webhook was deleted")
    # end if
    return r_success(True, "Webhook was not set")
# end def


@routes.get('/bot{token}/getUpdates')
async def get_updates(token):
    global updates
    logger.debug(f'Setting webhook for {token}...')

    if token not in updates:
        if token in webhooks:
            return r_error(409, "Conflict: can't use getUpdates method while webhook is active; use deleteWebhook to delete the webhook first")
        # end if
        try:
            logger.debug(f'Launching telegram client for {token}.')
            bot = TelegramClientUpdates(
                session=token, api_id=TG_API_ID, api_hash=TG_API_HASH, api_key=token,
            )
            bot.parse_mode = 'html'  # <- Render things nicely
            await bot.connect()
            bot.register_update_listeners()
            await bot.sign_in(bot_token=bot.api_key)
            logger.debug(f'Done registering all the listeners for {token}.')
        except Exception as e:
            logger.warning('Registering bot failed', exc_info=True)
            return r_error(500, description=str(e))
        # end try
        updates[token] = bot
        logger.debug(f'Telegram client for {token} is registered.')
    # end if

    # in any case we wanna return the updates
    return r_success([x.to_array() for x in updates[token].updates])
# end def


def _get_bot(token: str) -> TelegramClientUpdateCollector:
    if token in webhooks:
        return webhooks[token]
    # end if
    if token in updates:
        return updates[token]
    # end if
    if token in bots:


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
    logger.debug(f'current listeners: {webhooks!r}')
# end def


def r_error(error_code=500, description=None):
    return web.json_response({
        "ok": False,
        "error_code": error_code,
        "description": description
    }, status=error_code)
# end def


def r_success(result, description=None, status_code=200):
    return web.json_response({
        "ok": True,
        "result": result,
        "description": description,
    }, status=status_code)


app.include_router(routes)
# from views.api.v4_4.sendable import routes as sendable_routes
# app.include_router(sendable_routes)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
# end if
