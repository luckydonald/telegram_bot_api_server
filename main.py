#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Dict
from aiohttp import web
from asyncio import get_event_loop
from telethon import TelegramClient, events
from aiohttp_utils import flaskify_arguments
from aiohttp.web_request import Request
from luckydonaldUtils.logger import logging
from pytgbot.api_types.receivable.peer import User
from pytgbot.api_types.receivable.updates import Update

__author__ = 'luckydonald'

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if

loop = get_event_loop()
loop.set_debug(True)


class WebhookInfo(object):
    bot_instance: TelegramClient

    def __init__(self, url: str, bot_instance: TelegramClient):
        self.url = url
        self.bot_instance = bot_instance
    # end def
# end class


webhooks: Dict[str, WebhookInfo] = {
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
    if 'url' not in request.query or not request.query['url']:
        return await delete_webhook(token, request)
    # end if
    url: str = request.query['url']

    if token in webhooks:
        webhooks[token].url = url
        return r_success(True, "Webhook was updated")
    # end if
    try:
        bot = TelegramClient('bot', 11111, 'a1b2c3d4', loop=loop).start(bot_token=token)
    except Exception as e:
        return r_error(500, description=str(e))
    # end try

    webhooks[token] = WebhookInfo(url=url, bot_instance=bot)
    return r_success(True, "Webhook was set")
# end def


@routes.get('/bot{token}/deleteWebhook')
@flaskify_arguments
async def delete_webhook(token, request: Request):
    if 'url' in request.query and request.query['url']:
        return set_webhook(token, request)
    # end if

    if token in webhooks:
        del webhooks[token]
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
