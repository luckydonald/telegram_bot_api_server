#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from luckydonaldUtils.logger import logging

__author__ = 'luckydonald'


logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if

__all__ = ['Json', 'parse_obj_as']


FAST_API_ISSUE_884_IS_FIXED = False


if FAST_API_ISSUE_884_IS_FIXED:
    from pydantic import Json

    def parse_obj_as(_, obj, *__, **___):
        """
        we don't need any additional parsing as fastapi now does that correctly
        """
        return obj
    # end def
else:
    class __JsonWrapper:
        from pydantic import Json

        def __getitem__(self, item):
            """ Basically throw away `[Type]` when used like `Json[Type]` """
            return self.Json
        # end def
    # end def
    Json = __JsonWrapper()  # so Json[Type] does call Json.__getitem__(self, item=Type)

    from pydantic import parse_obj_as
# end if
