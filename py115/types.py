__author__ = 'deadblue'

from enum import IntEnum

class TaskClearFlag(IntEnum):
    Done = 0
    All = 1
    Failed = 2
    Running = 3
