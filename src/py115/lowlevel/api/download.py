__author__ = 'deadblue'

from py115.lowlevel.types.download import DownloadResult
from py115.lowlevel._utils import now_str
from ._base import M115ApiSpec, JsonResult


class DownloadApi(M115ApiSpec[DownloadResult]):
    
    def __init__(self, pickcode: str) -> None:
        super().__init__('https://proapi.115.com/app/chrome/downurl')
        self.query['t'] = now_str()
        self.form['pickcode'] = pickcode

    def _parse_m115_result(self, m115_obj: JsonResult) -> DownloadResult:
        if len(m115_obj) == 0:
            return None
        file_id, down_info = m115_obj.popitem()
        return DownloadResult(
            file_id=file_id,
            file_name=down_info.get('file_name'),
            file_size=down_info.get('file_size'),
            url=down_info['url']['url']
        )
