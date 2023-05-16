__author__ = 'deadblue'

from py115._internal.protocol import api

class GetApi(api.ApiSpec):

    def __init__(self) -> None:
        super().__init__('https://webapi.115.com/files/index_info')
    
    def parse_result(self, result: dict):
        data = super().parse_result(result)
        return data.get('space_info', None)
