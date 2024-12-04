__author__ = 'deadblue'

from typing import Dict, List, Sequence

from py115.lowlevel.types.common import CommonParams
from py115.lowlevel.types.offline import (
    TaskInfo, 
    OfflineListResult, 
    OfflineClearFlag,
    OfflineErrorReason,
    OfflineAddResult,
)
from ._base import (
    JsonApiSpec, JsonResult, M115ApiSpec, VoidApiSpec
)
from ._error import (
    OFFLINE_LINK_INVALID, OFFLINE_TASK_EXISTED
)


class OfflineListApi(JsonApiSpec[OfflineListResult]):

    _page: int

    def __init__(self, page_num: int = 1) -> None:
        super().__init__(
            'https://lixian.115.com/lixian/?ct=lixian&ac=task_lists'
        )
        self._page = page_num
        self.query['page'] = str(self._page)

    def _parse_json_result(self, json_obj: JsonResult) -> OfflineListResult:
        result = OfflineListResult(
            page_num=json_obj['page'],
            page_count=json_obj['page_count'],
            page_size=json_obj['page_row'],
            quota_total=json_obj['total'],
            quota_remain=json_obj['quota'],
            task_count=json_obj['count'],
            tasks=[
                TaskInfo(task_obj)
                for task_obj in json_obj['tasks']
            ]
        )
        return result

    def set_page(self, page_num: int):
        self.query['page'] = str(page_num)


class OfflineDeleteApi(VoidApiSpec):

    def __init__(
            self, 
            info_hashes: Sequence[str], 
            delete_files: bool = False
        ) -> None:
        super().__init__(
            'https://lixian.115.com/lixian/?ct=lixian&ac=task_del'
        )
        for index, info_hash in enumerate(info_hashes):
            key = f'hash[{index}]'
            self.form[key] = info_hash
        self.form['flag'] = '1' if delete_files else '0'


class OfflineClearApi(VoidApiSpec):
    
    def __init__(self, flag: OfflineClearFlag = OfflineClearFlag.DONE) -> None:
        super().__init__(
            'https://lixian.115.com/lixian/?ct=lixian&ac=task_clear'
        )
        self.form['flag'] = str(flag.value)


_add_error_mapping: Dict[int, OfflineErrorReason] = {
    OFFLINE_LINK_INVALID: OfflineErrorReason.LINK_INVALID,
    OFFLINE_TASK_EXISTED: OfflineErrorReason.TASK_EXISTED
}


class OfflineAddUrlsApi(M115ApiSpec[List[OfflineAddResult]]):

    def __init__(
            self, 
            cp: CommonParams, 
            urls: Sequence[str],
            save_dir_id: str | None = None
        ) -> None:
        super().__init__(
            'https://lixian.115.com/lixianssp/?ac=add_task_urls'
        )
        self.form.update({
            'ac': 'add_task_urls',
            'app_ver': cp.app_ver,
            'uid': cp.user_id
        })
        for index, url in enumerate(urls):
            key = f'url[{index}]'
            self.form[key] = url
        if save_dir_id is not None:
            self.form['wp_path_id'] = save_dir_id

    def _parse_m115_result(self, m115_obj: JsonResult) -> List[OfflineAddResult]:
        result = []
        for ar in m115_obj['result']:
            error_code = ar['errcode']
            if error_code == 0:
                result.append(OfflineAddResult(
                    info_hash=ar['info_hash'],
                    url=ar['url']
                ))
            else:
                result.append(OfflineAddResult(
                    reason=_add_error_mapping.get(error_code, OfflineErrorReason.UNKNOWN),
                    url=ar['url']
                ))
        return result
