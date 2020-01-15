#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import uvloop
from enum import Enum
from typing import Dict, Union
from aiocron import crontab
from asyncio import get_event_loop
from fastapi import FastAPI, APIRouter
from pydantic import AnyHttpUrl, BaseModel
from starlette import status
from serializer import to_web_api
from telethon.utils import parse_phone
from classes.webhook import TelegramClientUpdateCollector, UpdateModes
from telethon.errors import SessionPasswordNeededError, PhoneCodeExpiredError
from fastapi.encoders import jsonable_encoder
from telethon.tl.types import User
from telethon.sessions import StringSession
from starlette.requests import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from luckydonaldUtils.logger import logging
from telethon.tl.functions.auth import SignInRequest
from pytgbot.api_types.receivable.peer import User as TGUser

from .tools.responses import r_error, r_success, JSONableResponse
from .constants import TOKEN_VALIDATION

from somewhere import TG_API_ID, TG_API_HASH


__author__ = 'luckydonald'

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG, date_formatter="%Y-%m-%d %H:%M:%S")
# end if

loop = get_event_loop()
loop.set_debug(True)

bots: Dict[int, TelegramClientUpdateCollector] = {
    # "token": TelegramClientUpdateCollector('https://route/to/instance', ...),
}

app = FastAPI()
routes = APIRouter()  # like flask.Blueprint


@routes.get('/{token}/setWebhook', tags=["webhook", "updates"])
async def set_webhook(token: str = TOKEN_VALIDATION, url: Union[AnyHttpUrl, None] = None) -> JSONableResponse:
    global bots
    logger.debug(f'Setting webhook for {token} to {url!r}.')
    if not url:
        return await delete_webhook(token)
    # end if
    is_api, user_id, secret = split_token(token)
    if user_id in bots:
        bot: TelegramClientUpdateCollector = bots[user_id]
        if bot.mode == UpdateModes.WEBHOOK:
            # easy case: we already have a webhook registered and only want to change the url.
            bots[user_id].webhook_url = url
            return r_success(True, "Webhook was updated")
        # end if -> else
        logger.debug(f'Changing old bot instance: {bot}')
        bot.enable_webhook(url)
        return r_success(True, "Webhook was not set before")
    # end if

    try:
        logger.debug(f'Launching telegram webhook client for {user_id}.')
        bot = await _get_bot(token)
        logger.debug(f'Registering all the listeners for {user_id}.')
        bot.register_update_listeners()
        logger.debug(f'Telegram client for {user_id} is now ready to use.')
    except Exception as e:
        logger.warning('Registering bot failed', exc_info=True)
        return r_error(500, description=str(e))
    # end try
    bots[user_id] = bot
    logger.debug(f'Added {user_id} to the list: {bot!r}.')
    return r_success(True, "Webhook was set")
# end def


@routes.get('/{token}/deleteWebhook', tags=["webhook", "updates"])
async def delete_webhook(token: str = TOKEN_VALIDATION):
    global bots
    is_api, user_id, secret = split_token(token)
    if user_id in bots:
        bot = bots[user_id]
        bot.mode = UpdateModes.POLLING
        return r_success(True, "Webhook was deleted")
    # end if
    return r_success(True, "Webhook was not set")
# end def


class PhoneAuthorisationData(BaseModel):
    token: Union[None, str]
    phone_code_hash: Union[None, str]
    code: Union[None, str]
    password: Union[None, str]
    session: Union[None, str]
# end def


class PhoneAuthorisationReasons(Enum):
    SUCCESS_BOT = 'success_bot'
    SUCCESS_PHONE = 'success_phone'
    CODE_NEEDED = 'code_needed'
    CODE_EXPIRED = 'code_expired'
    TWO_FACTOR_PASSWORD_NEEDED = 'two_factor_password_needed'
# end class


class PhoneAuthorisation(BaseModel):
    message: str
    reason: PhoneAuthorisationReasons
    data: PhoneAuthorisationData
# end def


