__author__ = 'deadblue'

import json
import logging
import time
import warnings
from urllib3.exceptions import InsecureRequestWarning

import requests

from py115.internal.crypto import ec115
from py115.internal.protocol.api import ApiSpec


_logger = logging.getLogger(__name__)


class Client:

    def __init__(self) -> None:
        self._user_agent = 'Mozilla/5.0'
        self._app_version = None
        session = requests.Session()
        session.headers.update({
            'User-Agent': self._user_agent
        })
        self._session = session
        self._ecc = ec115.Cipher()

    def enable_debug(self):
        # Disable SSL verification for MITM debugging
        self._session.verify = False
        warnings.simplefilter('ignore', category=InsecureRequestWarning)
        self._session.proxies.update({
            'http': '127.0.0.1:9999',
            'https': '127.0.0.1:9999'
        })

    def import_cookie(self, cookies: dict):
        for name, value in cookies.items():
            self._session.cookies.set(
                name, value,
                domain='.115.com'
            )

    def setup_user_agent(self, app_version: str):
        self._app_version = app_version
        self._user_agent = 'Mozilla/5.0 115Desktop/%s' % app_version
        self._session.headers.update({
            'User-Agent': self._user_agent
        })

    @property
    def user_agent(self) -> str:
        return self._user_agent

    @property
    def app_version(self) -> str:
        return self._app_version

    def execute_api(self, spec: ApiSpec):
        if spec.use_ec:
            spec.append_param(
                'k_ec', 
                self._ecc.encode_token(int(time.time()))
            )
        data = spec.payload
        if data is None:
            resp = self._session.get(url=spec.url, params=spec.qs)
        else:
            if spec.use_ec:
                data = self._ecc.encode(data)
            resp = self._session.post(
                url=spec.url, 
                params=spec.qs, 
                data=data,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            )
        if spec.use_ec:
            result = json.loads(self._ecc.decode(resp.content))
        else:
            result = resp.json()
        return spec.parse_result(result)
