__author__ = 'deadblue'

from dataclasses import dataclass

@dataclass
class DownloadResult:
    file_id: str
    file_name: str
    file_size: int
    url: str