@routes.get('/authorizePhone', response_model=PhoneAuthorisation, tags=["authorisation"])
@routes.post('/authorizePhone', response_model=PhoneAuthorisation, tags=["authorisation"])
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
        me = await bot.sign_in(bot_token=bot_token)
        if not isinstance(me, User):
            me = await bot.get_me()
        # end if
        user_id = me.user_id if hasattr(me, 'user_id') else me.id
        assert user_id
        bots[user_id] = bot
        return r_success(
            result=PhoneAuthorisation(
                message='SUCCESS: registered bot',
                reason=PhoneAuthorisationReasons.SUCCESS_BOT,
                data=PhoneAuthorisationData(
                    token='bot'+bot_token,
                    # session=bot.session.save(),
                )
            ),
            description="OK: Logged in. Use the token to connect to this service.",
            status_code=200,
        )
    # end if

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
        return r_error(
            result=PhoneAuthorisation(
                message='LOGIN FAILED: Please provide the code sent to you',
                reason=PhoneAuthorisationReasons.CODE_NEEDED,
                data=PhoneAuthorisationData(
                    phone_code_hash=sent_code.phone_code_hash,
                    session=session_str,
                ),
            ),
            error_code=401,
            description="UNAUTHORIZED: Login failed, please provide the code sent to you",
        )
    else:
        logger.info('Signing in.')
        try:
            # me = await self.sign_in(phone, code=code, phone_code_hash=phone_code_hash)
            result = await bot(SignInRequest(phone, phone_code_hash, str(code)))
            logger.warning(f"Sign in result: {result}")
            me = bot._on_login(result.user)
        except PhoneCodeExpiredError:
            session_str = bot.session.save()
            # TODO: Status 502
            return r_error(
                result=PhoneAuthorisation(
                    message='LOGIN FAILED: Code expired. Please provide the new code sent to you',
                    reason=PhoneAuthorisationReasons.CODE_EXPIRED,
                    data=PhoneAuthorisationData(
                        phone_code_hash=phone_code_hash,
                        session=session_str,
                    )
                ),
                error_code=401,
                description='UNAUTHORIZED: Login failed, code expired. Please provide the new code sent to you',
            )
        except SessionPasswordNeededError:
            if not password:
                txt = "Two-step verification is enabled for this account. Please provide the 'TELEGRAM_LOGGER_PHONE_LOGIN_CODE' environment variable."
                session_str = bot.session.save()
                logger.error(txt)
                # TODO: Status 502
                return r_error(
                    result=PhoneAuthorisation(
                        message='LOGIN FAILED: Please provide your personal two factor login (2FA) password you set in your account',
                        reason=PhoneAuthorisationReasons.TWO_FACTOR_PASSWORD_NEEDED,
                        data=PhoneAuthorisationData(
                            phone_code_hash=phone_code_hash,
                            code=code,
                            session=session_str,
                        )
                    ),
                    error_code=401,
                    description='UNAUTHORIZED: Login failed, please provide your personal two factor login (2FA) password you set in your account',
                )

            # end if
            me = await bot.sign_in(phone=phone, password=password, phone_code_hash=phone_code_hash)
        except Exception as e:
            logger.exception('sign in didn\'t work')
            raise e
        # end try
        assert await bot.is_user_authorized(), "should be authorized now."
        if not isinstance(me, User):
            me = await bot.get_me()
        # end if
        if hasattr(me, 'id'):
            chat_id = me.id
        elif hasattr(me, 'chat_id'):
             chat_id = me.chat_id
        elif hasattr(me, 'channel_id'):
            chat_id = me.channel_id
        elif hasattr(me, 'user_id'):
            chat_id = me.user_id
        else:
            logger.warn(f'me has no id like attribute:\n{me!r}\n{me!s}')
            raise ValueError('me is wrong?')
        # end if
        secret = bot.session.save()
        user_token = f'user{chat_id!s}@{secret}'
        # noinspection PyTypeChecker
        raise HTTPException(200, detail={'message': 'success', 'user_token': user_token})
        return r_error(
            result=PhoneAuthorisation(
                message='We did it mate!',
                reason=PhoneAuthorisationReasons.SUCCESS_PHONE,
                data=PhoneAuthorisationData(
                    token=user_token,
                ),
            ),
            error_code=401,
            description="OK: Logged in. Use the token to connect to this service.",
        )

    # end if
# end def


@routes.get('/{token}/getUpdates', tags=["updates"])
async def get_updates(token):
    global bots
    is_api, user_id, secret = await split_token(token)
    logger.debug(f'Setting webhook for {user_id}...')

    if user_id in bots:
        bot: TelegramClientUpdateCollector = bots[user_id]
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

    if user_id not in bots:
        try:
            logger.debug(f'Launching telegram client for {user_id}.')
            bot = await _get_bot(token)
            logger.debug(f'Registering all the listeners for {user_id}.')
            bot.register_update_listeners()
            bot.enable_polling()
            logger.debug(f'Telegram client for {user_id} is signed in and ready to use.')
        except Exception as e:
            logger.warning('Registering bot failed', exc_info=True)
            return r_error(500, description=str(e))
        # end try
        bots[user_id] = bot
        logger.debug(f'Telegram client for {user_id} is registered.')
    # end if

    # in any case we wanna return the updates
    return r_success([x.to_array() for x in bots[user_id].updates])
