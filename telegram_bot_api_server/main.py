#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
try:
    import uvloop
except ImportError:
    uvloop = None
# end if

from enum import Enum
from typing import Dict, Union, List, Optional, Any
from aiocron import crontab
from asyncio import get_event_loop
from fastapi import FastAPI, APIRouter, Query
from pydantic import BaseModel
from starlette import status
from telethon.utils import parse_phone
from telethon.errors import SessionPasswordNeededError, PhoneCodeExpiredError, RPCError
from fastapi.encoders import jsonable_encoder
from telethon.tl.types import User
from telethon.sessions import StringSession
from starlette.requests import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from luckydonaldUtils.logger import logging
from telethon.tl.functions.auth import SignInRequest
from pytgbot.api_types.receivable import WebhookInfo

from .tools.telegram_bot_api_server import split_token
from .environment_vars import TG_APP_ID, TG_APP_HASH
from .classes.webhook import TelegramClientUpdateCollector, UpdateModes
from .tools.responses import r_error, r_success, JSONableResponse
from .constants import TOKEN_VALIDATION

__author__ = 'luckydonald'

if uvloop:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
# end if

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


@routes.api_route('/{token}/setWebhook', methods=['GET', 'POST'], tags=['official', 'webhook', 'updates'])
async def set_webhook(
    token: str = TOKEN_VALIDATION,
    url: str = Query(..., description='HTTPS url to send updates to. Use an empty string to remove webhook integration'),
    # certificate: Optional[InputFile] = Query(None, description='Upload your public key certificate so that the root certificate in use can be checked. See our self-signed guide for details.'),
    certificate: Optional[Any] = Query(None, description='Upload your public key certificate so that the root certificate in use can be checked. See our self-signed guide for details.'),
    max_connections: Optional[int] = Query(None, description='Maximum allowed number of simultaneous HTTPS connections to the webhook for update delivery, 1-100. Defaults to 40. Use lower values to limit the load on your bot‘s server, and higher values to increase your bot’s throughput.'),
    allowed_updates: Optional[List[str]] = Query(None, description='List the types of updates you want your bot to receive. For example, specify ["message", "edited_channel_post", "callback_query"] to only receive updates of these types. See Update for a complete list of available update types. Specify an empty list to receive all updates regardless of type (default). If not specified, the previous setting will be used.Please note that this parameter doesn\'t affect updates created before the call to the setWebhook, so unwanted updates may be received for a short period of time.'),
) -> JSONableResponse:
    """
    Use this method to specify a url and receive incoming updates via an outgoing webhook. Whenever there is an update for the bot, we will send an HTTPS POST request to the specified url, containing a JSON-serialized Update. In case of an unsuccessful request, we will give up after a reasonable amount of attempts. Returns True on success.
    If you'd like to make sure that the Webhook request comes from Telegram, we recommend using a secret path in the URL, e.g. https://www.example.com/<token>. Since nobody else knows your bot‘s token, you can be pretty sure it’s us.

    Notes1. You will not be able to receive updates using getUpdates for as long as an outgoing webhook is set up.2. To use a self-signed certificate, you need to upload your public key certificate using certificate parameter. Please upload as InputFile, sending a String will not work.3. Ports currently supported for Webhooks: 443, 80, 88, 8443.
    NEW! If you're having any trouble setting up webhooks, please check out this amazing guide to Webhooks.


    https://core.telegram.org/bots/api#setwebhook
    """
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


@routes.api_route('/{token}/deleteWebhook', methods=['GET', 'POST'], tags=['official', 'webhook', 'updates'])
async def delete_webhook(
    token: str = TOKEN_VALIDATION,
) -> JSONableResponse:
    """
    Use this method to remove webhook integration if you decide to switch back to getUpdates. Returns True on success. Requires no parameters.

    https://core.telegram.org/bots/api#deletewebhook
    """
    global bots
    is_api, user_id, secret = split_token(token)
    if user_id in bots:
        bot = bots[user_id]
        bot.mode = UpdateModes.POLLING
        return r_success(True, "Webhook was deleted")
    # end if
    return r_success(True, "Webhook was not set")
# end def


@routes.api_route('/{token}/getWebhookInfo', methods=['GET', 'POST'], tags=['official'])
async def get_webhook_info(
    token: str = TOKEN_VALIDATION,
) -> JSONableResponse:
    """
    Use this method to get current webhook status. Requires no parameters. On success, returns a WebhookInfo object. If the bot is using getUpdates, will return an object with the url field empty.

    https://core.telegram.org/bots/api#getwebhookinfo
    """
    bot = await _get_bot(token)

    data = WebhookInfo(
        url=bot.webhook_url if bot.webhook_url else "",
        has_custom_certificate=False,
        pending_update_count=len(bot.updates),
        last_error_date=None,
        last_error_message=None,
        max_connections=None,
        allowed_updates=None,
    )
    return r_success(data.to_array())
