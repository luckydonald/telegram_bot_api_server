#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import struct
import base64
from abc import abstractmethod

from luckydonaldUtils.logger import logging
from luckydonaldUtils.encoding import to_unicode

__author__ = 'luckydonald'

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if


def base64url_decode(string):
    # add missing padding # http://stackoverflow.com/a/9807138
    return base64.urlsafe_b64decode(string + '='*(4 - len(string)%4))
# end def


def base64url_encode(string):
    return to_unicode(base64.urlsafe_b64encode(string)).rstrip("=")
# end def


def rle_decode(binary):
    """
    Returns the byte array of the given string.
    :param string:
    :return: The array of ints.
    :rtype: bytearray
    """
    # https://github.com/danog/MadelineProto/blob/38d6ee07b3a7785bcc77ed4ba3ef9ddd8e915975/pwrtelegram_debug_bot.php#L28-L42
    # https://github.com/danog/MadelineProto/blob/1485d3879296a997d47f54469b0dd518b9230b06/src/danog/MadelineProto/TL/Files.php#L66
    base256 = bytearray()
    last = None
    for cur in binary:
        if last == 0:
            for i in range(cur):
                base256.append(0)
            # end for
            last = None
        else:
            if last is not None:
                base256.append(last)
            # end if
            last = cur
        # end if
    # end for
    if last is not None:
        base256.append(last)
    # end if
    return base256
# end def


def rle_encode(binary):
    # https://github.com/danog/MadelineProto/blob/1485d3879296a997d47f54469b0dd518b9230b06/src/danog/MadelineProto/TL/Files.php#L85
    new = bytearray()
    count = 0
    for cur in binary:
        if cur == 0:
            count += 1
        else:  # not 0 (any more)
            if count > 0:
                new.append(0)
                new.append(count)
                count = 0
            # end if
            new.append(cur)
        # end if
    # end for
    return new
# end def


class FileId(object):
    def __init__(self, file_id, type_id, type_str, type_detailed, dc_id, id, access_hash, version=2):
        """
        :param file_id: Telegram file_id
        :type  file_id: str

        :param type_id: Number describing the type. See `type_detailed` for a human readable string
        :type  type_id: int

        :param type_str: A string showing which datatype this file_id is. Could also be checked with `isinstance(...)`
        :type  type_str: str

        :param type_detailed: a human readable string of the type
        :type  type_detailed: str

        :param dc_id: The if of the Telegram Datacenter
        :type  dc_id: int

        :param id: The file id (long)
        :type  id: int

        :param access_hash: the file access hash for the current user (long)
        :type  access_hash: int

        :param version: version number of the file id.
        :type  version: int

        :return:
        :rtype:
        """
        self.file_id = file_id
        self.type_id = type_id
        self.type_str = type_str
        self.type_detailed = type_detailed
        self.dc_id = dc_id
        self.id = id
        self.access_hash = access_hash
        self.version = version
    # end def __init__

    def change_type(self, type_id):
        """
        Changes the type of the document.

        :param type_id:
        :return:
        """
        self.type_id = type_id
        self.type_detailed = DocumentFileId.TYPES[self.type_id]
        return self.recalculate()
    # end def

    @staticmethod
    def generate_new(file_id, type_id, type_detailed, dc_id, id, access_hash, location=None, something=None, version=2):
        if location:
            return PhotoFileId(file_id, type_id, type_detailed, dc_id, id, access_hash, location, something, version)
        # end if
        return DocumentFileId(file_id, type_id, type_detailed, dc_id, id, access_hash, version)
    # end def

    @classmethod
    def from_file_id(cls, file_id, decoded=None):
        """

        :param file_id:
        :param decoded: if the file_id binary data is already decoded (rle + base64url).
        :except ValueError: Unknown type id.
        :return:
        """
        if not decoded:
            decoded = rle_decode(base64url_decode(file_id))
        # end if
        type_id = struct.unpack("<i", decoded[0:4])[0]
        if type_id in PhotoFileId.TYPES:  # 0, 2
            file_id_obj = PhotoFileId.from_file_id(file_id, decoded)
        elif type_id in DocumentFileId.TYPES:  # 3, 4, 5, 8, 9
            file_id_obj = DocumentFileId.from_file_id(file_id, decoded)
        else:
            raise ValueError("Found unknown type: {type} in {file_id}".format(type=type, file_id=file_id))
        # end if
        return file_id_obj
    # end def

    def recalculate(self):
        """ Recalculates the file_id """
        file_id = self.to_file_id()
        self.file_id = file_id
        return file_id
    # end def

    def __repr__(self):
        return "FileId(file_id={file_id!r}, type_id={type_id!r}, type_str={type_str!r}, type_detailed={type_detailed!r}, dc_id={dc_id!r}, id={id!r}, access_hash={access_hash!r}, version={version!r})".format(
            file_id=self.file_id, type_id=self.type_id, type_str=self.type_str, type_detailed=self.type_detailed,
            dc_id=self.dc_id, id=self.id, access_hash=self.access_hash, version=self.version,
        )
    # end def __str__
    TYPE_THUMBNAIL = 0
    TYPE_PHOTO = 2
    TYPE_VOICE = 3
    TYPE_VIDEO = 4
    TYPE_DOCUMENT = 5
    TYPE_STICKER = 8
    TYPE_SONG = 9
    TYPE_VIDEO_NOTE = 13

    SUPPORTED_VERSIONS = (2, 4)
    MAX_VERSION = 4

    @abstractmethod
    def to_file_id(self):
        raise NotImplementedError('Subclasses should have code here.')
    # end def
