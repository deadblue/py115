__author__ = 'deadblue'

from py115._internal.api import m115
from py115._internal.protocol import api


class WebPlayApi(api.ApiSpec):

    def __init__(self, pickcode: str) -> None:
        super().__init__('https://webapi.115.com/files/video', False)
        self.update_qs({'pickcode': pickcode})
    
    def parse_result(self, result: dict) -> str:
        err_code = api.find_error_code(result)
        if err_code != 0:
            raise api.ApiException(code=err_code)
        return result.get('video_url')


class PcPlayApi(m115.M115ApiSpec):

    def __init__(self, pickcode: str, user_id: str, app_ver: str) -> None:
        super().__init__('https://proapi.115.com/pc/video/play')
        self.update_from({
            'format': 'app',
            'definition_filter': '1',
            'pickcode': pickcode,
            'user_id': user_id,
            'appversion': app_ver
        })
    
    def parse_result(self, result: dict):
        result = super().parse_result(result)
        video_urls = sorted(
            result['video_url'], 
            key=lambda u: u['definition'],
            reverse=True
        )
        return video_urls[0]['url']
