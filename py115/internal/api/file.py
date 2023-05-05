__author__ = 'deadblue'

import time

from py115.internal.protocol import ApiException, ApiSpec, M115ApiSpec


class RetryException(ApiException):

    def __init__(self, code: int, *args: object) -> None:
        super().__init__(code, *args)


class ListApi(ApiSpec):

    def __init__(self, dir_id: str) -> None:
        super().__init__(None)
        self._qs = {
            'aid': '1',
            'cid': dir_id,
            'o': 'user_utime',
            'asc': '0',
            'offset': '0',
            'limit': '115',
            'show_dir': '1',
            'snap': '0',
            'natsort': '1',
            'format': 'json',
        }

    @property
    def url(self) -> str:
        order = self._qs.get('o')
        if order == 'file_name':
            return 'https://aps.115.com/natsort/files.php'
        else:
            return 'https://webapi.115.com/files'

    def parse_result(self, result: dict):
        if result.get('state', False):
            return {
                'count': result.get('count'),
                'offset': result.get('offset'),
                'files': result.get('data')
            }
        else:
            err_code = result.get('errNo', -1)
            if err_code == 20130827:
                self._qs.update({
                    'o': result['order'],
                    'asc': result['is_asc'],
                })
                raise RetryException(err_code)
            else:
                raise ApiException(err_code)

    def update_offset(self, offset: int):
        self._qs.update({
            'offset': str(offset)
        })


class DeleteApi(ApiSpec):

    def __init__(self, parent_id: str, *file_ids: str) -> None:
        super().__init__('https://webapi.115.com/rb/delete')
        self._form = {
            'pid': parent_id,
            'ignore_warn': '1'
        }
        for index, file_id in enumerate(file_ids):
            key = 'fid[%d]' % index
            self._form[key] = file_id


class MoveApi(ApiSpec):

    def __init__(self, parent_id: str, *file_ids: str) -> None:
        super().__init__('https://webapi.115.com/files/move')
        self._form = {
            'pid': parent_id,
        }
        for index, file_id in enumerate(file_ids):
            key = 'fid[%d]' % index
            self._form[key] = file_id


class RenameApi(ApiSpec):

    def __init__(self, file_id: str, new_name: str) -> None:
        super().__init__('https://webapi.115.com/files/batch_rename')
        key = 'files_new_name[%s]' % file_id
        self._form[key] = new_name


class OrderApi(ApiSpec):

    def __init__(self, dir_id: str, order: str, asc: bool = False) -> None:
        super().__init__('https://webapi.115.com/files/order')
        self._form = {
            'file_id': dir_id,
            'user_order': order,
            'user_asc': '1' if asc else '0',
            'fc_mix': '0'
        }


class DownloadApi(M115ApiSpec):

    def __init__(self, pickcode: str) -> None:
        super().__init__('https://proapi.115.com/app/chrome/downurl', True)
        self._qs['t'] = int(time.time())
        self._form['pickcode'] = pickcode
