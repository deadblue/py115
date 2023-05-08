__author__ = 'deadblue'

import typing
from py115.internal.protocol import api


class InfoApi(api.ApiSpec):

    def __init__(self) -> None:
        super().__init__('https://proapi.115.com/app/uploadinfo')
    

    def parse_result(self, result: dict) -> typing.Tuple[int, str]:
        err_code = api.find_error_code(result)
        if err_code != 0:
            raise api.ApiException(err_code)
        user_id = result.get('user_id')
        user_key = result.get('userkey')
        return (user_id, user_key)


class InitApi(api.ApiSpec):

    def __init__(self, url: str, use_ec: bool = False) -> None:
        super().__init__(url, use_ec)
