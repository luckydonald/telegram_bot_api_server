#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from aiohttp.web_request import Request
from luckydonaldUtils.logger import logging
import functools
import inspect

__author__ = 'luckydonald'

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if


def flaskify_arguments(function):
    """
    Takes the path arguments from the `request` parameter, and apply them as `**kwargs`.
    """
    # preparation: inspect the function to check if we should supply a `request=...` parameter.
    sig = inspect.signature(function)
    apply_request_param = False
    if "request" in sig.parameters and sig.parameters['request']:
        # function has parameter request
        apply_request_param = True
        if sig.parameters['request'].annotation not in (Request,):
            # it doesn't have the type annotation `request: Request`

            raise TypeError(
                f'Function {function} has a parameter "request" which is not annotated with the `Request` or `str` type!\n'
                f'To avoid overwriting a possible text variable, it will be ignored if there is a "request" parameter in the data!'
            )
        # end if
    # end if

    @functools.wraps(function)
    async def apply_matches_inner(*args, **kwargs):
        logger.debug(
            f'function wrapper for {function} got arguments: *{args!r} and **{kwargs!r}'
        )
        args = list(args)
        if 'request' in kwargs and len(args) == 0:
            request = kwargs.pop('request')
        elif not kwargs and len(args) == 1:
            request = args.pop(0)
        else:
            logger.debug(
                f'wrapped function {function} directly called with additional arguments *{args!r} and **{kwargs!r}, not resolving `request.match_info`'
            )
            return await function(*args, **kwargs)
        # end def
        params = dict(request.match_info)
        if apply_request_param:
            if 'request' in params:
                raise ValueError(
                    f'Function {function} has a parameter "request" requiring the `Request` type, but routing has given us a "request" parameter as well!'
                )
            # end if
            params['request'] = request
        # end if
        logger.debug(
            f'calling function {function} with resolved variables: **{params!r}'
        )
        return await function(**params)
    # end def

    return apply_matches_inner
# end def
