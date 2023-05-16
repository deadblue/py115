__author__ = 'deadblue'

from datetime import datetime
from enum import IntEnum

from py115.types import _utils as utils


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
