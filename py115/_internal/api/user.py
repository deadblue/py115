__author__ = 'deadblue'

from py115._internal.protocol.api import ApiSpec

class GetApi(ApiSpec):

    def __init__(self) -> None:
        super().__init__('https://my.115.com/?ct=ajax&ac=nav')
