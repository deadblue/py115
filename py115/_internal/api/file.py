__author__ = 'deadblue'

import time

from py115._internal.protocol import api


class ListApi(api.ApiSpec):

    def __init__(self, dir_id: str) -> None:
        super().__init__(None)
        self.update_qs({
            'aid': '1',
            'cid': dir_id,
            'o': 'user_ptime',
            'asc': '0',
            'offset': '0',
            'limit': '115',
            'show_dir': '1',
            'snap': '0',
            'natsort': '1',
            'format': 'json',
        })

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
            err_code = api.find_error_code(result)
            if err_code == 20130827:
                self._qs.update({
                    'o': result['order'],
                    'asc': result['is_asc'],
                })
                raise api.RetryException()
            else:
                raise api.ApiException(err_code)

    def set_offset(self, offset: int):
        self.update_qs({
            'offset': str(offset)
        })


class DeleteApi(api.ApiSpec):

    def __init__(self, parent_id: str, *file_ids: str) -> None:
        super().__init__('https://webapi.115.com/rb/delete')
        self.update_from({
            'pid': parent_id,
            'fid': file_ids,
            'ignore_warn': '1'
        })


class MoveApi(api.ApiSpec):

    def __init__(self, parent_id: str, *file_ids: str) -> None:
        super().__init__('https://webapi.115.com/files/move')
        self.update_from({
            'pid': parent_id,
            'fid': file_ids
        })


class RenameApi(api.ApiSpec):

    def __init__(self, file_id: str, new_name: str) -> None:
        super().__init__('https://webapi.115.com/files/batch_rename')
        key = 'files_new_name[%s]' % file_id
        self.update_from({
            key: new_name
        })


class DownloadApi(api.M115ApiSpec):

    def __init__(self, pickcode: str) -> None:
        super().__init__('https://proapi.115.com/app/chrome/downurl', True)
        self.update_qs({
            't': int(time.time())
        })
        self.update_from({
            'pickcode': pickcode
        })