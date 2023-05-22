__author__ = 'deadblue'

import json
import logging
import time
import warnings
from urllib3.exceptions import InsecureRequestWarning

import requests

from py115._internal.crypto import ec115
from py115._internal.protocol.api import ApiSpec, RetryException


_logger = logging.getLogger(__name__)


class Client:

    def __init__(self, **kwargs) -> None:
        self._ecc = ec115.Cipher()
        self._session = requests.Session()
        # Configure session
        self._user_agent = 'Mozilla/5.0'
        self._session.headers.update({
            'User-Agent': self._user_agent
        })
        # Flow control
        self._next_request_time = 0.0
        # Protocol client settings
        verify = kwargs.pop('verify', None)
        if verify is not None and isinstance(verify, bool):
            self._session.verify = verify
            if not verify:
                warnings.simplefilter('ignore', category=InsecureRequestWarning)
        proxies = kwargs.pop('proxies', None)
        if proxies is not None and isinstance(proxies, dict):
            self._session.proxies = proxies

    def import_cookies(self, cookies: dict):
        for name, value in cookies.items():
            self._session.cookies.set(
                name, value,
                domain='.115.com',
                path='/'
            )

    def export_cookies(self) -> dict:
        return self._session.cookies.get_dict(
            domain='.115.com', path='/'
        )

    def setup_user_agent(self, app_version: str):
        self._user_agent = 'Mozilla/5.0 115Desktop/%s' % app_version
        self._session.headers.update({
            'User-Agent': self._user_agent
        })

    @property
    def user_agent(self) -> str:
        return self._user_agent

    def execute_api(self, spec: ApiSpec):
        while True:
            try:
                return self._execute_api_internal(spec)
            except RetryException:
                pass

    def _execute_api_internal(self, spec: ApiSpec):
        if spec.use_ec:
            spec.update_qs({
                'k_ec': self._ecc.encode_token(int(time.time()))
            })
        data = spec.payload
        # Flow control
        wait_time = self._next_request_time - time.time()
        if wait_time > 0:
            time.sleep(wait_time)
        try:
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
        finally:
            self._next_request_time = time.time() + spec.get_delay()
        if spec.use_ec:
            result = json.loads(self._ecc.decode(resp.content))
        else:
            result = resp.json()
        _logger.debug('API result: %r', result)
        return spec.parse_result(result)
