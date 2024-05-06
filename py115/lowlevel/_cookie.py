__author__ = 'deadblue'

import time
from http.cookiejar import Cookie, CookieJar
from typing import Sequence
from urllib.request import Request


class LowlevelCookieJar(CookieJar):
    """LowlevelCookieJar exposes protected CookieJar method to public."""

    def __init__(self) -> None:
        super().__init__(None)
    
    def get_cookies_for_url(self, url: str) -> Sequence[Cookie]:
        with self._cookies_lock:
            self._policy._now = self._now = int(time.time())
            return self._cookies_for_request(Request(
                url=url, method='GET'
            ))    
