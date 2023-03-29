__author__ = 'deadblue'

import datetime

import pytz

from py115.internal.webapi.client import ApiException, ResponseParser

_tz_cst = pytz.FixedOffset(480)

def _parse_file_time(s: str) -> datetime.datetime:
    if '-' in s:
        t = datetime.datetime.strptime(
            s, '%Y-%m-%d %H:%M'
        )
        t.replace(tzinfo=_tz_cst)
        return t
    else:
        return  datetime.datetime.fromtimestamp(
            float(s), tz=_tz_cst
        )

class File:

    def __init__(self, raw: dict) -> None:
        category_id = raw.get('cid')
        file_id = raw.get('fid')
        parent_id = raw.get('pid')
        if file_id is None:
            self._file_id = category_id
            self._parent_id = parent_id
            self._is_dir = True
        else:
            self._file_id = file_id
            self._parent_id = category_id
            self._is_dir = False
        self._name = raw.get('n')
        self._size = 0 if self._is_dir else raw.get('s')
        self._sha1 = None if self._is_dir else raw.get('sha')
        self._pc = None if self._is_dir else raw.get('pc')
        self._time = _parse_file_time(raw.get('t'))

    @property
    def is_dir(self) -> bool:
        return self._is_dir

    @property
    def file_id(self) -> str:
        return self._file_id
    
    @property
    def parent_id(self) -> str:
        return self._parent_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def size(self) -> int:
        return self._size
    
    @property
    def modified_time(self) -> datetime.datetime:
        return self._time
    
    @property
    def sha1(self) -> str:
        return self._sha1

    @property
    def pickcode(self) -> str:
        return self._pc
    
    def __str__(self) -> str:
        return self._name


class FileListException(ApiException):

    def __init__(self, code: int, order: str, is_asc: int, *args: object) -> None:
        super().__init__(code, *args)
        self._order = order
        self._is_asc = is_asc

    @property
    def order(self) -> str:
        return self._order

    @property
    def is_asc(self) -> int:
        return self._is_asc


class FileListResponseParser(ResponseParser):

    def __init__(self) -> None:
        super().__init__()
    
    def validate(self, result: dict):
        if result.get('state', False):
            return
        error_code = result.get('errNo', 999999)
        if error_code == 20130827:
            order, is_asc = result.get('order'), result.get('is_asc')
            raise FileListException(error_code, order, is_asc)
        else:
            raise ApiException(error_code)

    def extract(self, result: dict) -> dict:
        data = result.get('data', [])
        ret = {
            'count': result.get('count'),
            'offset': result.get('offset'),
            'files': [ File(r) for r in data ]
        }
        return ret
