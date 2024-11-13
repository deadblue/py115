__author__ = 'deadblue'

import time
from http.cookiejar import Cookie, CookieJar
from typing import Sequence
from urllib.request import Request


class LowlevelCookieJar(CookieJar):
    """LowlevelCookieJar exposes protected CookieJar method to public."""

    def __init__(self) -> None:
        super().__init__(None)

    def set(self, name: str, value: str, domain: str) -> None:
        self.set_cookie(Cookie(
            version=0,
            name=name,
            value=value,
            port=None,
            port_specified=False,
            domain=domain,
            domain_specified=True,
            domain_initial_dot=domain.startswith('.'),
            path='/',
            path_specified=True,
            secure=False,
            expires=None,
            discard=False, 
            comment=None,
            comment_url=None,
            rest={'HttpOnly': None}
        ))

    def get_cookies_for_url(self, url: str) -> Sequence[Cookie]:
        with self._cookies_lock:
            self._policy._now = self._now = int(time.time())
            return self._cookies_for_request(Request(
                url=url, method='GET'
            ))    
