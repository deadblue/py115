__author__ = 'deadblue'

from py115._internal.protocol.api import ApiSpec

class GetVersionApi(ApiSpec):
    
    def __init__(self) -> None:
        super().__init__('https://appversion.115.com/1/web/1.0/api/chrome')

    def parse_result(self, result: dict) -> str:
        return result['data']['linux_115']['version_code']


class GetTypeApi(ApiSpec):

    def __init__(self) -> None:
        super().__init__('https://webapi.115.com/files/index_info')
    
    def parse_result(self, result: dict):
        result = super().parse_result(result)
        login_devices = result['login_devices_info']['list']
        for device in login_devices:
            if device['is_current'] == 1:
                device_flag = device['ssoent']
                if device_flag.startswith('A'):
                    return 'web'
                elif device_flag.startswith('P'):
                    return 'pc'
                else:
                    break
        return 'unknown'
