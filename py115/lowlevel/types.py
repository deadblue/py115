__author__ = 'deadblue'

from hashlib import md5
from abc import ABC, abstractmethod
from typing import Dict, Generic, TypeVar, Union


R = TypeVar('R')


class ApiSpec(Generic[R], ABC):
    """
    ApiSpec is the super class of all 115 APIs.
    """

    _api_url: str
    _use_ec: bool
    query: Dict[str, str]
    form: Dict[str, str]

    def __init__(self, api_url: str, use_ec: bool) -> None:
        self._api_url = api_url
        self._use_ec = use_ec
        self.query = {}
        self.form = {}

    @property
    def use_ec(self) -> bool:
        return self._use_ec

    def url(self) -> str:
        return self._api_url

    @abstractmethod
    def payload(self) -> Union[bytes, None]:
        pass

    @abstractmethod
    def parse_result(self, result: bytes) -> R:
        pass


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
