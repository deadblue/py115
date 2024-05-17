__author__ = 'deadblue'

from typing import Any, Dict

from py115._internal.api import app
from py115.compat import StrEnum
from ._base import JsonApiSpec


class AppType(StrEnum):

    WEB = 'web'
    WINDOWS = 'windows'
    MAC = 'mac'
    LINUX = 'linux'


class AppVersionApi(JsonApiSpec[str]):

    _app_name: str

    def __init__(self, app_type: AppType = AppType.LINUX) -> None:
        super().__init__('https://appversion.115.com/1/web/1.0/api/chrome')
        if app_type in (AppType.LINUX, AppType.MAC):
            self._app_name = f'{app_type.value}_115'
        elif app_type == AppType.WINDOWS:
            self._app_name = f'window_115'
        else:
            raise Exception()

    def _parse_json_result(self, obj: Dict[str, Any]) -> str:
        return obj['data'][self._app_name]['version_code']