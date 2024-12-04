__author__ = 'deadblue'

from abc import ABC
from typing import Dict, Sequence

from py115.lowlevel.exceptions import RetryException
from py115.lowlevel.types.dir import DirOrder
from py115.lowlevel.types.file import (
    FileInfo, FileListResult, FileType
)
from ._base import (
    JsonApiSpec, JsonResult, VoidApiSpec
)
from ._error import FILE_ORDER_INVALID


DEFAULT_FILE_LIST_LIMIT = 32


class BaseFileListApi(JsonApiSpec[FileListResult], ABC):

    _offset: int = 0
    _limit: int = 0

    def __init__(
            self, 
            api_url: str, 
            offset: int, 
            limit: int
        ):
        super().__init__(api_url)
        self._offset, self._limit = offset, limit
        self.query.update({
            'offset': str(offset),
            'limit': str(limit)
        })

    def _get_offset(self) -> int:
        return self._offset
    
    def _set_offset(self, value: int):
        self._offset = value
        self.query['offset'] = str(value)

    offset = property(
        fget=_get_offset, 
        fset=_set_offset
    )

    @property
    def limit(self) -> int:
        return self._limit

    def _parse_json_result(self, json_obj: JsonResult) -> FileListResult:
        return FileListResult(
            offset=json_obj.get('offset'),
            limit=json_obj.get('page_size'),
            order=json_obj.get('order'),
            asc=json_obj.get('is_asc'),
            count=json_obj.get('count'),
            files=[
                FileInfo(file_obj) for file_obj in json_obj['data']
            ]
        )

class FileListApi(BaseFileListApi):

    _order: DirOrder = 'user_ptime'

    def __init__(
            self, 
            dir_id: str, 
            offset: int = 0, 
            limit: int = DEFAULT_FILE_LIST_LIMIT
        ) -> None:
        super().__init__('', offset, limit)
        self.query.update({
            'aid': '1',
            'cid': dir_id,
            'show_dir': '1',
            'o': self._order,
            'asc': '1',
            'fc_mix': '0',
            'natsort': '1',
            'format': 'json'
        })

    @property
    def url(self) -> str:
        if self._order == 'file_name':
            return 'https://aps.115.com/natsort/files.php'
        else:
            return 'https://webapi.115.com/files'

    def _get_error_code(self, json_obj: JsonResult) -> int:
        err_code = super()._get_error_code(json_obj)
        if err_code == FILE_ORDER_INVALID:
            self._order = json_obj.get('order')
            self.query.update({
                'o': self._order,
                'asc': str(json_obj.get('is_asc'))
            })
            raise RetryException()
        return err_code


class FileSearchApi(BaseFileListApi):

    def __init__(
            self, 
            keyword: str, 
            dir_id: str = '0', 
            offset: int = 0, 
            limit: int = DEFAULT_FILE_LIST_LIMIT,
            *,
            file_type: FileType | None = None
        ) -> None:
        super().__init__(
            'https://webapi.115.com/files/search', offset, limit
        )
        self.query.update({
            'aid': '1',
            'cid': dir_id,
            'search_value': keyword,
            'format': 'json'
        })
        if file_type is not None:
            self.query['type'] = str(file_type.value)


class FileStaredApi(BaseFileListApi):
    """
    API spec for retrieving stared files.
    """

    def __init__(
            self, 
            offset: int = 0, 
            limit: int = DEFAULT_FILE_LIST_LIMIT,
            *,
            file_type: FileType | None = None
        ) -> None:
        super().__init__(
            'https://webapi.115.com/files', offset, limit
        )
        self.query.update({
            'aid': '1',
            'cid': '0',
            'star': '1',
            'show_dir': '1',
            'format': 'json'
        })
        if file_type is not None:
            self.query['type'] = str(file_type.value)


class FileLabeledApi(BaseFileListApi):
    """
    API spec for retrieving files with specific label.
    """

    def __init__(
            self, 
            label_id: str,
            offset: int = 0, 
            limit: int = DEFAULT_FILE_LIST_LIMIT,
            *,
            file_type: FileType | None = None
        ) -> None:
        super().__init__(
            'https://webapi.115.com/files/search', offset, limit
        )
        self.query.update({
            'aid': '1',
            'cid': '0',
            'file_label': label_id,
            'show_dir': '1',
            'format': 'json'
        })
        if file_type is not None:
            self.query['type'] = str(file_type.value)


