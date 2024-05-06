__author__ = 'deadblue'

from typing import Awaitable, Dict

import httpx

from ._cookie import LowlevelCookieJar
from ._crypto.ec115 import Cipher
from .types import ApiSpec, R


_COOKIE_DOMAIN = '.115.com'


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
                'User-Agent': 'Mozilla/5.0'
            },
            cookies=self._jar
        )

    def set_user_agent(self, name: str):
        self._hc.headers['User-Agent'] = name

    def import_cookies(self, cookies: Dict[str, str]):
        for name, value in cookies.items():
            self._hc.cookies.set(name, value, domain=_COOKIE_DOMAIN)

    def export_cookies(self, target_url='https://115.com/') -> Dict[str, str]:
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
