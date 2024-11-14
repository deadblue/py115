__author__ = 'deadblue'

from py115.lowlevel.types.app import (
    AppName, AppVersion, AppVersionResult
)
from ._base import JsonApiSpec, JsonResult


class AppVersionApi(JsonApiSpec[AppVersionResult]):

    def __init__(self) -> None:
        super().__init__('https://appversion.115.com/1/web/1.0/api/getMultiVer')

    def _parse_json_result(self, json_obj: JsonResult) -> AppVersionResult:
        result: AppVersionResult = {}
        for key, value in json_obj.get('data').items():
            app_name = AppName._value2member_map_.get(key, None)
            if app_name is None: continue
            result[app_name] = AppVersion(
                version_code=value.get('version_code'),
                download_url=value.get('version_url')
            )
        return result
