__author__ = 'deadblue'

from dataclasses import dataclass
from typing import Dict, TypeAlias

from py115.compat import StrEnum


@dataclass
class AppVersion:
    version_code: str
    download_url: str


class AppName(StrEnum):
    LifeAndroid = 'Android'
    LifeiOS = 'iOS-iPhone'
    TV = 'Android-tv'
    YunAndroid = 'Android-Yun'
    YuniOS = 'iOS-iPhone-Yun'
    BrowserWindows = 'PC-115chrome_x64'
    BrowserMacOS = 'MAC-115chrome'
    BrowserLinux = 'Linux-115chrome'


AppVersionResult: TypeAlias = Dict[AppName, AppVersion]