# end class FileId


class DocumentFileId(FileId):
    def __init__(self, file_id, type_id, type_detailed, dc_id, id, access_hash, version=2):
        """
        :param file_id: Telegram file_id
        :type  file_id: str

        :param type_id: Number describing the type. See `type_detailed` for a human readable string
        :type  type_id: int

        :param type_detailed: a human readable string of the type
        :type  type_detailed: str

        :param dc_id: The if of the Telegram Datacenter
        :type  dc_id: int

        :param id: The file id (long)
        :type  id: int

        :param access_hash: the file access hash for the current user (long)
        :type  access_hash: int

        :param version: version number of the file id.
        :type  version: int

        :return:
        :rtype:
        """
        super(DocumentFileId, self).__init__(file_id, type_id, "document", type_detailed, dc_id, id, access_hash, version)
    # end def __init__

    TYPES = {FileId.TYPE_VOICE: "voice", FileId.TYPE_VIDEO: "video", FileId.TYPE_DOCUMENT: "document",
             FileId.TYPE_STICKER: "sticker", FileId.TYPE_SONG: "song", FileId.TYPE_VIDEO_NOTE: "video note"}
    """ A human readable string of the type """

    def swap_type_sticker(self):
        """
        This swaps out the document types "document" <-> "sticker"

        :param data: Can be a dict as obtained by `take_apart_file_id(file_id)`.
                     Otherwise a file_id is assumed and said function `take_apart_file_id` is called.
        :type  data: dict or bytearray or bytes

        :return: new file id
        :rtype: str
        """

        self.change_type(FileId.TYPE_STICKER if self.type_id == FileId.TYPE_DOCUMENT else FileId.TYPE_DOCUMENT)
        return self.recalculate()
    # end def

    @classmethod
    def from_file_id(cls, file_id, decoded=None):
        if not decoded:
            decoded = rle_decode(base64url_decode(file_id))
        # end if
        version = struct.unpack("<b", decoded[-1:])[0]
        if version not in FileId.SUPPORTED_VERSIONS:
            raise ValueError(f'Unsupported file_id version: {version}')
        # end if
        if version == 2:
            # CAADBAADwwADmFmqDf6xBrPTReqHAg sticker, @teleflaskBot
            type_id, dc_id, id, access_hash, checksum = struct.unpack('<iiqqb', decoded)
        elif version == 4:
            # CAADBAADwwADmFmqDf6xBrPTReqHFgQ sticker, @teleflaskBot
            type_id, dc_id, id, access_hash, twentytwo, checksum = struct.unpack('<iiqqbb', decoded)
            if twentytwo != 22:
                raise ValueError(f"Strange field expected to be 22.")
            # end if
        else:
            raise ValueError(f'Unsupported file_id version for document type: {version}')
        # end if
        if checksum != version:
            raise ValueError(f"Version expected to be {version} but is {checksum}.")
        # end if
        assert type_id in DocumentFileId.TYPES
        return DocumentFileId(
            file_id=file_id, type_id=type_id, type_detailed=DocumentFileId.TYPES[type_id],
            dc_id=dc_id, id=id, access_hash=access_hash, version=version
        )
    # end def

    def as_photo(self, location: 'PhotoFileId.Location', something: int):
        return PhotoFileId(
            file_id=self.file_id,
            type_id=self.type_id, type_detailed=self.type_detailed, dc_id=self.dc_id, access_hash=self.access_hash,
            location=location,
            something=something,
        )

    def to_file_id(self, version=None):
        assert self.type_id in DocumentFileId.TYPES
        if version is None:
            version = self.version
        # end if
        if version is None:
            version = self.MAX_VERSION
        # end if
        if version == 2:
            binary = struct.pack(
                "<iiqqb",
                # type, dc_id, id,
                self.type_id, self.dc_id, self.id if self.id else 0,
                # access_hash
                self.access_hash if self.access_hash else 0,
                # version
                2
            )
        elif version == 4:
            binary = struct.pack(
                "<iiqqbb",
                # type, dc_id, id,
                self.type_id, self.dc_id, self.id if self.id else 0,
                # access_hash,
                self.access_hash if self.access_hash else 0,
                # twentytwo, version
                22, 4
            )
        else:
            raise ValueError(f'Unknown version flag: {version}')
        # end if
        return base64url_encode(rle_encode(binary))
    # end def

    def __repr__(self):
        return "DocumentFileId(file_id={file_id!r}, type_id={type_id!r}, type_str={type_str!r}, type_detailed={type_detailed!r}, dc_id={dc_id!r}, id={id!r}, access_hash={access_hash!r}, version={version!r})".format(
            file_id=self.file_id, type_id=self.type_id, type_str=self.type_str, type_detailed=self.type_detailed,
            dc_id=self.dc_id, id=self.id, access_hash=self.access_hash, version=self.version,
        )
    # end def __repr__
