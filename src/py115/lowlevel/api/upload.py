__author__ = 'deadblue'

from py115.lowlevel.types.upload import UploadInfo
from ._base import JsonApiSpec, JsonResult


class UploadInfoApi(JsonApiSpec[UploadInfo]):

    def __init__(self) -> None:
        super().__init__('https://proapi.115.com/app/uploadinfo')
    
    def _parse_json_result(self, json_obj: JsonResult) -> UploadInfo:
        return UploadInfo(
            user_id=json_obj.get('user_id'),
            user_key=json_obj.get('userkey')
        )


# @dataclass
# class UploadInitOssResult:
#     bucket: str
#     object: str
#     callback: str
#     callback_var: str
#     endpoint: str = 'https://oss-cn-shenzhen.aliyuncs.com'

# @dataclass
# class UploadInitDoneResult:
#     pickcode: str

# @dataclass
# class UploadInitSignResult:
#     sign_key: str
#     sign_range: str

# UploadInitResult = Union[
#     UploadInitOssResult, UploadInitDoneResult, UploadInitSignResult
# ]


# def _to_target_id(dir_id: str) -> str:
#     return f'U_1_{dir_id}'

# _token_salt = 'Qclm8MGWUv59TnrR0XPg'

# class UploadInitApi(JsonApiSpec[UploadInitResult]):

#     _cp: CommonParams

#     def __init__(
#             self, cp: CommonParams,
#             dir_id: str, file_name: str, file_size: int, file_sha1: str, 
#             sign_key: str = '', sign_value: str = '',
#         ) -> None:
#         super().__init__('https://uplb.115.com/4.0/initupload.php', True)
#         self._cp = cp
#         target_id = _to_target_id(dir_id)
#         now = int(time.time())
#         self.form.update({
#             'appid': '0',
#             'appversion': cp.app_ver,
#             'userid': cp.user_id,
#             'target': target_id,
#             'fileid': file_sha1,
#             'filename': file_name,
#             'filesize': str(file_size),
#             't': str(now)
#         })
#         # Calculate signature
#         h1 = hashlib.sha1(
#             f'{cp.user_id}{file_sha1}{target_id}0'.encode()
#         ).hexdigest().lower()
#         self.form['sig'] = hashlib.sha1(
#             f'{cp.user_key}{h1}000000'.encode()
#         ).hexdigest().upper()
#         # Calculate token
#         if sign_key != '' and sign_value != '':
#             self.form.update({
#                 'sign_key': sign_key,
#                 'sign_val': sign_value
#             })
#         self._set_token()

#     def _set_token(self):
#         file_sha1 = self.form.get('fileid')
#         file_size = self.form.get('filesize')
#         timestamp = self.form.get('t')
#         sign_key = self.form.get('sign_key', '')
#         sign_value = self.form.get('sign_val', '')
#         token_data = ''.join([
#             _token_salt, file_sha1, file_size, sign_key, sign_value, 
#             self._cp.user_id, timestamp, self._cp.user_hash, self._cp.app_ver
#         ]).encode()
#         self.form['token'] = hashlib.md5(token_data).hexdigest().lower()

#     def update_token(self, sign_key: str, sign_value: str):
#         now = int(time.time())
#         self.form.update({
#             'sign_key': sign_key,
#             'sign_val': sign_value,
#             't': str(now),
#         })
#         self._set_token()

#     def _parse_json_result(self, json_obj: JsonResult) -> UploadInitResult:
#         status = json_obj.get('status')
#         status_code = json_obj.get('statuscode')
#         if status == 1:
#             return UploadInitOssResult(
#                 bucket=json_obj['bucket'],
#                 object=json_obj['object'],
#                 callback=json_obj['callback']['callback'],
#                 callback_var=json_obj['callback']['callback_var']
#             )
#         elif status == 2:
#             return UploadInitDoneResult(
#                 pickcode=json_obj['pickcode']
#             )
#         elif status == 7 and status_code == 701:
#             return UploadInitSignResult(
#                 sign_key=json_obj['sign_key'],
#                 sign_range=json_obj['sign_check']
#             )
#         return None


# @dataclass
# class UploadTokenResult:
#     access_key_id: str
#     access_key_secret: str
#     security_token: str
#     expiration: datetime


# _tz_utc = timezone(offset=timedelta(0), name='UTC')

# class UploadTokenApi(JsonApiSpec[UploadTokenResult]):

#     def __init__(self) -> None:
#         super().__init__('https://uplb.115.com/3.0/gettoken.php')
    
#     def _parse_json_result(self, json_obj: JsonResult) -> UploadTokenResult:
#         expiration = datetime.strptime(
#             '%Y-%m-%dT%H:%M:%SZ', json_obj['Expiration']
#         ).replace(tzinfo=_tz_utc)
#         return UploadTokenResult(
#             access_key_id=json_obj['AccessKeyId'],
#             access_key_secret=json_obj['AccessKeySecret'],
#             security_token=json_obj['SecurityToken'],
#             expiration=expiration
#         )
