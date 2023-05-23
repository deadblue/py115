__author__ = 'deadblue'

from datetime import datetime
from enum import IntEnum

from py115._internal import oss, utils


class Credential:
    """Credential contains required information to identify user.

    Args:
        uid (str): The "UID" value in cookies.
        cid (str): The "CID" value in cookies.
        seid (str): The "SEID" value in cookies.
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
    DownloadTicket contains required parameters to download a file from 
    cloud storage.

    Please check examples for detail usage.
    """

    file_name: str
    """Base name of the file."""

    file_size: int
    """Size of the file."""

    url: str
    """Download URL."""

    headers: dict
    """Required headers that should be used with download URL."""

    @classmethod
    def _create(cls, raw: dict, header: dict):
        r = cls()
        r.file_name = raw.get('file_name')
        r.file_size = raw.get('file_size')
        r.url = raw.get('url')
        r.headers = header.copy()
        return r

    def __str__(self) -> str:
        return self.url


class UploadTicket:
    """
    UploadTicket contains required parameters to upload a file to 
    cloud storage.

    Please check examples for detial usage.
    """

    is_done: bool
    """Is file already uploaded."""

    oss_endpoint: str
    """OSS endpoint address."""

    oss_token: dict
    """OSS token"""

    bucket_name: str
    """OSS bucket name."""

    object_key: str
    """OSS object key."""

    headers: dict
    """Required headers that should be used in upload."""

    expiration: datetime
    """Expiration time of this ticket."""

    @classmethod
    def _create(cls, raw: dict, token: dict):
        r = cls()
        r.is_done = raw['done']
        if not r.is_done:
            r.oss_endpoint = oss.ENDPOINT
            r.oss_token = {
                'access_key_id': token.get('access_key_id'),
                'access_key_secret': token.get('access_key_secret'),
                'security_token': token.get('security_token')
            }
            r.bucket_name = raw.get('bucket')
            r.object_key = raw.get('object')
            r.headers = {
                'x-oss-callback': oss.encode_header_value(raw.get('callback')),
                'x-oss-callback-var': oss.encode_header_value(raw.get('callback_var'))
            }
            r.expiration = token.get('expiration')
        return r
    
    def is_valid(self) -> bool:
        """Check whether the ticket is valid.

        Returns:
            bool: Valid flag.
        """
        return datetime.now() < self.expiration


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
