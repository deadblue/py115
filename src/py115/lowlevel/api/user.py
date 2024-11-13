__author__ = 'deadblue'

from py115.lowlevel.types.user import UserInfo
from ._base import JsonApiSpec, JsonResult


class UserInfoApi(JsonApiSpec[UserInfo]):

    def __init__(self) -> None:
        super().__init__('https://my.115.com/?ct=ajax&ac=nav')
    
    def _parse_json_result(self, json_obj: JsonResult) -> UserInfo:
        data_obj = json_obj['data']
        return UserInfo(
            user_id=data_obj['user_id'],
            name=data_obj['user_name'],
            is_vip=data_obj.get('vip', 0) == 1
        )
