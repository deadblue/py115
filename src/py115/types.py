__author__ = 'deadblue'

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, TypeAlias

from py115.lowlevel.types import (
    QrcodeClient, 
    FileInfo,
    TaskStatus,
    TaskInfo
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


@dataclass(init=False)
class UploadTicket:
    """
    UploadTicket contains required parameters to upload a file to 
    cloud storage.

    Please check examples for detial usage.
    """

    is_done: bool
    """Is file already uploaded."""

    pickcode: Optional[str]
    """Pick-code to download file."""

    oss_endpoint: str
    """OSS endpoint address."""

    oss_key_id: str

    oss_key_secret: str

    oss_security_token: str

    bucket_name: str
    """OSS bucket name."""

    object_key: str
    """OSS object key."""

    callback_url: str

    callback_var: str

    expiration: datetime
    """Expiration time of this ticket."""

    def __new__(cls) -> "UploadTicket":
        ret = object.__new__(cls)
        # TODO: Fill fields
        return ret

    def __bool__(self) -> bool:
        return datetime.now() < self.expiration


__all__ = [
    'QrcodeClient',
    'File',
    'TaskStatus',
    'Task'
]