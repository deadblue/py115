__author__ = 'deadblue'

import typing

from py115._internal.api import offline
from py115._internal.protocol.client import Client

from py115.types import ClearFlag, Task


class OfflineService:
    """
    Manage offline tasks.
    """

    _client: Client = None
    _app_ver: str = None
    _user_id: str = None

    @classmethod
    def _create(cls, client: Client, app_ver: str, user_id: str):
        s = cls()
        s._client = client
        s._app_ver = app_ver
        s._user_id = user_id
        return s

    def list(self) -> typing.Generator[Task, None, None]:
        """
        Get all offline tasks.
        """
        spec = offline.ListApi()
        while True:
            result = self._client.execute_api(spec)
            for t in result['tasks']:
                yield Task(t)
            page, page_count = result['page'], result['page_count']
            if page < page_count:
                spec.set_page(page + 1)
            else:
                break

    def add_urls(self, *urls: str):
        """
        Add tasks by download URL.
        """
        add_results = self._client.execute_api(offline.AddUrlsApi(
            self._app_ver, self._user_id, *urls
        ))
        return [Task(r) for r in add_results]

    def delete(self, *task_ids: str):
        """
        Delete tasks by task ID.
        """
        self._client.execute_api(offline.DeleteApi(*task_ids))

    def clear(self, flag: ClearFlag = ClearFlag.Done):
        """
        Clear tasks.
        """
        self._client.execute_api(offline.ClearApi(flag.value))
