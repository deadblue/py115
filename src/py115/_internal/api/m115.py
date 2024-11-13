__author__ = 'deadblue'

import json
import urllib

from py115._internal.crypto import m115
from py115._internal.protocol import api


class M115ApiSpec(api.ApiSpec):

    def __init__(self, url: str, use_ec: bool = False) -> None:
        super().__init__(url, use_ec)
        self._m_key = m115.generate_key()

    @property
    def payload(self) -> bytes:
        data = m115.encode(self._m_key, json.dumps(self._form))
        return urllib.parse.urlencode({
            'data': data
        }).encode()

    def parse_result(self, result: dict):
        # M115 decode
        data = m115.decode(
            self._m_key,  super().parse_result(result)
        )
        return json.loads(data)