# end class DocumentFileId


class PhotoFileId(FileId):
    class Location(object):
        def __init__(self, volume_id, secret, local_id):
            self.volume_id = volume_id
            self.secret = secret
            self.local_id = local_id
        # end def __init__

        def __repr__(self):
            return "Location(volume_id={volume_id}, secret={secret}, local_id={local_id})".format(
                volume_id=self.volume_id, secret=self.secret, local_id=self.local_id
            )
        # end def __str__
    # end class Location

    def __init__(self, file_id, type_id, type_detailed, dc_id, id, access_hash, location, something, version=2):
        """
        :param file_id: Telegram file_id
        :type  file_id: str

        :param type_id: Number describing the type. See `type_detailed` for a human readable string
        :type  type_id: int

        :param type_detailed: str
        :type  type_detailed: str

        :param dc_id: The if of the Telegram Datacenter
        :type  dc_id: int

        :param id: The file id (long)
        :type  id: int

        :param access_hash: the file access hash for the current user (long)
        :type  access_hash: int

        :param location: a location (for downloading)
        :type  location: PhotoFileId.Location

        :return:
        :rtype:
        """
        super(PhotoFileId, self).__init__(file_id, type_id, "photo", type_detailed, dc_id, id, access_hash, version)
        assert isinstance(location, PhotoFileId.Location)
        self.location = location
        self.something = something
    # end def __init__

    TYPES = {FileId.TYPE_THUMBNAIL: "thumbnail", FileId.TYPE_PHOTO: "photo"}
    """ A human readable string of the type """

    @classmethod
    def from_file_id(cls, file_id, decoded=None):
        if not decoded:
            decoded = rle_decode(base64url_decode(file_id))
        # end if
        version = struct.unpack("<b", decoded[-1:])[0]
        if version not in FileId.SUPPORTED_VERSIONS:
            raise ValueError(f'Unsupported file_id version: {version}')
        # end if
        if version == 2:
            # AgADAgADRaoxG64rCUlfm3fj3nihW3PHUQ8ABLefjdP8kuxqa7ABAAEC via @teleflaskBot
            type_id, dc_id, id, access_hash, location_volume_id, location_secret, location_local_id, checksum = struct.unpack('<iiqqqqib', decoded)
            something = None
        elif version == 4:
            # AgADAgADRaoxG64rCUlfm3fj3nihW3PHUQ8ABAEAAwIAA3gAA2uwAQABFgQ via @teleflaskBot
            type_id, dc_id, id, access_hash, location_volume_id, location_secret, something, location_local_id, twentytwo, checksum = struct.unpack('<iiqqqqiibb', decoded)
            if twentytwo != 22:
                raise ValueError(f"Strange field expected to be 22.")
            # end if
        else:
            raise ValueError(f'Unsupported file_id version for image type {type}: {version}')
        # end if
        if checksum != version:
            raise ValueError(f"Version expected to be {version}")
        # end if
        assert type_id in PhotoFileId.TYPES
        return PhotoFileId(
            file_id=file_id, type_id=type_id, type_detailed=PhotoFileId.TYPES[type_id],
            dc_id=dc_id, id=id, access_hash=access_hash,
            location=PhotoFileId.Location(
                volume_id=location_volume_id, secret=location_secret, local_id=location_local_id
            ),
            something=something,
            version=version,
        )
    # end def

    def to_file_id(self, version=None):
        assert self.type_id in PhotoFileId.TYPES
        if version == 2:
            binary = struct.pack(
                '<iiqqqqib',
                # type, dc_id, id,
                self.type_id, self.dc_id, self.id if self.id else 0,
                # access_hash,
                self.access_hash if self.access_hash else 0,
                # location_volume_id, location_secret,
                self.location.volume_id, self.location.secret,
                # location_local_id,
                self.location.local_id,
                # version
                2
            )
        elif version == 4:
            binary = struct.pack(
                '<iiqqqqiibb',
                # type, dc_id, id,
                self.type_id, self.dc_id, self.id if self.id else 0,
                # access_hash,
                self.access_hash if self.access_hash else 0,
                # location_volume_id, location_secret,
                self.location.volume_id, self.location.secret,
                # something,
                self.something,
                #  location_local_id,
                self.location.local_id,
                # twentytwo, version
                22, 4
            )
        else:
            raise ValueError(f'Unknown version to use: {version}')
            # end if
        return base64url_encode(rle_encode(binary))
    # end def

    def __repr__(self):
        return "PhotoFileId(file_id={file_id!r}, type_id={type_id!r}, type_str={type_str!r}, type_detailed={type_detailed!r}, dc_id={dc_id!r}, id={id!r}, access_hash={access_hash!r}, location={location!r}, version={version!r}, something={something!r})".format(
            file_id=self.file_id, type_id=self.type_id, type_str=self.type_str, type_detailed=self.type_detailed,
            dc_id=self.dc_id, id=self.id, access_hash=self.access_hash, location=self.location,
            version=self.version, something=self.something,
        )
    # end def __str__
# end class PhotoFileId
