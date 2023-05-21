__author__ = 'deadblue'

from datetime import datetime
from enum import IntEnum

from py115._internal import utils


class Credential:
    """Credential contains required information to identify user.
    """

    _uid: str = None
    _cid: str = None
    _seid: str = None

    def __init__(self, uid: str = None, cid: str = None, seid: str = None) -> None:
        self._uid = uid
        self._cid = cid
        self._seid = seid

    @classmethod
    def from_dict(cls, d: dict):
        """Create Credential from a dict object.

        Args:
            d (dict): Dict object.

        Returns:
            py115.types.Credential: Credential object.
        """
        if len(d) == 0 or not ('UID' in d and 'CID' in d and 'SEID' in d):
            return None
        return Credential(
            uid=d.get('UID'),
            cid=d.get('CID'),
            seid=d.get('SEID')
        )

    def to_dict(self) -> dict:
        """Convert credential object to dict object.

        Returns:
            dict: Dict object.
        """
        return {
            'UID': self._uid,
            'CID': self._cid,
            'SEID': self._seid,
        }

    def __repr__(self) -> str:
        return f'UID={self._uid}, CID={self._cid}, SEID={self._seid}'


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

    def _set_oss_token(self, raw:dict):
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

    @property
    def oss_token(self) -> dict:
        return {
            'access_key_id': self._access_key_id,
            'access_key_secret': self._access_key_secret,
            'security_token': self._security_token
        }


class ClearFlag(IntEnum):
    Done = 0
    All = 1
    Failed = 2
    Running = 3


class Task:
    """
    Task represents an offline task.
    """

    def __init__(self, raw: dict):
        self._id = raw.get('info_hash')
        self._name = raw.get('name', None)
        self._size = raw.get('size', -1)
        self._time = utils.make_datetime(raw.get('add_time', 0))
        self._precent = float(raw.get('percentDone', 0))
        self._status = raw.get('status', 0)
        # Get File ID
        file_id = raw.get('file_id', '')
        del_file_id = raw.get('delete_file_id', '')
        self._file_id = del_file_id
        self._is_dir = file_id != '' and file_id == del_file_id

    @property
    def task_id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def size(self) -> int:
        return self._size

    @property
    def added_time(self) -> datetime:
        return self._time

    @property
    def percent(self) -> float:
        return self._precent

    @property
    def file_id(self) -> str:
        return self._file_id

    @property
    def file_is_dir(self) -> bool:
        return self._is_dir

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
        return f'ID={self._id}, Name="{self._name}", Size={self._size}, Percent={self._precent:0.2f}'
