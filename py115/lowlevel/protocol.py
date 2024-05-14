__author__ = 'deadblue'

from abc import ABC, abstractmethod
from dataclasses import dataclass
from hashlib import md5
from typing import Dict, Generic, TypeVar, Union

import httpx

from ._cookie import LowlevelCookieJar
from ._crypto.ec115 import Cipher


_DEFAULT_USER_AGNET = 'Mozilla/5.0'
_COOKIE_DOMAIN = '.115.com'
_COOKIE_URL = 'https://115.com/'

R = TypeVar('R')

@dataclass
class ApiTimeout:
    """
    Timeout config for API.
    """

    connect: float
    """Connect timeout in seconds."""
    read: float
    """Read timeout in seconds."""


class ApiSpec(Generic[R], ABC):
    """
    ApiSpec is the super class of all 115 APIs.
    """

    _api_url: str
    _use_ec: bool
    _timeout: ApiTimeout
    query: Dict[str, str]
    form: Dict[str, str]

    def __init__(self, api_url: str, use_ec: bool) -> None:
        self._api_url = api_url
        self._use_ec = use_ec
        self._timeout = ApiTimeout(
            connect=5.0, read=5.0
        )
        self.query = {}
        self.form = {}

    @property
    def use_ec(self) -> bool:
        return self._use_ec

    @property
    def timeout(self) -> ApiTimeout:
        return self._timeout

    def url(self) -> str:
        return self._api_url

    def payload(self) -> Union[bytes, None]:
        return None

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


class RetryException(Exception):
    """
    Client will retry when catch this exception.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Client:
    """
    Client is low-level API client which works with low-level ApiSpecs.
    """

    _ecc: Cipher
    _jar: LowlevelCookieJar
    _hc: httpx.Client

    def __init__(self) -> None:
        self._ecc = Cipher()
        self._jar = LowlevelCookieJar()
        self._hc = httpx.Client(
            headers={
                'User-Agent': _DEFAULT_USER_AGNET
            },
            cookies=self._jar
        )

    def get_user_agent(self) -> str:
        return self._hc.headers.get('User-Agent', _DEFAULT_USER_AGNET)

    def set_user_agent(self, name: str):
        self._hc.headers['User-Agent'] = name

    user_agent = property(get_user_agent, set_user_agent)

    def import_cookies(self, cookies: Dict[str, str]):
        """
        Import cookies to client.

        Args:
            cookies (Dict[str, str]): Cookies that will be sent for HTTP API.
        """
        for name, value in cookies.items():
            self._hc.cookies.set(name, value, domain=_COOKIE_DOMAIN)

    def export_cookies(self, target_url=_COOKIE_URL) -> Dict[str, str]:
        """
        Export cookies from client.

        Args:
            target_url (str): The URL that export cookies for.
        
        Returns:
            Dict[str, str]: Cookies for `target_url`.
        """
        result = {}
        for cookie in self._jar.get_cookies_for_url(target_url):
            result[cookie.name] = cookie.value
        return result

    def _build_request(self, spec: ApiSpec[R]) -> httpx.Request:
        payload = spec.payload()
        method, headers = 'GET', {}
        if payload is not None:
            method = 'POST'
            headers.update({
                'Content-Type': 'application/x-www-form-urlencoded'
            })
        if spec.use_ec:
            spec.query['k_ec'] = self._ecc.encode_token()
            if payload is not None: 
                payload = self._ecc.encode(payload)
        timeout = httpx.Timeout(
            timeout=None,
            connect=spec.timeout.connect,
            read=spec.timeout.read
        )
        return self._hc.build_request(
            method=method,
            url=spec.url(),
            params=spec.query,
            headers=headers,
            content=payload,
            timeout=timeout
        )

    def call_api(self, spec: ApiSpec[R]) -> R:
        """
        Call a 115 API.

        Args:
            spec (ApiSpec[R]): An API spec.
        """
        while True:
            request = self._build_request(spec)
            try:
                resp = self._hc.send(request)
                body = resp.content
                if spec.use_ec and body is not None:
                    body = self._ecc.decode(body)
                return spec.parse_result(body)
            except (httpx.TimeoutException, RetryException):
                pass

    def fetch(self, url: str) -> bytes:
        resp = self._hc.get(url)
        return resp.content
