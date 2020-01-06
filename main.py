#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from telegram_bot_api_server.main import app, main
from luckydonaldUtils.logger import logging

__author__ = 'luckydonald'

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if


logger.debug(f'launching {app}')

if __name__ == '__main__':
    main()
# end def
