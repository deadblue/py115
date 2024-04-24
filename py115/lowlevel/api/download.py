__author__ = 'deadblue'

import time
from dataclasses import dataclass
from typing import Any, Dict

from ._m115 import M115ApiSpec


@dataclass
class DownloadResult:
    file_id: str
    file_name: str
    file_size: int
    url: str


class DownloadApi(M115ApiSpec[DownloadResult]):
    
    def __init__(self, pickcode: str) -> None:
        super().__init__('https://proapi.115.com/app/chrome/downurl')
        self.query['t'] = int(time.time())
        self.form['pickcode'] = pickcode

    def _parse_m115_result(self, m115_obj: Dict[str, Any]) -> DownloadResult:
        if len(m115_obj) == 0:
            return None
        file_id, down_info = m115_obj.popitem()
        return DownloadResult(
            file_id=file_id,
            file_name=down_info.get('file_name'),
            file_size=down_info.get('file_size'),
            url=down_info['url']['url']
        )