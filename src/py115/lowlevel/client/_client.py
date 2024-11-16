__author__ = 'deadblue'

from typing import Awaitable
from types import TracebackType

import httpx

from py115.lowlevel.exceptions import RetryException
from py115.lowlevel.spec import ApiSpec, R
from ._base import BaseClient


class Client(BaseClient[httpx.Client]):
    """
    Low-level API client.
    """

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
        return self
    
    def __exit__(
            self, 
            exc_type: type[BaseException] | None,
            exc_value: BaseException | None,
            traceback: TracebackType | None
        ):
        self._hc.__exit__(exc_type, exc_value, traceback)



class AsyncClient(BaseClient[httpx.AsyncClient]):
    """
    Low-level asynchronous API client.
    """

    async def call_api(self, spec: ApiSpec[R]) -> Awaitable[R]:
        while True:
            try:
                req = self._prepare_request(spec)
                resp = await self._hc.send(req)
                body = resp.content
                if spec.use_ec:
                    body = self._ecc.decode(body)
                return spec.parse_result(body)
            except (httpx.TimeoutException, RetryException):
                pass

    async def __aenter__(self):
        await self._hc.__aenter__()
        return self
    
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: TracebackType | None = None,
    ):
        await self._hc.__aexit__(exc_type, exc_value, traceback)
