#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi.params import Path
from luckydonaldUtils.logger import logging

__author__ = 'luckydonald'

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if

TOKEN_VALIDATION = Path(..., description="the bot's unique authentication token", min_length=1, regex=r"(bot\d+:[a-z0-9A-z-]|user\d+@[a-z0-9A-z_-])")
