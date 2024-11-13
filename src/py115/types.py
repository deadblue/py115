__author__ = 'deadblue'

from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from typing import Dict, Optional

from py115.lowlevel.api import (
    AppType, FileObject, TaskObject
)


class QrcodeStatus(IntEnum):

    WAITING = 0
    """QRCode is waiting for scanning."""

    DONE = 1
    """QRCode is scanned and approved by user."""

    EXPIRED = -1
    """QRCode is expired."""

    FAILED = -2
    """QRcode is declined by user."""


class QrcodeSession:
    """QRcode login session."""

    _app_type: AppType
    _uid: str
    _time: int
    _sign: str

    image_data: bytes
    """QRcode image data"""

    def __init__(
            self,
            app_type: AppType, 
            uid: str, 
            time: int, 
            sign: str, 
            image_data: bytes
        ) -> None:
        self._app_type = app_type
        self._uid = uid
        self._time = time
        self._sign = sign
        self.image_data = image_data


@dataclass
class Credential:
    """Credential contains required information to identify user."""

    uid: str
    """
    "UID" cookie value.
    """

    cid: str
    """
    "CID" cookie value.
    """

    seid: str
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


class VideoDefinition(IntEnum):

    SD = 1
    """Standard definition."""

    HD = 2
    """High definition."""

    FHD = 3
    """Full high definition."""

    FHD_1080P = 4
    """Another full high definition."""

    UHD_4K = 5
    """Ultra high definition."""

    ORIGINAL = 100
    """Other definition."""


@dataclass(init=False)
class File:
    """File represents a file or directory on cloud."""

    is_dir: bool
    """Indicate whether file is a directory."""

    file_id: str
    """Unique ID of the file or directory on cloud."""

    parent_id: str
    """File ID of the parent directory."""

    name: str
    """Base name."""

    modified_time: datetime
    """Last modified datetime."""

    size: int = 0
    """Size in bytes."""

    sha1: Optional[str] = None
    """SHA-1 hash of the file in HEX encoding."""

    pickcode: Optional[str] = None
    """Pickcode to download the file."""

    media_duration: Optional[int] = None
    """Media duration in seconds for audio/video file."""

    video_definition: Optional[VideoDefinition] = None
    """Video definition"""

    def __new__(cls, obj: FileObject) -> "File":
        ret = object.__new__(cls)

        ret.is_dir = obj.is_dir
        ret.file_id = obj.file_id
        ret.parent_id = obj.parent_id
        ret.name = obj.name
        ret.size = obj.size
        ret.sha1 = obj.sha1
        ret.pickcode = obj.pickcode
        ret.media_duration = obj.media_duration
        if obj.video_definition is not None:
            ret.video_definition = VideoDefinition(obj.video_definition)
        ret.modified_time = datetime.fromtimestamp(obj.update_time)
        return ret

    def __str__(self) -> str:
        if self.is_dir:
            return f'{self.name}/'
        else:
            return self.name


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


class TaskStatus(IntEnum):

    RUNNING = 1
    """Task is running."""

    COMPLETE = 2
    """Task is completely downloaded."""

    FAILED = -1
    """Task is failed."""


@dataclass(init=False)
class Task:
    """Task represents an offline task."""

    task_id: str
    """Unique ID of the task."""

    name: str
    """Task name."""

    size: int
    """Total size to be downloaded."""

    created_time: datetime
    """Task created time."""

    percent: float
    """Precentage of the download, 0~100."""

    status: TaskStatus
    """Task status."""

    file_id: str
    """Downloaded file ID of the task, may be None if the task does not finish."""

    file_is_dir: bool
    """Is the downloaded file a directory."""

    def __new__(cls, task_obj: TaskObject):
        ret = object.__new__(cls)
        ret.task_id = task_obj.info_hash
        ret.name = task_obj.name
        ret.size = task_obj.size
        ret.created_time = task_obj.created_time
        ret.percent = task_obj.percent
        ret.status = TaskStatus(task_obj.status)
        ret.file_id = task_obj.file_id
        ret.file_is_dir = task_obj.file_id == task_obj.dir_id
        return ret

    def is_complete(self) -> bool:
        """Check is task complete."""
        return self.status == TaskStatus.COMPLETE

    def is_failed(self) -> bool:
        """Check is task failed."""
        return self.status == TaskStatus.FAILED

    def is_running(self) -> bool:
        """Check is task still running."""
        return self.status == TaskStatus.RUNNING
