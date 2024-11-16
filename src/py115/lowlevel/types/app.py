__author__ = 'deadblue'

from dataclasses import dataclass
from typing import Dict, TypeAlias

from py115._internal.compat import StrEnum


@dataclass
class AppVersion:
    version_code: str
    download_url: str


class AppName(StrEnum):
    LIFE_ANDROID    = 'Android'
    LIFE_IOS        = 'iOS-iPhone'
    YUN_ANDROID     = 'Android-Yun'
    YUN_IOS         = 'iOS-iPhone-Yun'
    TV              = 'Android-tv'
    BROWSER_WINDOWS = 'PC-115chrome_x64'
    BROWSER_MACOS   = 'MAC-115chrome'
    BROWSER_LINUX   = 'Linux-115chrome'


AppVersionResult: TypeAlias = Dict[AppName, AppVersion]
