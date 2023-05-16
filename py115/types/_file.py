__author__ = 'deadblue'

from datetime import datetime

from py115.types import _utils as utils


class File:
    """
    File represents a cloud file.
    """

    def __init__(self, raw: dict) -> None:
        category_id = raw.get('cid')
        file_id = raw.get('fid')
        parent_id = raw.get('pid')
        self._is_dir = file_id is None
        if self._is_dir:
            self._file_id = category_id
            self._parent_id = parent_id
            self._size = 0
            self._sha1, self._pc = None, None
        else:
            self._file_id = file_id
            self._parent_id = category_id
            self._size = raw.get('s')
            self._sha1 = raw.get('sha')
            self._pc = raw.get('pc')
        self._name = raw.get('n')
        self._time = utils.parse_datetime_str(raw.get('t'))

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
    def modified_time(self) -> datetime:
        return self._time
    
    @property
    def sha1(self) -> str:
        return self._sha1

    @property
    def pickcode(self) -> str:
        return self._pc

    @property
    def is_dir(self) -> bool:
        return self._is_dir

    def __repr__(self) -> str:
        return f'ID={self._file_id}, Name={self._name}'

    def __str__(self) -> str:
        if self._is_dir:
            return f'{self._name}/'
        else:
            return self._name


class DownloadTicket:
    """
    DownloadTicket contains required parameters to download a file 
    from cloud storage.
    """

    def __init__(self, raw: dict, headers: dict = {}) -> None:
        self._name = raw.get('file_name', '')
        self._size = int(raw.get('file_size', 0))
        self._url = raw.get('url', {}).get('url', '')
        self._headers = headers

    @property
    def url(self) -> str:
        return self._url
    
    @property
    def headers(self) -> dict:
        return self._headers

    @property
    def file_name(self) -> str :
        return self._name

    @property
    def file_size(self) -> int:
        return self._size
    
    def __str__(self) -> str:
        return self._url


class UploadTicket:

    _done: bool = None
    _bucket: str = None
    _object: str = None
    _callback_url: str = None
    _callback_var: str = None
    _access_key_id: str = None
    _access_key_secret: str = None
    _security_token: str = None

    def __init__(self, raw: dict) -> None:
        self._done = raw.get('done', False)
        self._bucket = raw.get('bucket', None)
        self._object = raw.get('object', None)
        self._callback_url = raw.get('callback', None)
        self._callback_var = raw.get('callback_var', None)

    def set_oss_token(self, raw:dict):
        self._access_key_id = raw.get('access_key_id', None)
        self._access_key_secret = raw.get('access_key_secret', None)
        self._security_token = raw.get('security_token', None)

    @property
    def is_done(self) -> bool:
        return self._done

    @property
    def bucket(self) -> str:
        return self._bucket

    @property
    def object(self) -> str:
        return self._object

    @property
    def callback_url(self) -> str:
        return self._callback_url
    
    @property
    def callback_var(self) -> str:
        return self._callback_var
