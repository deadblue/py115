__author__ = 'deadblue'

import typing

from py115.internal.protocol import ApiSpec, M115ApiSpec, ApiException


class ListApi(ApiSpec):
    
    def __init__(self, page: int = 1) -> None:
        super().__init__('https://lixian.115.com/lixian/', True)
        self._qs = {
            'ct': 'lixian',
            'ac': 'task_lists',
            'page': page
        }

    def set_page(self, page: int):
        self._qs['page'] = page

    def parse_result(self, result: dict) -> typing.Any:
        if result.get('state', False):
            return {
                'page_count': result.get('page_count', 1),
                'tasks': result.get('tasks', [])
            }
        else:
            raise ApiException(result.get('errno', -1))


class DeleteApi(ApiSpec):

    def __init__(self) -> None:
        super().__init__('https://lixian.115.com/lixian/', True)
        self._qs = {
            'ct': 'lixian',
            'ac': 'task_del'
        }


class ClearApi(ApiSpec):

    def __init__(self, flag: int) -> None:
        super().__init__('https://lixian.115.com/lixian/', True)
        self._qs = {
            'ct': 'lixian',
            'ac': 'task_clear'
        }
        self._form = {
            'flag': flag
        }


class AddUrlsApi(M115ApiSpec):
    
    def __init__(self) -> None:
        super().__init__('https://lixian.115.com/lixianssp/?ac=add_task_urls', True)
        self._form = {
            'ac': 'add_task_urls'
        }
