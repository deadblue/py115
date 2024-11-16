__author__ = 'deadblue'

from py115.lowlevel.types.storage import StorageInfo
from ._base import JsonApiSpec, JsonResult


class StorageInfoApi(JsonApiSpec[StorageInfo]):

    def __init__(self) -> None:
        super().__init__('https://webapi.115.com/files/index_info')
    
    def _parse_json_result(self, json_obj: JsonResult) -> StorageInfo:
        space_info = json_obj['data']['space_info']
        return StorageInfo(
            total_size=int(space_info['all_total']['size']),
            remain_size=int(space_info['all_remain']['size']),
            used_size=int(space_info['all_use']['size'])
        )
