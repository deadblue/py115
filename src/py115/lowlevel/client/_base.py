__author__ = 'deadblue'

from abc import ABC
from typing import Dict, Generic, TypeVar

import httpx

from py115._internal.crypto.ec115 import Cipher
from py115.lowlevel.spec import ApiSpec
from ._cookie import LowlevelCookieJar


COOKIE_DOMAINS = ('.115.com', '.anxia.com')
COOKIE_URL = 'https://115.com/'


C = TypeVar('C', httpx.Client, httpx.AsyncClient)


class BaseClient(Generic[C], ABC):

    _ecc: Cipher
    _jar: LowlevelCookieJar
    _hc: C

    def __init__(self) -> None:
        self._ecc = Cipher()
        self._jar = LowlevelCookieJar()

    def import_cookies(self, cookies: Dict[str, str]):
        """
        Import cookies to client.

        Args:
            cookies (Dict[str, str]): Cookies that will be sent for HTTP API.
        """
        for domain in COOKIE_DOMAINS:
            for name, value in cookies.items():
                self._jar.set(name, value, domain=domain)

    def export_cookies(self, target_url=COOKIE_URL) -> Dict[str, str]:
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

    def set_user_agent(self, user_agent: str):
        self._hc.headers['User-Agent'] = user_agent

    def _prepare_request(self, spec: ApiSpec) -> httpx.Request:
        method, headers, content = 'GET', {}, None
        payload = spec.payload()
        if payload is not None:
            method = 'POST'
            headers.update({
                'Content-Type': payload.mime_type
            })
            content = payload.content
        if spec.use_ec:
            spec.query['k_ec'] = self._ecc.encode_token()
            if content is not None: 
                content = self._ecc.encode(content)
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
            content=content,
            timeout=timeout
        )
