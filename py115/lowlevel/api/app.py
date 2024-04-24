__author__ = 'deadblue'

from typing import Any, Dict

from ._json import JsonApiSpec


class AppVersionApi(JsonApiSpec[str]):

    def __init__(self) -> None:
        super().__init__('https://appversion.115.com/1/web/1.0/api/chrome')

    def _parse_json_result(self, obj: Dict[str, Any]) -> str:
        return obj['data']['linux_115']['version_code']