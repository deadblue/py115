__author__ = 'deadblue'

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

from ..protocol import RetryException
from ._json import JsonApiSpec, JsonResult, VoidApiSpec
from .exceptions import ApiException


@dataclass(init=False)
class FileObject:
    is_dir: bool 
    file_id: str
    parent_id: str
    name: str
    pickcode: str
    size: int = 0
    sha1: Optional[str] = None
    # created_time: Optional[int]
    # modified_time: Optional[int]
    # opened_time: Optional[int]
    media_duration: Optional[int] = None
    video_definition: Optional[int] = None

    def __new__(cls, json_obj: Dict[str, Any]):
        ret = object.__new__(cls)
        ret.is_dir = 'fid' not in json_obj
        ret.name = json_obj['n']
        ret.pickcode = json_obj['pc']
        if ret.is_dir:
            ret.file_id = json_obj['cid']
            ret.parent_id = json_obj['pid']
        else:
            ret.file_id = json_obj['fid']
            ret.parent_id = json_obj['cid']
            ret.size = json_obj['s']
            ret.sha1 = json_obj['sha']
            ret.media_duration = json_obj.get('play_long', None)
            ret.video_definition = json_obj.get('vdi', None)
        return ret


@dataclass
class FileListResult:
    files: List[FileObject]
    order_mode: str
    order_asc: int
    offset: int
    limit: int
    count: int


class FileListApi(JsonApiSpec[FileListResult]):

    def __init__(self, dir_id: str, offset: int = 0, limit: int = 115) -> None:
        super().__init__('')
        self.query.update({
            'aid': '1',
            'cid': dir_id,
            'show_dir': '1',
            'o': 'user_ptime',
            'asc': '1',
            'offset': f'{offset}',
            'limit': f'{limit}',
            'fc_mix': '0',
            'natsort': '1',
            'format': 'json'
        })

    def url(self) -> str:
        order_mode = self.query.get('o', 'user_ptime')
        if order_mode == 'file_name':
            return 'https://aps.115.com/natsort/files.php'
        else:
            return 'https://webapi.115.com/files'
    
    def parse_result(self, result: bytes) -> FileListResult:
        try:
            return super().parse_result(result)
        except ApiException as ex:
            if ex.error_code == 20130827:
                self.query.update({
                    'o': ex.raw_result.get('order'),
                    'asc': str(ex.raw_result.get('is_asc'))
                })
                raise RetryException
            else:
                raise ex

    def _parse_json_result(self, obj: JsonResult) -> FileListResult:
        ret = FileListResult(
            files=[],
            order_mode=obj.get('order'),
            order_asc=obj.get('is_ac'),
            offset=obj.get('offset'),
            limit=obj.get('limit'),
            count=obj.get('count')
        )
        for file_obj in obj['data']:
            ret.files.append(FileObject(file_obj))
        return ret


class FileDeleteApi(VoidApiSpec):

    def __init__(self, file_ids: Sequence[str]) -> None:
        super().__init__('https://webapi.115.com/rb/delete')
        for index, file_id in enumerate(file_ids):
            sub_key = f'fid[{index}]'
            self.form[sub_key] = file_id
        self.form['ignore_warn'] = '1'


class FileMoveApi(VoidApiSpec):

    def __init__(self, target_dir_id: str, file_ids: Sequence[str]) -> None:
        super().__init__('https://webapi.115.com/files/move')
        self.form['pid'] = target_dir_id
        for index, file_id in enumerate(file_ids):
            sub_key = f'fid[{index}]'
            self.form[sub_key] = file_id
        self.form['ignore_warn'] = '1'
