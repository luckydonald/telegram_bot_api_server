#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from telegram_bot_api_server.main import app, main
from luckydonaldUtils.logger import logging
try:
    # noinspection PyUnresolvedReferences
    import pydevd_pycharm
    pydevd_pycharm.settrace('localhost', port=56221, suspend=False)
except (ImportError, ConnectionRefusedError):
    pass
# end try

__author__ = 'luckydonald'

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if


logger.debug(f'launching {app}')

if __name__ == '__main__':
    main()
# end def
