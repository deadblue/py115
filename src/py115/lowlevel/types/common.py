__author__ = 'deadblue'

from hashlib import md5


class CommonParams:
    """
    CommonParams contains most-used parameters for low-level APIs.
    """

    _app_ver: str
    _user_id: str
    _user_hash: str
    _user_key: str

    def __init__(self, app_ver: str) -> None:
        self._app_ver = app_ver

    def set_user_info(self, user_id: int, user_key: str):
        self._user_id = str(user_id)
        self._user_key = user_key
        self._user_hash = md5(self._user_id.encode()).hexdigest()

    @property
    def app_ver(self) -> str:
        return self._app_ver
    
    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def user_hash(self) -> str:
        return self._user_hash
    
    @property
    def user_key(self) -> str:
        return self._user_key
    
    def clone(self) -> 'CommonParams':
        ret = CommonParams(self._app_ver)
        ret._user_id = self._user_id
        ret._user_key = self._user_key
        ret._user_hash = self._user_hash
        return ret
