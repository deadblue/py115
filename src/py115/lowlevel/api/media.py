__author__ = 'deadblue'

from py115.lowlevel.types.media import (
    ImageInfo, VideoInfo
)
from py115.lowlevel._utils import (
    now_str, must_int
)
from ._base import JsonApiSpec, JsonResult


class ImageLinkApi(JsonApiSpec[ImageInfo]):
    def __init__(self, pickcode: str) -> None:
        super().__init__('https://webapi.115.com/files/image')
        self.query.update({
            'pickcode': pickcode,
            '_': now_str()
        })

    def _parse_json_result(self, json_obj: JsonResult) -> ImageInfo:
        data_obj = json_obj['data']
        return ImageInfo(
            file_name=data_obj['file_name'],
            origin_url=data_obj['origin_url']
        )


class VideoPlayWebApi(JsonApiSpec[VideoInfo]):

    def __init__(self, pickcode: str) -> None:
        super().__init__('https://webapi.115.com/files/video')
        self.query['pickcode'] = pickcode

    def _parse_json_result(self, json_obj: JsonResult) -> VideoInfo:
        return VideoInfo(
            file_name=json_obj['file_name'],
            duration=must_int(json_obj['play_long']),
            width=must_int(json_obj['width']),
            height=must_int(json_obj['height']),
            play_url=json_obj['video_url']
        )
