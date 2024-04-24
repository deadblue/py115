__author__ = 'deadblue'

from dataclasses import dataclass
from typing import Any, Dict

from ._json import JsonApiSpec, JsonResult
from ._m115 import M115ApiSpec, M115Result


@dataclass
class VideoResult:
    play_url: str


class VideoWebApi(JsonApiSpec[VideoResult]):

    def __init__(self, pickcode: str) -> None:
        super().__init__('https://webapi.115.com/files/video')
        self.query['pickcode'] = pickcode

    def _parse_json_result(self, json_obj: JsonResult) -> VideoResult:
        return VideoResult(
            play_url=json_obj.get('video_url')
        )


class VideoDesktopApi(M115ApiSpec[VideoResult]):
    
    def __init__(self, pickcode: str) -> None:
        super().__init__('https://proapi.115.com/pc/video/play')
        self.form.update({
            'pickcode': pickcode
        })

    def _parse_m115_result(self, m115_obj: M115Result) -> VideoResult:
        return super()._parse_m115_result(m115_obj)