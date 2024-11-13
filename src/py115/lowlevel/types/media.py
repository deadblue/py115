__author__ = 'deadblue'

from dataclasses import dataclass


@dataclass
class ImageInfo:
    file_name: str
    origin_url: str


@dataclass
class VideoInfo:
    file_name: str
    duration: int
    width: int
    height: int
    play_url: str
