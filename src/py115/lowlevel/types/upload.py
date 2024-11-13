__author__ = 'deadblue'

from dataclasses import dataclass


@dataclass
class UploadInfo:
    user_id: int
    user_key: str

