__author__ = 'deadblue'

from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Dict, List

from py115.lowlevel._utils import to_timestamp


class VideoDefinition(IntEnum):
    SD        = 1
    HD        = 2
    FHD       = 3
    FHD_1080P = 4
    UHD_4K    = 5
    ORIGINAL  = 100


@dataclass(init=False)
class FileInfo:
    """
    FileObject represents a file/directory item in cloud storage.
    """

    file_id: str
    """Unique ID of the file/directory."""

    parent_id: str
    """File ID of parent directory."""

    name: str
    """Base name."""

    pickcode: str
    """Pick code for download/play."""

    is_dir: bool
    """Indicate whether file is a directory."""

    is_stared: bool
    """Indicate whether file is stared."""

    is_hidden: bool
    """Indicate whether file is hidden."""

    is_top: bool
    """Indicate whether file is on top."""

    size: int | None = None
    """File size in bytes."""

    sha1: str | None = None
    """File SHA-1 hash in HEX-format."""

    modified_time: int
    """Timestamp when file is modified."""

    created_time: int | None = None
    """Timestamp when file is created."""

    opened_time: int | None = None
    """Timestamp when file is opened."""

    is_video: bool = False
    """Indicate whether file is video."""

    media_duration: int | None = None
    """Media duration in seconds for audio/video file."""

    video_definition: VideoDefinition | None = None
    """Video definition for video file."""

    def __init__(self, file_obj: Dict[str, Any]) -> None:
        self.is_dir = 'fid' not in file_obj
        self.is_stared = file_obj.get('m', 0) == 1
        self.is_hidden = file_obj.get('hdf', 0) != 0
        self.is_top = file_obj.get('is_top', 0) == 1
        self.name = file_obj['n']
        self.pickcode = file_obj['pc']
        if self.is_dir:
            self.file_id = file_obj['cid']
            self.parent_id = file_obj['pid']
        else:
            self.file_id = file_obj['fid']
            self.parent_id = file_obj['cid']
            self.size = file_obj['s']
            self.sha1 = file_obj['sha']
            self.is_video = file_obj.get('iv', 0) == 1
            self.media_duration = file_obj.get('play_long', None)
            if 'vdi' in file_obj:
                self.video_definition = VideoDefinition(file_obj['vdi'])
        for key in ('tu', 'te', 't'):
            if key in file_obj:
                self.modified_time = to_timestamp(file_obj[key])
                break
        if 'tp' in file_obj:
            self.created_time = to_timestamp(file_obj['tp'])
        if 'to' in file_obj:
            self.opened_time = to_timestamp(file_obj['to'])

@dataclass
class FileListResult:

    offset: int
    limit: int
    order: str
    asc: int
    count: int
    files: List[FileInfo]


class FileType(IntEnum):

    ALL      = 0
    DOCUMENT = 1
    IMAGE    = 2
    AUDIO    = 3
    VIDEO    = 4
    ARCHIVE  = 5
    SOFTWARE = 6
