__author__ = 'deadblue'

import typing
from py115.internal.protocol import api


class AddApi(api.ApiSpec):

    def __init__(self, parent_id: str, dir_name: str) -> None:
        super().__init__('https://webapi.115.com/files/add')
        self.update_from({
            'pid': parent_id,
            'cname': dir_name
        })

    def parse_result(self, result: dict) -> typing.Any:
        # error_code = api.find_error_code(result)
        return super().parse_result(result)


class SortApi(api.ApiSpec):

    def __init__(self, dir_id: str, order: str, asc: bool = False) -> None:
        super().__init__('https://webapi.115.com/files/order')
        self.update_from({
            'file_id': dir_id,
            'user_order': order,
            'user_asc': '1' if asc else '0',
            'fc_mix': '0'
        })