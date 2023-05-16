__author__ = 'deadblue'

import datetime
import hashlib
import io
import logging
import time
import typing

from py115._internal.protocol import api


_logger = logging.getLogger(__name__)

_token_salt = 'Qclm8MGWUv59TnrR0XPg'


class Helper:

    _app_ver: str = None
    _user_id: str = None
    _user_key: str = None
    _user_hash: str = None

    def __init__(self, app_ver: str, user_id: int, user_key: str) -> None:
        self._app_ver = app_ver
        self._user_id = str(user_id)
        self._user_key = user_key
        self._user_hash = hashlib.md5(
            self._user_id.encode()
        ).hexdigest()
    
    @property
    def app_version(self) -> str:
        return self._app_ver
    
    @property
    def user_id(self) -> str:
        return self._user_id

    def calc_sig(self, file_id: str, target_id: str) -> str:
        h1 = hashlib.sha1(
            f'{self._user_id}{file_id}{target_id}0'.encode()
        ).hexdigest().lower()
        return hashlib.sha1(
            f'{self._user_key}{h1}000000'.encode()
        ).hexdigest().upper()

    def calc_token(
            self, 
            file_id: str,
            file_size: int,
            timestamp: int,
            sign_key: str = '',
            sign_val: str = ''
        ) -> str:
        token_data = ''.join([
            _token_salt, file_id, str(file_size), sign_key, sign_val, 
            self._user_id, str(timestamp), self._user_hash, self._app_ver
        ]).encode()
        return hashlib.md5(token_data).hexdigest().lower()


class InfoApi(api.ApiSpec):

    def __init__(self) -> None:
        super().__init__('https://proapi.115.com/app/uploadinfo')

    def parse_result(self, result: dict) -> typing.Tuple[int, str]:
        err_code = api.find_error_code(result)
        if err_code != 0:
            raise api.ApiException(err_code)
        return result.get('user_id'), result.get('userkey')


class InitApi(api.ApiSpec):

    _helper: Helper = None
    _file_io: typing.BinaryIO = None

    def __init__(
            self, 
            target_id: str, 
            file_name: str, 
            file_io: typing.BinaryIO,
            helper: Helper
        ) -> None:
        super().__init__('https://uplb.115.com/4.0/initupload.php', True)
        self._file_io = file_io
        self._helper = helper
        now = int(time.time())
        file_size, file_hash = _digest_file(file_io)
        self.update_from({
            'appid': '0',
            'appversion': helper.app_version,
            'userid': helper.user_id,
            'filename': file_name,
            'filesize': file_size,
            'fileid': file_hash,
            'target': target_id,
            'sig': helper.calc_sig(file_hash, target_id),
            't': now,
            'token': helper.calc_token(file_hash, file_size, now)
        })

    def parse_result(self, result: dict):
        status = result['status']
        if status == 7:
            sign_key = result['sign_key']
            sign_val = _digest_file_range(self._file_io, result['sign_check'])
            now = int(time.time())
            self.update_from({
                'sign_key': sign_key,
                'sign_val': sign_val,
                't': now,
                'token': self._helper.calc_token(
                    self._form['fileid'], 
                    self._form['filesize'],
                    now, sign_key, sign_val
                )
            })
            raise api.RetryException()
        elif status == 2:
            return  {
                'done': True
            }
        elif status == 1:
            return {
                'done': False,
                'bucket': result['bucket'],
                'object': result['object'],
                'callback': result['callback']['callback'],
                'callback_var': result['callback']['callback_var']
            }
        else:
            _logger.warning('Unexpected upload init status: %d', status)
            return None


def _digest_file(r: typing.BinaryIO) -> typing.Tuple[int, str]:
    h = hashlib.sha1()
    while True:
        chunk = r.read(4096)
        if len(chunk) == 0: break
        h.update(chunk)
    file_size = r.tell()
    file_hash = h.hexdigest().upper()
    return file_size, file_hash


def _digest_file_range(r: typing.BinaryIO, check_range: str) :
    tmp = [int(x) for x in check_range.split('-')]
    start, length = tmp[0], tmp[1] - tmp[0] + 1
    r.seek(start, io.SEEK_SET)
    return hashlib.sha1(
        r.read(length)
    ).hexdigest().upper()


class TokenApi(api.ApiSpec):

    def __init__(self) -> None:
        super().__init__('https://uplb.115.com/3.0/gettoken.php')
    
    def parse_result(self, result: dict):
        if result.get('StatusCode' '') == '200':
            return {
                'access_key_id': result['AccessKeyId'],
                'access_key_secret': result['AccessKeySecret'],
                'security_token': result['SecurityToken'],
                'expiration': datetime.datetime.strptime(
                    result['Expiration'], '%Y-%m-%dT%H:%M:%SZ'
                )
            }
        return None
