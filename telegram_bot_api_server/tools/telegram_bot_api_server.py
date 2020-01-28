#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Tuple

from luckydonaldUtils.logger import logging

__author__ = 'luckydonald'

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if


def split_token(token: str) -> Tuple[bool, int, str]:
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
