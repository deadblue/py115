__author__ = 'deadblue'

from py115._internal.protocol import api


class AddApi(api.ApiSpec):

    def __init__(self, parent_id: str, dir_name: str) -> None:
        super().__init__('https://webapi.115.com/files/add')
        self.update_from({
            'pid': parent_id,
            'cname': dir_name
        })
    
    def parse_result(self, result: dict) -> dict:
        err_code = api.find_error_code(result)
        if err_code != 0:
            raise api.ApiException(err_code)
        return {
            'cid': result.get('cid'),
            'n': result.get('cname')
        }


class SortApi(api.ApiSpec):

    def __init__(self, dir_id: str, order: str, asc: bool = False) -> None:
        super().__init__('https://webapi.115.com/files/order')
        self.update_from({
            'file_id': dir_id,
            'user_order': order,
            'user_asc': '1' if asc else '0',
            'fc_mix': '0'
        })
