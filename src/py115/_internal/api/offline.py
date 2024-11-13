__author__ = 'deadblue'

import typing

from py115._internal.api import m115
from py115._internal.protocol import api


class ListApi(api.ApiSpec):
    
    def __init__(self, page: int = 1) -> None:
        super().__init__('https://lixian.115.com/lixian/', True)
        self.update_qs({
            'ct': 'lixian',
            'ac': 'task_lists',
            'page': page
        })

    def set_page(self, page: int):
        self.update_qs({
            'page': page
        })

    def parse_result(self, result: dict) -> typing.Any:
        error_code = api.find_error_code(result)
        if error_code != 0:
            raise api.ApiException(error_code)
        tasks = result.get('tasks', None)
        return {
            'page_count': result.get('page_count', 1),
            'page': result.get('page', 1),
            'task_count': result.get('count', 0),
            'tasks': tasks or []
        }


class DeleteApi(api.ApiSpec):

    def __init__(self, task_ids: typing.Iterable[str]) -> None:
        super().__init__('https://lixian.115.com/lixian/', True)
        self.update_qs({
            'ct': 'lixian',
            'ac': 'task_del'
        })
        self.update_from({
            'hash': task_ids,
            'flag': '0',
        })


class ClearApi(api.ApiSpec):

    def __init__(self, flag: int) -> None:
        super().__init__('https://lixian.115.com/lixian/', True)
        self.update_qs({
            'ct': 'lixian',
            'ac': 'task_clear'
        })
        self.update_from({
            'flag': flag
        })


class AddUrlsApi(m115.M115ApiSpec):
    
    def __init__(self, app_ver: str, user_id: int, urls: typing.Iterable[str], **kwargs) -> None:
        super().__init__('https://lixian.115.com/lixianssp/', True)
        self.update_qs({
            'ac': 'add_task_urls'
        })
        params = {
            'ac': 'add_task_urls',
            'app_ver': app_ver,
            'uid': user_id,
            'url': urls
        }
        save_dir_id = kwargs.pop('save_dir_id', None)
        if save_dir_id is not None:
            params['wp_path_id'] = save_dir_id
        self.update_from(params)
    
    def parse_result(self, result: dict):
        result = super().parse_result(result)
        return result['result']
