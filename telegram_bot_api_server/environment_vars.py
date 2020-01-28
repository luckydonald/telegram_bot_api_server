#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from luckydonaldUtils.logger import logging

__author__ = 'luckydonald'

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if

TG_APP_ID = os.getenv('TG_APP_ID', None)
assert TG_APP_ID is not None  # $TG_APP_ID environment variable
TG_APP_ID = int(TG_APP_ID)  # parse $TG_APP_ID as integer.

TG_APP_HASH = os.getenv('TG_APP_HASH', None)
assert TG_APP_HASH is not None  # $TG_APP_HASH environment variable#