# end def


class SuccessfulPhoneAuthorisationData(BaseModel):
    user_token: str


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
    data: Union[PhoneAuthorisationData, SuccessfulPhoneAuthorisationData]
# end def


@routes.get('/authorizePhone', response_model=PhoneAuthorisation, tags=["authorisation", "addition"])
@routes.post('/authorizePhone', response_model=PhoneAuthorisation, tags=["authorisation", "addition"])
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
        session=StringSession(session), api_id=TG_APP_ID, api_hash=TG_APP_HASH,
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
        return r_success(result=SuccessfulPhoneAuthorisationData(user_token=user_token), description="OK: Logged in. Use the token to connect to this service.", status_code=200)
    # end if
# end def


@routes.api_route('/{token}/getUpdates', methods=['GET', 'POST'], tags=['official', 'updates'])
async def get_updates(
    token: str = TOKEN_VALIDATION,
    offset: Optional[int] = Query(None, description='Identifier of the first update to be returned. Must be greater by one than the highest among the identifiers of previously received updates. By default, updates starting with the earliest unconfirmed update are returned. An update is considered confirmed as soon as getUpdates is called with an offset higher than its update_id. The negative offset can be specified to retrieve updates starting from -offset update from the end of the updates queue. All previous updates will forgotten.'),
    limit: Optional[int] = Query(None, description='Limits the number of updates to be retrieved. Values between 1—100 are accepted. Defaults to 100.'),
    timeout: Optional[int] = Query(None, description='Timeout in seconds for long polling. Defaults to 0, i.e. usual short polling. Should be positive, short polling should be used for testing purposes only.'),
    allowed_updates: Optional[List[str]] = Query(None, description='List the types of updates you want your bot to receive. For example, specify ["message", "edited_channel_post", "callback_query"] to only receive updates of these types. See Update for a complete list of available update types. Specify an empty list to receive all updates regardless of type (default). If not specified, the previous setting will be used.Please note that this parameter doesn\'t affect updates created before the call to the getUpdates, so unwanted updates may be received for a short period of time.'),
) -> JSONableResponse:
    """
    Use this method to receive incoming updates using long polling (wiki). An Array of Update objects is returned.

    Notes1. This method will not work if an outgoing webhook is set up.2. In order to avoid getting duplicate updates, recalculate offset after each server response.


    https://core.telegram.org/bots/api#getupdates
    """
    global bots
    is_api, user_id, secret = split_token(token)
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
    return r_success([x.to_array() if x is not None else None for x in bots[user_id].updates])
# end def


async def _get_bot(token: str) -> Union[TelegramClientUpdateCollector]:
    """
    Loads a bot by token or by phone account (in various register stages).
    - API token: `bot123456:ABC-DEF1234ghIkl-zyx007Wvsu4458w69`
    - User account: `user123456@asdasdajkhasd` (phone number + login hash)
    """
    global bots
    is_api, user_id, secret = split_token(token)
    logger.debug(f"loading {'api' if is_api else 'user'} bot with id {user_id!r} and the token {secret!r}...")
    user_id = int(user_id)

    if user_id in bots:
        # easy mode: find existing
        return bots[user_id]
    # end if

    logger.debug(f'could not find instance for user_id {user_id},\nlaunching telegram muted client.')
    bot = TelegramClientUpdateCollector(
        session=StringSession(None if is_api else secret),  # set a session if not bot
        api_id=TG_APP_ID,
        api_hash=TG_APP_HASH,
        api_key=secret if is_api else None,  # use the api_key if is bot
        token=token,
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
@app.exception_handler(RPCError)
async def request_validation_exception_handler(
    request: Request, exc: RPCError
) -> JSONableResponse:
    msg, causer = str(exc).rstrip(')').split(' (caused by ', maxsplit=1)
    return r_error(
        error_code=exc.code if exc.code else status.HTTP_500_INTERNAL_SERVER_ERROR,
        description=exc.message + ': ' + msg,
        result={
            'caused_by': causer,
        },
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
from .api.v4_6.functions.message import routes as message_routes
app.include_router(message_routes)
from .api.v4_6.functions.location import routes as location_routes
app.include_router(location_routes)
from .api.v4_6.functions.status import routes as status_routes
app.include_router(status_routes)
from .api.v4_6.functions.sticker import routes as sticker_routes
app.include_router(sticker_routes)
from .api.v4_6.functions.testing123 import routes as testing123_routes
app.include_router(testing123_routes)
from .api.v4_6.functions.media import routes as media_routes
app.include_router(media_routes)


def main():
    import uvicorn
    uvicorn.run(
        app, host="0.0.0.0", port=8080,
        use_colors=True,
        log_config=None,
    )
# end def

if __name__ == "__main__":
    main()
# end def
