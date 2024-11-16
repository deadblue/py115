__author__ = 'deadblue'

from dataclasses import dataclass
from enum import IntEnum
from typing import Dict

from py115._internal.compat import StrEnum


class QrcodeClient(StrEnum):
    WEB      = 'web'
    ANDROID  = 'android'
    IOS      = 'ios'
    TV       = 'tv'
    WECHAT   = 'wechatmini'
    ALIPAY   = 'alipaymini'
    QANDROID = 'qandroid'


@dataclass
class QrcodeToken:
    uid: str
    time: int
    sign: str


class QrcodeStatus(IntEnum):
    WAITING = 0
    SCANNED = 1
    ALLOWED = 2
    EXPIRED = 9


@dataclass
class QrcodeLoginResult:
    user_id: int
    user_name: str
    cookies: Dict[str, str]
