#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Dict, Union
from aiocron import crontab
from asyncio import get_event_loop
from classes.webhook import TelegramClientUpdateCollector, UpdateModes
from fastapi import FastAPI, APIRouter
from pydantic import AnyHttpUrl
from somewhere import TG_API_ID, TG_API_HASH
from telethon.utils import parse_phone
from telethon.errors import SessionPasswordNeededError, PhoneCodeExpiredError
from telethon.sessions import StringSession
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException
from luckydonaldUtils.logger import logging
from telethon.tl.functions.auth import SignInRequest
from pytgbot.api_types.receivable.peer import User


__author__ = 'luckydonald'

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG, date_formatter="%Y-%m-%d %H:%M:%S")
# end if

loop = get_event_loop()
loop.set_debug(True)

bots: Dict[str, TelegramClientUpdateCollector] = {
    # "token": TelegramClientUpdateCollector('https://route/to/instance', ...),
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
        bot: TelegramClientUpdateCollector = bots[token]
        if bot.mode == UpdateModes.WEBHOOK:
            # easy case: we already have a webhook registered and only want to change the url.
            bots[token].webhook_url = url
            return r_success(True, "Webhook was updated")
        # end if -> else
        logger.debug(f'Changing old bot instance: {bot}')
        bot.enable_webhook(url)
        return r_success(True, "Webhook was not set before")
        # end if
    # end if

    try:
        logger.debug(f'Launching telegram webhook client for {token}.')
        bot = TelegramClientUpdateCollector(
            session=token, api_id=TG_API_ID, api_hash=TG_API_HASH, api_key=token,
            webhook_url=url, mode=UpdateModes.WEBHOOK,
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


@routes.get('/authorize')
@routes.post('/authorize')
async def authorize_phone(
    phone: str,
    password: Union[None, str] = None,
    bot_token: Union[None, str] = None,
    force_sms: bool = False,
    code: Union[None, str] = None,
    phone_code_hash: Union[None, str] = None,
    session: Union[None, str] = None,
):
    logger.info(f"Args: phone={phone}, password={password}, bot_token={bot_token}, force_sms={force_sms}, code={code}.")
    me = None
    bot = TelegramClientUpdateCollector(
        session=StringSession(session), api_id=TG_API_ID, api_hash=TG_API_HASH,
        mode=UpdateModes.SILENT,
    )
    if not bot.is_connected():
        await bot.connect()
    # end if

    if not bot_token:
        # Turn the callable into a valid phone number (or bot token)
        phone = parse_phone(phone)
    else:
        await bot.sign_in(bot_token=bot_token)
        return bot
    # end try

    logger.info(f'Phone Number: {phone}')
    if not code:
        logger.info('Sending code request.')
        sent_code = await bot.send_code_request(phone, force_sms=force_sms)
        logger.info(f'sent_code: {sent_code}')
        # sign_up = not sent_code.phone_registered
        logger.warning(
            "Needs code now!\n"
            "Please provide via '$TELEGRAM_LOGGER_PHONE_LOGIN_CODE' environment variable.\n"
            f"Also set '$TELEGRAM_LOGGER_PHONE_LOGIN_HASH={sent_code.phone_code_hash}'."
        )
        session_str = bot.session.save()
        # noinspection PyTypeChecker
        raise HTTPException(502, detail={
            'message': 'LOGIN FAILED: Please provide your code sent to you',
            'reason': 'code',
            'data': {'phone_code_hash': sent_code.phone_code_hash, 'code': None, 'password': None, 'session': session_str}
        })
    else:
        logger.info('Signing in.')
        try:
            # me = await self.sign_in(phone, code=code, phone_code_hash=phone_code_hash)
            result = await bot(SignInRequest(phone, phone_code_hash, str(code)))
            logger.warning(f"Sign in result: {result}")
            me = bot._on_login(result.user)
        except PhoneCodeExpiredError:
            session_str = bot.session.save()
            raise HTTPException(502, detail={
                'message': 'LOGIN FAILED: Please provide your code sent to you',
                'reason': 'code_expired',
                'data': {'phone_code_hash': phone_code_hash, 'code': None, 'password': None, 'session': session_str}
            })
        except SessionPasswordNeededError:
            if not password:
                txt = "Two-step verification is enabled for this account. Please provide the 'TELEGRAM_LOGGER_PHONE_LOGIN_CODE' environment variable."
                session_str = bot.session.save()
                logger.error(txt)
                raise HTTPException(502, detail={
                    'message': 'LOGIN FAILED: Please provide your two factor login (2FA) password you personally set',
                    'reason': 'two_factor_password_needed',
                    'data': {'phone_code_hash': phone_code_hash, 'code': code, 'password': None, 'session': session_str}
                })
            # end if
            me = await bot.sign_in(phone=phone, password=password, phone_code_hash=phone_code_hash)
        except Exception as e:
            logger.exception('sign in didn\'t work')
            raise e
        # end try
        if not me:
            me = await bot.get_me()
        # end if
        assert await bot.is_user_authorized(), "should be authorized now."
        secret = bot.session.save()
        user_token = f'{me.id!s}@{secret}'
        # noinspection PyTypeChecker
        raise HTTPException(200, detail={'message': 'success', 'user_token': user_token})
    # end if
# end def


@routes.get('/bot{token}/getUpdates')
async def get_updates(token):
    global bots
    logger.debug(f'Setting webhook for {token}...')

    if token in bots:
        bot: TelegramClientUpdateCollector = bots[token]
        if bot.mode == UpdateModes.WEBHOOK:
            logger.debug("using bot already registered as webhook")
            return r_error(409, "Conflict: can't use getUpdates method while webhook is active; use deleteWebhook to delete the webhook first")
        elif bot.mode != UpdateModes.POLLING:
            # we have an instance not listening for any updates.
            # -> close and delete
            logger.debug(f"using bot neither webhook nor polling, but is in mode {bot.mode!r}. Now forcing polling mode.")
            bot.enable_polling()
        else:
            logger.debug("bot listening for getUpdates already found.")
        # end if
    # end if

    if token not in bots:
        try:
            logger.debug(f'Launching telegram client for {token}.')
            bot = TelegramClientUpdateCollector(
                session=token, api_id=TG_API_ID, api_hash=TG_API_HASH, api_key=token,
                mode=UpdateModes.POLLING,
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


async def _get_bot(token: str) -> Union[TelegramClientUpdateCollector]:
    global bots
    if token in bots:
        # easy mode: find existing
        return bots[token]
    # end if

    logger.debug(f'could not find bot for token {token},\nLaunching telegram muted client.')
    bot = TelegramClientUpdateCollector(
        session=token, api_id=TG_API_ID, api_hash=TG_API_HASH, api_key=token,
        mode=UpdateModes.SILENT,
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
