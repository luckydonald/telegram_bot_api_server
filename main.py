#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Dict
from aiohttp import web
from aiocron import crontab
from asyncio import get_event_loop, create_task
from classes.webhook import TelegramClientWebhook
from somewhere import TG_API_ID, TG_API_HASH
from aiohttp_utils import flaskify_arguments
from aiohttp.web_request import Request
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
    # token: ('https://route/to/instance', bot),
}

routes = web.RouteTableDef()


async def handle(request: Request):
    name = request.match_info.get('name', "World!")
    text = "Hello, " + name
    print('received request, replying with "{}".'.format(text))
    return web.Response(text=text)
# end def


@routes.get('/bot{token}/setWebhook')
@flaskify_arguments
async def set_webhook(token, request: Request):
    global webhooks
    logger.debug(f'Setting webhook for {token}...')
    if 'url' not in request.query or not request.query['url']:
        return await delete_webhook(token, request)
    # end if
    url: str = request.query['url']
    logger.debug(f'Setting webhook for {token} to {url!r}.')

    if token in webhooks:
        webhooks[token].webhook_url = url
        return r_success(True, "Webhook was updated")
    # end if
    try:
        logger.debug(f'Launching telegram client for {token}.')
        bot = TelegramClientWebhook(
            session='bot', api_id=TG_API_ID, api_hash=TG_API_HASH, api_key=token, webhook_url=url,
        )
        bot.parse_mode = 'html'  # <- Render things nicely
        await bot.connect()
        bot.register_webhook_methods()
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
@flaskify_arguments
async def delete_webhook(token, request: Request):
    global webhooks
    if 'url' in request.query and request.query['url']:
        return set_webhook(token, request)
    # end if

    if token in webhooks:
        bot = webhooks[token]
        del webhooks[token]
        bot.disconnect()
        return r_success(True, "Webhook was deleted")
    # end if
    return r_success(True, "Webhook was not set")
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


app = web.Application()
app.router.add_routes(routes)
app.router.add_get('/', handle)
app.router.add_get('/{name:int}', handle)

if __name__ == '__main__':
    try:
        raise ImportError()
        from aiohttp_devtools.runserver import run_app, runserver, INFER_HOST
        run_app(*runserver(host=INFER_HOST, main_port=8080, debug_toolbar=True, verbose=True, livereload=True))
    except ImportError:
        try:
            import aiohttp_debugtoolbar
            # from aiohttp_debugtoolbar import toolbar_middleware_factory
            aiohttp_debugtoolbar.setup(app)
        except ImportError:
            pass
        # end try
        web.run_app(app, port=8080)
    # end iff
# end if