class FileGetInfoApi(JsonApiSpec[FileInfo]):
    
    def __init__(self, file_id: str) -> None:
        super().__init__('https://webapi.115.com/files/get_info')
        self.query['file_id'] = file_id
    
    def _parse_json_result(self, json_obj: JsonResult) -> FileInfo:
        return FileInfo(json_obj['data'][0])


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


class FileBatchRenameApi(VoidApiSpec):

    def __init__(self, new_names: Dict[str, str]) -> None:
        super().__init__('https://webapi.115.com/files/batch_rename')
        for file_id, new_name in new_names.items():
            key = f'files_new_name[{file_id}]'
            self.form[key] = new_name


class FileSetStarApi(VoidApiSpec):

    def __init__(self, file_ids: Sequence[str], star: bool) -> None:
        super().__init__('https://webapi.115.com/files/star')
        self.form.update({
            'file_id': ','.join(file_ids),
            'star': '1' if star else '0'
        })


class FileSetLabelsApi(VoidApiSpec):

    def __init__(self, file_id: str, label_ids: Sequence[str]) -> None:
        super().__init__('https://webapi.115.com/files/edit')
        self.form.update({
            'fid': file_id,
            'file_label': ','.join(label_ids) if len(label_ids) > 0 else ''
        })


class FileBatchSetLabelsApi(VoidApiSpec):
    
    def __init__(self, file_ids: Sequence[str], label_ids: Sequence[str]) -> None:
        super().__init__('https://webapi.115.com/files/batch_label')
        self.form.update({
            'file_ids': ','.join(file_ids),
            'file_label': ','.join(label_ids),
            'action': 'reset'
        })


class FileBatchAddLabelsApi(VoidApiSpec):
    
    def __init__(self, file_ids: Sequence[str], label_ids: Sequence[str]) -> None:
        super().__init__('https://webapi.115.com/files/batch_label')
        self.form.update({
            'file_ids': ','.join(file_ids),
            'file_label': ','.join(label_ids),
            'action': 'add'
        })


class FileBatchRemoveLabelsApi(VoidApiSpec):
    
    def __init__(self, file_ids: Sequence[str], label_ids: Sequence[str]) -> None:
        super().__init__('https://webapi.115.com/files/batch_label')
        self.form.update({
            'file_ids': ','.join(file_ids),
            'file_label': ','.join(label_ids),
            'action': 'remove'
        })


class FileSetDescApi(VoidApiSpec):

    def __init__(self, file_id: str, description: str) -> None:
        super().__init__('https://webapi.115.com/files/edit')
        self.form.update({
            'fid': file_id,
            'file_desc': description
        })


class FileGetDescApi(JsonApiSpec[str]):

    def __init__(self, file_id: str) -> None:
        super().__init__('https://webapi.115.com/files/desc')
        self.query.update({
            'file_id': file_id,
            'compat': '1',
            'new_html': '1',
            'format': 'json',
        })
    
    def _parse_json_result(self, json_obj: JsonResult) -> str:
        return json_obj.get('desc')


class FileHideApi(VoidApiSpec):

    def __init__(self, file_ids: Sequence[str], hidden: bool) -> None:
        super().__init__('https://webapi.115.com/files/hiddenfiles')
        for index, file_id in enumerate(file_ids):
            key = f'fid[{index}]'
            self.form[key] = file_id
        self.form['hidden'] = '1' if hidden else '0'


class FileSetTopApi(VoidApiSpec):

    def __init__(self, file_ids: Sequence[str], on_top: bool) -> None:
        super().__init__('https://webapi.115.com/files/top')
        self.form.update({
            'file_id': ','.join(file_ids),
            'top': '1' if on_top else '0'
        })


class FileShowHiddenApi(VoidApiSpec):

    def __init__(self, show_hidden: bool, password: str = None) -> None:
        super().__init__('https://115.com/?ct=hiddenfiles&ac=switching')
        self.form.update({
            'show': '1' if show_hidden else '0',
            'valid_type': '1',
            'safe_pwd': password if password is not None else ''
        })
