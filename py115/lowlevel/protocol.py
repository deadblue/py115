__author__ = 'deadblue'

from typing import Dict

import httpx

from ._crypto.ec115 import Cipher
from .types import ApiSpec, R


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

    _hc: httpx.Client
    _ecc: Cipher

    def __init__(self) -> None:
        self._hc = httpx.Client(
            headers={
                'User-Agent': 'Mozilla/5.0'
            },
            timeout=httpx.Timeout(
                timeout=5.0, read=60.0
            )
        )
        self._ecc = Cipher()

    def set_user_agent(self, name: str):
        self._hc.headers['User-Agent'] = name

    def import_cookies(self, cookies: Dict[str, str]):
        for name, value in cookies.items():
            self._hc.cookies.set(name, value, domain='.115.com')

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
        return self._hc.build_request(
            method=method,
            url=spec.url(),
            params=spec.query,
            headers=headers,
            content=payload
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
