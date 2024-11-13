__author__ = 'deadblue'

from typing import Awaitable
from types import TracebackType

import httpx

from py115.lowlevel.exceptions import RetryException
from py115.lowlevel.spec import ApiSpec, R
from ._base import BaseClient


DEFAULT_USER_AGNET = 'Mozilla/5.0'


class Client(BaseClient[httpx.Client]):
    """
    Low-level API client
    """

    def __init__(self) -> None:
        super().__init__()
        self._hc = httpx.Client(
            headers={
                'User-Agent': DEFAULT_USER_AGNET
            },
            cookies=self._jar,
            limits=httpx.Limits(
                max_connections=None,
                max_keepalive_connections=20,
                keepalive_expiry=10.0
            ),
            verify=False,
            proxy='http://127.0.0.1:9999'
        )

    def call_api(self, spec: ApiSpec[R]) -> R:
        while True:
            try:
                req = self._prepare_request(spec)
                resp = self._hc.send(req)
                body = resp.content
                if spec.use_ec:
                    body = self._ecc.decode(body)
                return spec.parse_result(body)
            except (httpx.TimeoutException, RetryException):
                pass
    
    def fetch(self, url: str) -> bytes:
        resp = self._hc.get(url)
        return resp.content
    
    def __enter__(self):
        self._hc.__enter__()
    
    def __exit__(
            self, 
            exc_type: type[BaseException] | None,
            exc_value: BaseException | None,
            traceback: TracebackType | None
        ):
        self._hc.__exit__(exc_type, exc_value, traceback)


class AsyncClient(BaseClient[httpx.AsyncClient]):
    """
    Low-level async API client
    """

    def __init__(self) -> None:
        super().__init__()
        self._hc = httpx.AsyncClient(
            headers={
                'User-Agent': DEFAULT_USER_AGNET
            },
            cookies=self._jar
        )

    async def call_api(self, spec: ApiSpec[R]) -> Awaitable[R]:
        req = self._prepare_request(spec)
        resp = await self._hc.send(req)
        # TODO
        pass
