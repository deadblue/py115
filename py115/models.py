__author__ = 'deadblue'

import datetime

from py115.internal.api import time


class File:
    
    """
    File represents a cloud file.
    """

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
        self._time = time.parse_datetime_str(raw.get('t'))

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


class Task:

    def __init__(self, raw: dict) -> None:
        self._info_hash = raw.get('info_hash')
        self._name = raw.get('name')
        self._size = raw.get('size')
        self._status = raw.get('status')

    @property
    def info_hash(self) -> str:
        return self._info_hash

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def size(self) -> int:
        return self._size

    @property
    def is_running(self) -> bool:
        return self._status == 1

    @property
    def is_done(self) -> bool:
        return self._status == 2

    @property
    def is_failed(self) -> bool:
        return self._status == -1

    def __repr__(self) -> str:
        return '%s - %s' % (self._info_hash, self._name)


class DownloadTicket:

    def __init__(self, raw: dict) -> None:
        self._file_name = raw.get('file_name', '')
        self._file_size = int(raw.get('file_size', 0))
        self._url = raw.get('url', {}).get('url', '')
        self._headers = {}

    @property
    def url(self) -> str:
        return self._url
    
    @property
    def headers(self) -> dict:
        return self._headers

    @property
    def file_name(self) -> str :
        return self._file_name

    @property
    def file_size(self) -> int:
        return self._file_size
    
    def __str__(self) -> str:
        return self._url


class UploadTicket:

    def __init__(self) -> None:
        pass
