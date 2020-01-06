#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import typing

from typing import Union, Any
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse
from luckydonaldUtils.logger import logging

__author__ = 'luckydonald'

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if


class JSONableResponse(JSONResponse):
    """ Wraps the result in `jsonable_encoder()` to have pythonic models display correctly. """

    def render(self, content: typing.Any) -> bytes:
        content = jsonable_encoder(content)
        return super().render(content)
    # end def
# end class


def r_error(error_code=500, description: Union[str, None] = None, result: Any = None) -> JSONableResponse:
    return JSONableResponse({
        "ok": False,
        "error_code": error_code,
        "description": description,
        "result": result,
    }, status_code=error_code)
# end def


def r_success(result: Any = True, description: Union[str, None] = None, status_code: int = 200) -> JSONableResponse:
    return JSONableResponse({
        "ok": True,
        "result": result,
        "description": description,
    }, status_code=status_code)
# end def


#class RException(Htto)
