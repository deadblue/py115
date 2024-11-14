__author__ = 'deadblue'

from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Dict, List


class TaskStatus(IntEnum):
    FAILED  = -1
    STOPPED = 0
    RUNNING = 1
    DONE    = 2


@dataclass(init=False)
class TaskInfo:

    info_hash: str
    """Unique ID of the task."""

    url: str
    """Download URL."""

    name: str
    """Task name."""

    size: int
    """Total size to download."""

    created_time: int
    """Task created time."""

    status: TaskStatus
    """Task status."""

    percent: float
    """Download progress in percentage."""

    file_id: str
    """File ID of the downloaded file."""

    parent_id: str
    """Parent directory ID to save downloaded file."""

    is_dir: bool
    """Indeicate whether downloaded file is a directory."""

    def __init__(self, task_obj: Dict[str, Any]) -> None:
        self.info_hash = task_obj['info_hash']
        self.url = task_obj['url']
        self.name = task_obj['name']
        self.size = task_obj['size']
        self.created_time = task_obj['add_time']
        self.status = TaskStatus(task_obj['status'])
        self.percent = float(task_obj.get('percentDone', 0))
        self.file_id = task_obj['delete_file_id']
        self.parent_id = task_obj['wp_path_id']
        self.is_dir = task_obj['delete_file_id'] == task_obj['file_id']


@dataclass
class OfflineListResult:
    page_num: int
    page_count: int
    page_size: int
    quota_total: int
    quota_remain: int
    task_count: int
    tasks: List[TaskInfo]


class OfflineClearFlag(IntEnum):
    DONE = 0
    ALL = 1
    FAILED = 2
    RUNNING = 3
    DONE_AND_DELETE = 4
    ALL_AND_DELETE = 5


class OfflineErrorReason(IntEnum):
    UNKNOWN      = -1
    TASK_EXISTED = 1
    LINK_INVALID = 2


@dataclass
class OfflineAddResult:
    info_hash: str | None = None
    reason: OfflineErrorReason | None = None
    url: str | None = None
