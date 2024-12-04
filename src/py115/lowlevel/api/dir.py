__author__ = 'deadblue'

from py115.lowlevel.types.dir import DirOrder
from ._base import (
    JsonApiSpec, JsonResult, VoidApiSpec
)


class DirMakeApi(JsonApiSpec[str]):

    def __init__(self, parent_id: str, dir_name: str) -> None:
        super().__init__(
            api_url='https://webapi.115.com/files/add'
        )
        self.form.update({
            'pid': parent_id,
            'cname': dir_name
        })

    def _parse_json_result(self, json_obj: JsonResult) -> str:
        return json_obj.get('file_id')


class DirSetOrderApi(VoidApiSpec):

    def __init__(self, dir_id: str, order: DirOrder, is_asc: bool) -> None:
        super().__init__('https://webapi.115.com/files/order')
        self.form.update({
            'file_id': dir_id,
            'user_order': order,
            'user_asc': '1' if is_asc else '0',
            'fc_mix': 0
        })


class DirGetIdApi(JsonApiSpec[str]):

    def __init__(self, path: str):
        super().__init__('https://webapi.115.com/files/getid')
        self.query['path'] = path
    
    def _parse_json_result(self, json_obj: JsonResult) -> str:
        return json_obj.get('id')
