#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Union
from fastapi import UploadFile
from pydantic import HttpUrl, AnyUrl
from luckydonaldUtils.logger import logging

__author__ = 'luckydonald'
__all__ = [
    'AttachUrl', 'CallbackGameModel', 'InputFileModel', 'InputFileModel', 'InputMessageContentModel'
]

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if


CallbackGameModel = Union[str]
InputMessageContentModel = Union[
    'InputTextMessageContentModel', 'InputLocationMessageContentModel',
    'InputVenueMessageContentModel', 'InputContactMessageContentModel'
]


class AttachUrl(AnyUrl):
    strip_whitespace = True
    min_length = len('attach://') + 1
    max_length = 2 ** 16  # 65536
    allowed_schemes = {'attach'}
    tld_required = False
    user_required = False
# end class


InputFileModel = Union[
    str,  # file_id,
    AttachUrl,  # attach://filename
    HttpUrl,  # HTTP URL,
    UploadFile,  # multipart/form-data
]
