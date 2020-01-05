#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Union, Any
from starlette.responses import JSONResponse
from luckydonaldUtils.logger import logging

__author__ = 'luckydonald'

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if


def r_error(error_code=500, description: Union[str, None] = None, result: Any = None) -> JSONResponse:
    return JSONResponse({
        "ok": False,
        "error_code": error_code,
        "description": description,
        "result": result,
    }, status_code=error_code)
# end def


def r_success(result: Any, description: Union[str, None] = None, status_code: int = 200) -> JSONResponse:
    return JSONResponse({
        "ok": True,
        "result": result,
        "description": description,
    }, status_code=status_code)
# end def
