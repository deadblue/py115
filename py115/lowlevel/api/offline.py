__author__ = 'deadblue'

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Sequence

from ..types import CommonParams
from ._base import (
    JsonApiSpec, JsonResult, M115ApiSpec, VoidApiSpec
)


@dataclass(init=False)
class TaskObject:
    info_hash: str
    url: str
    name: str
    size: int
    add_time: int
    status: int
    percent: float
    file_id: str
    dir_id: str

    def __new__(cls, json_obj: JsonResult):
        ret = object.__new__(cls)
        ret.info_hash = json_obj.get('info_hash')
        ret.url = json_obj.get('url')
        ret.name = json_obj.get('name')
        ret.size = json_obj.get('size', 0)
        ret.add_time = json_obj.get('add_time', 0)
        ret.status = json_obj.get('status', -1)
        ret.percent = float(json_obj.get('percentDone', 0))
        ret.file_id = json_obj.get('delete_file_id', '')
        ret.dir_id = json_obj.get('file_id', '')
        return ret


@dataclass
class OfflineListResult:
    page_num: int
    page_count: int
    page_size: int
    quota_total: int
    quota_remain: int
    task_count: int
    tasks: List[TaskObject]


class OfflineListApi(JsonApiSpec[OfflineListResult]):

    _page: int

    def __init__(self, page_num: int = 1) -> None:
        super().__init__(
            'https://lixian.115.com/lixian/?ct=lixian&ac=task_lists'
        )
        self._page = page_num
        self.query['page'] = str(self._page)

    def _parse_json_result(self, json_obj: JsonResult) -> OfflineListResult:
        return OfflineListResult(
            page_num=json_obj['page'],
            page_count=json_obj['page_count'],
            page_size=json_obj['page_row'],
            quota_total=json_obj['total'],
            quota_remain=json_obj['quota'],
            task_count=json_obj['count'],
            tasks=[
                TaskObject(task_obj) 
                for task_obj in json_obj['tasks']
            ]
        )

    def next_page(self):
        self._page += 1
        self.query['page'] = str(self._page)


class OfflineDeleteApi(VoidApiSpec):

    def __init__(self, info_hashes: Sequence[str], delete_files: bool = False) -> None:
        super().__init__(
            'https://lixian.115.com/lixian/?ct=lixian&ac=task_del'
        )
        for index, info_hash in enumerate(info_hashes):
            key = f'hash[{index}]'
            self.form[key] = info_hash
        self.form['flag'] = '1' if delete_files else '0'


class OfflineClearFlag(Enum):
    DONE = 0
    ALL = 1
    FAILED = 2
    RUNNING = 3
    DONE_WITH_DELETE = 4
    ALL_WITH_DELETE = 5


class OfflineClearApi(VoidApiSpec):
    
    def __init__(self, flag: OfflineClearFlag = OfflineClearFlag.DONE) -> None:
        super().__init__(
            'https://lixian.115.com/lixian/?ct=lixian&ac=task_clear'
        )
        self.form['flag'] = str(flag.value)


@dataclass
class OfflineAddUrlResult:
    info_hash: str
    url: Optional[str] = None
    # TODO: Add more fields


class OfflineAddUrlsApi(M115ApiSpec[List[OfflineAddUrlResult]]):

    def __init__(self, cp: CommonParams, urls: Sequence[str]) -> None:
        super().__init__(
            'https://lixian.115.com/lixianssp/?ac=add_task_urls', True
        )
        self.form.update({
            'ac': 'add_task_urls',
            'app_ver': cp.app_ver,
            'uid': cp.user_id
        })
        for index, url in enumerate(urls):
            key = f'url[{index}]'
            self.form[key] = url

    def _parse_m115_result(self, m115_obj: JsonResult) -> List[OfflineAddUrlResult]:
        result: List[OfflineAddUrlResult] = []
        for task in m115_obj['result']:
            result.append(OfflineAddUrlResult(
                info_hash=task['info_hash'],
                url=task.get('url', None)
            ))
        return result
