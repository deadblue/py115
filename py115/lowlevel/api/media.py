__author__ = 'deadblue'

import time
from dataclasses import dataclass
from typing import List

from ..protocol import CommonParams
from ._base import JsonApiSpec, JsonResult, M115ApiSpec
from ._util import to_int, to_https_url


@dataclass
class ImageLinkResult:

    file_name: str
    origin_url: str


class ImageLinkApi(JsonApiSpec[ImageLinkResult]):
    def __init__(self, pickcode: str) -> None:
        super().__init__(
            'https://webapi.115.com/files/image'
        )
        self.query.update({
            'pickcode': pickcode,
            '_': str(int(time.time() * 1000))
        })

    def _parse_json_result(self, json_obj: JsonResult) -> ImageLinkResult:
        data_obj = json_obj['data']
        return ImageLinkResult(
            file_name=data_obj['file_name'],
            origin_url=data_obj['origin_url']
        )


@dataclass
class VideoObject:

    width: int
    height: int
    play_url: str


@dataclass
class VideoPlayResult:

    file_name: str
    duration: int
    items: List[VideoObject]


class VideoPlayWebApi(JsonApiSpec[VideoPlayResult]):

    def __init__(self, pickcode: str) -> None:
        super().__init__('https://webapi.115.com/files/video')
        self.query['pickcode'] = pickcode

    def _parse_json_result(self, json_obj: JsonResult) -> VideoPlayResult:
        return VideoPlayResult(
            file_name=json_obj['file_name'],
            duration=to_int(json_obj['play_long']),
            items=[VideoObject(
                width=to_int(json_obj['width']),
                height=to_int(json_obj['height']),
                play_url=to_https_url(json_obj['video_url'])
            )]
        )


class VideoPlayDesktopApi(M115ApiSpec[VideoPlayResult]):
    
    def __init__(self, pickcode: str, common_params: CommonParams) -> None:
        super().__init__('https://proapi.115.com/pc/video/play')
        self.form.update({
            'format': 'app',
            'definition_filter': '1',
            'pickcode': pickcode,
            'user_id': common_params.user_id,
            'appversion': common_params.app_ver
        })

    def _parse_m115_result(self, m115_obj: JsonResult) -> VideoPlayResult:
        result = VideoPlayResult(
            file_name=m115_obj['file_name'],
            duration=to_int(m115_obj['play_long']),
            items=[]
        )
        for video_obj in m115_obj['video_url']:
            result.items.append(VideoObject(
                width=to_int(video_obj['width']),
                height=to_int(video_obj['height']),
                play_url=to_https_url(video_obj['url'])
            ))
        return result
