__author__ = 'deadblue'

import json
import logging
import time
import warnings
from urllib.parse import urlparse
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
        proxy_addr = kwargs.pop('proxy', None)
        if proxy_addr is not None and isinstance(proxy_addr, str):
            self._session.proxies = {
                'http': proxy_addr,
                'https': proxy_addr
            }
        verify = kwargs.pop('verify', None)
        if verify is not None and isinstance(verify, bool):
            self._session.verify = verify
            if not verify:
                warnings.simplefilter('ignore', category=InsecureRequestWarning)

    def import_cookies(self, cookies: dict):
        for name, value in cookies.items():
            self._session.cookies.set(
                name, value,
                domain='.115.com',
                path='/'
            )

    def export_cookies(self, url: str = None) -> dict:
        req_domain, req_path = '.115.com', '/'
        if url is not None:
            result = urlparse(url)
            req_domain = f'.{result.hostname}'
            req_path = f'{result.path}/'

        cookie_dict = {}
        for cookie in self._session.cookies:
            # Check domain
            cookie_domain = cookie.domain
            if not cookie_domain.startswith('.'):
                cookie_domain = f'.{cookie_domain}'
            if not req_domain.endswith(cookie_domain): continue
            # Check path
            cookie_path = cookie.path
            if not cookie_path.endswith('/'):
                cookie_path = f'{cookie_path}/'
            if not req_path.startswith(cookie_path): continue
            # Add cookie to dict
            cookie_dict[cookie.name] = cookie.value
        return cookie_dict

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
        # Prepare request
        req = requests.Request(
            method='GET',
            url=spec.url,
            params=spec.qs
        )
        if data is not None:
            if spec.use_ec:
                data = self._ecc.encode(data)
            req.method = 'POST'
            req.data = data
            req.headers.update({
                'Content-Type': 'application/x-www-form-urlencoded'
            })
        # Send request with retrying
        while True:
            # Flow control
            wait_time = self._next_request_time - time.time()
            if wait_time > 0:
                time.sleep(wait_time)
            try:
                resp = self._session.send(
                    request=self._session.prepare_request(req),
                    timeout=(10.0, 30.0)
                )
                break
            except requests.Timeout:
                _logger.warning('Request timeout, retry ...')
            finally:
                self._next_request_time = time.time() + spec.get_delay()
        # Decrypt response body
        if spec.use_ec:
            result = json.loads(self._ecc.decode(resp.content))
        else:
            result = resp.json()
        _logger.debug('API result: %r', result)
        return spec.parse_result(result)

    def fetch(self, url: str) -> bytes:
        resp = self._session.get(url)
        return resp.content
