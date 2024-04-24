__author__ = 'deadblue'

from dataclasses import dataclass
from typing import Any

from ._json import JsonApiSpec, JsonResult

@dataclass
class UpdateInfoResult:
    user_id: int
    user_key: str


class UploadInfoApi(JsonApiSpec[Any]):

    def __init__(self) -> None:
        super().__init__('https://proapi.115.com/app/uploadinfo')
    
    def _parse_json_result(self, json_obj: JsonResult) -> Any:
        return UpdateInfoResult(
            user_id=json_obj.get('user_id'),
            user_key=json_obj.get('userkey')
        )
