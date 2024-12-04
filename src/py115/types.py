__author__ = 'deadblue'

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, TypeAlias

from py115.lowlevel.types import (
    QrcodeClient, 
    FileInfo,
    TaskStatus,
    TaskInfo,
    OfflineClearFlag,
)


File: TypeAlias = FileInfo

Task: TypeAlias = TaskInfo


class QrcodeSession:
    """QRcode login session."""

    _client: QrcodeClient
    _uid: str
    _time: int
    _sign: str
    _image_data: bytes

    def __init__(
            self,
            client: QrcodeClient, 
            uid: str, 
            time: int, 
            sign: str, 
            image_data: bytes
        ) -> None:
        self._client = client
        self._uid = uid
        self._time = time
        self._sign = sign
        self._image_data = image_data

    @property    
    def image_data(self) -> bytes:
        """QRcode image data"""
        return self._image_data


@dataclass
class Credential:
    """Credential contains required information to identify user."""

    uid: str | None
    """
    "UID" cookie value.
    """

    cid: str | None
    """
    "CID" cookie value.
    """

    seid: str | None
    """
    "SEID" cookie value.
    """

    def to_dict(self) -> Dict[str, str]:
        """Convert credential object to dict object.

        Returns:
            Dict: A dict form of cookies.
        """
        return {
            'UID': self.uid,
            'CID': self.cid,
            'SEID': self.seid,
        }

    def __bool__(self) -> bool:
        return self.uid is not None \
            and self.cid is not None \
            and self.seid is not None


@dataclass(init=False)
class DownloadTicket:
    """
    DownloadTicket contains required parameters to download a file from storage.
    """

    file_name: str
    """Base name of the file."""

    file_size: int
    """Size of the file."""

    url: str
    """Download URL."""

    headers: Dict[str, str]
    """Required headers that should be used with download URL."""

    def __init__(self, url: str, file_name: str, file_size: int) -> None:
        self.url = url
        self.file_name = file_name
        self.file_size = file_size
        self.headers = {}


@dataclass(init=False)
class PlayTicket:

    url: str
    """Download URL."""

    headers: dict
    """Required headers that should be used with download URL."""

    def __init__(self, url: str) -> None:
        self.url = url
        self.headers = {}


@dataclass(kw_only=True)
class UploadTicket:
    """
    UploadTicket contains required parameters to upload a file to 
    cloud storage.
    """

    region: str

    endpoint: str

    access_key_id: str

    access_key_secret: str

    security_token: str

    bucket_name: str

    object_key: str

    callback: str

    callback_var: str

    expiration: int
    """Expiration time of this ticket."""

    def __bool__(self) -> bool:
        return datetime.now().timestamp < self.expiration


__all__ = [
    'QrcodeClient',
    'File',
    'TaskStatus',
    'Task',
    'OfflineClearFlag'
]