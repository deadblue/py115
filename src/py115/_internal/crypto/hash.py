__author__ = 'deadblue'

import hashlib
import io
from dataclasses import dataclass
from typing import BinaryIO


@dataclass
class DigestResult:
    sha1: str
    size: int


def digest(stream: BinaryIO) -> DigestResult:
    h = hashlib.sha1(
        stream.read()
    ).hexdigest().upper()
    return DigestResult(
        sha1=h, size=stream.tell()
    )


def digest_range(stream: BinaryIO, range_spec: str) -> str:
    tmp = range_spec.split('-')
    if len(tmp) != 2:
        return None
    offset = int(tmp[0])
    length = int(tmp[1]) - offset + 1
    stream.seek(offset, io.SEEK_SET)
    return hashlib.sha1(
        stream.read(length)
    ).hexdigest().upper()
