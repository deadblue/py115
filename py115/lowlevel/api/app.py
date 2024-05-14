__author__ = 'deadblue'

from typing import Any, Dict

from py115._internal.api import app
from py115.compat import StrEnum
from ._base import JsonApiSpec


class AppName(StrEnum):

    WINDOWS = 'window_115'
    MAC = 'mac_115'
    LINUX = 'linux_115'


class AppVersionApi(JsonApiSpec[str]):

    _app_name: str

    def __init__(self, app_name: AppName = AppName.LINUX) -> None:
        super().__init__('https://appversion.115.com/1/web/1.0/api/chrome')
        self._app_name = app_name.value

    def _parse_json_result(self, obj: Dict[str, Any]) -> str:
        return obj['data'][self._app_name]['version_code']