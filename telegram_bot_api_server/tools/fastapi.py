#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from luckydonaldUtils.logger import logging

__author__ = 'luckydonald'


logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if


FAST_API_ISSUE_884_IS_FIXED = False


class Json:
    from pydantic import Json, parse_obj_as as _parse_obj_as

    def __getitem__(self, item):
        if FAST_API_ISSUE_884_IS_FIXED:
            return self.Json[item]
        else:
            return self.Json
        # end if
    # end def

    def parse_obj_as(self, type_, obj):
        """
        so we can easily turn off that workaround
        """
        if FAST_API_ISSUE_884_IS_FIXED:
            # nothing else is needed
            return obj
        else:
            return self.__class__._parse_obj_as(type_, obj)
        # end if
    # end def
# end def


Json = Json()  # so Json[Type] does call Json.__getitem__(self, item=Type)
