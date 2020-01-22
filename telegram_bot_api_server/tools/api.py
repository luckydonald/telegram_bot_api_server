#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import struct
from enum import IntEnum
from math import floor, log10
from typing import Union, Tuple
# noinspection PyProtectedMember
from telethon.utils import _rle_encode, _encode_telegram_base64
from luckydonaldUtils.logger import logging

__author__ = 'luckydonald'


logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if

class FileType(IntEnum):
  Thumbnail = 0
  ProfilePhoto = 1
  Photo = 2
  VoiceNote = 3
  Video = 4
  Document = 5
  Encrypted = 6
  Temp = 7
  Sticker = 8
  Audio = 9
  Animation = 10
  EncryptedThumbnail = 11
  Wallpaper = 12
  VideoNote = 13
  SecureRaw = 14
  Secure = 15
  Background = 16
  Size = 17
# end class


# noinspection PyShadowingBuiltins
def calculate_file_unique_id(type_id: int, id: int) -> str:
    return _encode_telegram_base64(
        _rle_encode(
            struct.pack(
                '<iq',
                type_id, id
            )
        )
    )
# end def


def calculate_file_id(type_id: FileType, dc_id: int, id: int, access_hash: int, version: int = 4):
    assert(
        type_id in
        (FileType.Voice, FileType.Video, FileType.Document, FileType.Sticker, FileType.Song, FileType.VideoNote)
    )
    if version == 2:
        binary = struct.pack(
            "<iiqqb",
            # type, dc_id, id,
            type_id, dc_id, id if id else 0,
            # access_hash
            access_hash if access_hash else 0,
            # version
            2
        )
    elif version == 4:
        binary = struct.pack(
            "<iiqqbb",
            # type, dc_id, id,
            type_id, dc_id, id if id else 0,
            # access_hash,
            access_hash if access_hash else 0,
            # twentytwo, version
            22, 4
        )
    else:
        raise ValueError(f'Unknown version flag: {version}')
    # end if
    return _encode_telegram_base64(_rle_encode(binary))
# end def


TYPE_SECRET = "secret"
TYPE_PRIVATE = "private"
TYPE_CHANNEL = "channel"
TYPE_SUPERGROUP = "supergroup"
TYPE_GROUP = "group"


def num_length(number: int) -> int:
    """
    Gets the length of a number.
    Negative and positive numbers have the same length, i.e. the sign is not taken into account.
    Only works with integers, not floats.

    Example: Negative `-100` and positive `100` both have the length of `3`.

    :param number: Number to calculate the length of.
    :return: the count of digits.
    """
    return floor(log10(abs(number))) + 1
# end def


def num_substring_start(number: int, length: int) -> int:
    delete_n_from_end = num_length(number) - length
    return int(number / 10 ** delete_n_from_end)
# end def


def from_supergroup(number: int) -> int:
    number = number * -1  # turn positive
    return number - 10 ** int(floor(log10(number)))
# end def


# https://github.com/tdlib/td/blob/56163c2460a65afc4db2c57ece576b8c38ea194b/td/telegram/DialogId.h#L27-L33
MIN_SECRET_ID = -2002147483648
ZERO_SECRET_ID = -2000000000000
MAX_SECRET_ID = -1997852516353
MIN_CHANNEL_ID = -1002147483647
MAX_CHANNEL_ID = -1000000000000
MIN_CHAT_ID = -2147483647
MAX_USER_ID = 2147483647


def type_from_id(chat_id: int) -> Union[None, Tuple[str], Tuple[str, str]]:
    # https://github.com/tdlib/td/blob/56163c2460a65afc4db2c57ece576b8c38ea194b/td/telegram/DialogId.cpp#L37-L52
    if chat_id >= 0:
        if 0 < chat_id <= MAX_USER_ID:
            return TYPE_PRIVATE,
        # end if
        return None
    # end if
    if MIN_CHAT_ID <= chat_id:
        return TYPE_GROUP,
    elif MIN_CHANNEL_ID <= chat_id < MAX_CHANNEL_ID:
        return TYPE_SUPERGROUP, TYPE_CHANNEL
    elif MIN_SECRET_ID <= chat_id < MAX_SECRET_ID:
        return TYPE_SECRET,
    # end if
# end def


def num_startswith(number: int, start: int) -> bool:
    start_n_digits = num_length(start)
    return num_substring_start(number, start_n_digits) == start
# end def


# https://github.com/tdlib/td/blob/56163c2460a65afc4db2c57ece576b8c38ea194b/td/telegram/DialogId.cpp#L54-L72
def as_user_id(id: int) -> int:
    assert TYPE_PRIVATE in type_from_id(id)
    return id
# end def


def as_chat_id(id: int) -> int:
    assert TYPE_GROUP in type_from_id(id);
    return -id
# end def


def as_channel_id(id: int) -> int:
    # assert TYPE_CHANNEL in type_from_id(id)
    return MAX_CHANNEL_ID - id
# end def


def as_secret_chat_id(id: int) -> int:
    # assert TYPE_SECRET in type_from_id(id)
    return id - ZERO_SECRET_ID
# end def


def from_user_id(id: int) -> int:
    return id
# end def


def from_chat_id(id: int) -> int:
    return -id
# end def


def from_channel_id(id: int) -> int:
    return MAX_CHANNEL_ID + id
# end def


def from_secret_chat_id(id: int) -> int:
    return id + ZERO_SECRET_ID
# end def
