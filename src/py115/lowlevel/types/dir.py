__author__ = 'deadblue'

from typing import Literal


DirOrder = Literal[
    'file_name',
    'file_size',
    'file_type',
    'user_ptime',
    'user_utime',
    'user_otime'
]
