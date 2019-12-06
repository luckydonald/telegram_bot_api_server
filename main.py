#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from aiohttp import web
from aiohttp_utils import flaskify_arguments
from aiohttp.web_request import Request
from luckydonaldUtils.logger import logging

__author__ = 'luckydonald'

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if


routes = web.RouteTableDef()


async def handle(request: Request):
    name = request.match_info.get('name', "World!")
    text = "Hello, " + name
    print('received request, replying with "{}".'.format(text))
    return web.Response(text=text)
# end def


@routes.get('/test')
@routes.get('/test/{name}')
@flaskify_arguments
async def handle_post(name, request: Request):
    return web.Response(text=f'matches: {name}')
# end def


app = web.Application()
app.router.add_routes(routes)
app.router.add_get('/', handle)
app.router.add_get('/{name:int}', handle)

web.run_app(app, port=8080)
