__author__ = 'deadblue'

from dataclasses import dataclass

from ._base import JsonApiSpec, JsonResult


@dataclass
class UserInfoResult:
    user_id: int
    user_name: str


class UserInfoApi(JsonApiSpec[UserInfoResult]):

    def __init__(self) -> None:
        super().__init__('https://my.115.com/?ct=ajax&ac=nav')
    
    def _parse_json_result(self, json_obj: JsonResult) -> UserInfoResult:
        data_obj = json_obj['data']
        return UserInfoResult(
            user_id=data_obj['user_id'],
            user_name=data_obj['user_name']
        )