# end def


async def _get_bot(token: str) -> Union[TelegramClientUpdateCollector]:
    """
    Loads a bot by token or by phone account (in various register stages).
    - API token: `bot123456:ABC-DEF1234ghIkl-zyx007Wvsu4458w69`
    - User account: `user123456@asdasdajkhasd` (phone number + login hash)
    """
    global bots
    is_api, user_id, secret = await split_token(token)
    logger.debug(f"loading {'api' if is_api else 'user'} bot with id {user_id!r} and the token {secret!r}...")
    user_id = int(user_id)

    if user_id in bots:
        # easy mode: find existing
        return bots[user_id]
    # end if

    logger.debug(f'could not find instance for user_id {user_id},\nlaunching telegram muted client.')
    bot = TelegramClientUpdateCollector(
        session=StringSession(None if is_api else secret),  # set a session if not bot
        api_id=TG_API_ID,
        api_hash=TG_API_HASH,
        api_key=secret if is_api else None,  # use the api_key if is bot
        mode=UpdateModes.SILENT
    )
    logger.debug(f'Connecting in the bot {token}.')
    await bot.connect()
    logger.debug(f'Signing in the bot {token}.')
    if is_api:
        await bot.sign_in(bot_token=bot.api_key)
    else:
        if not await bot.is_user_authorized():
            raise HTTPException(502, "account not authorized correctly. Please use the /authorize endpoint again.")
        # end if
    logger.debug(f'Telegram client for {user_id} is signed in and ready to use.')
    assert user_id not in bots
    bots[user_id] = bot
    return bot
# end def


async def split_token(token):
    if token.startswith('bot') and ":" in token:
        token = token[3:]  # [3:] to remove "bot" prefix
        user_id, _ = token.split(":", maxsplit=1)
        secret = token
        is_api = True
    elif token.startswith('user') and "@" in token:
        user_id, secret = token[4:].split("@", maxsplit=1)  # [:4] to remove "user" prefix
        is_api = False
    else:
        raise ValueError('Your token seems wrong')
    # end if
    user_id = int(user_id)
    return is_api, user_id, secret
# end def


@routes.get('/{token}/getMe', tags=["bot"])
async def get_me(token: str = TOKEN_VALIDATION):
    bot = await _get_bot(token)
    me: User = await bot.get_me()
    me: TGUser = await to_web_api(me, client=bot)
    me: dict = me.to_array()
    return r_success(me, None)
# end def


@routes.get('/bot{token}/')
async def not_found(request):
    return r_error(404, "Not Found")
# end def


@crontab('* * * * * */10', start=True)
async def attime():
    logger.debug(f'current listeners: {bots!r}')
# end def


# ERROR HANDLING


# noinspection PyUnusedLocal
@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONableResponse:
    return r_error(
        error_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        description="UNPROCESSABLE ENTITY: Input validation failed",
        result=jsonable_encoder(exc.errors())
    )
# end def


# noinspection PyUnusedLocal
@app.exception_handler(HTTPException)
async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONableResponse:
    return r_error(
        error_code=status.HTTP_404_NOT_FOUND,
        description="Not Found",
    )
# end def


app.include_router(routes)
from .views.api.v4_5.sendable import routes as sendable_routes
app.include_router(sendable_routes)


def main():
    import uvicorn
    uvicorn.run(
        app, host="0.0.0.0", port=8080,
        use_colors=True,
        log_config={
            #logging.getLogger("uvicorn")
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": "uvicorn.logging.DefaultFormatter",
                    "fmt": "%(levelprefix)s %(message)s",
                    "use_colors": True,
                },
                "access": {
                    "()": "uvicorn.logging.AccessFormatter",
                    "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
                    "use_colors": True,
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    # "stream": "ext://sys.stderr",
                },
                "access": {
                    "formatter": "access",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                "": {"handlers": ["default"], "level": "DEBUG"},
                "uvicorn.error": {"level": "INFO"},
                "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
            },
        },
    )
# end def

if __name__ == "__main__":
    main()
# end def
