__author__ = 'deadblue'

import json
import time
import urllib.parse

import requests

from py115.internal.crypto import ec115


class ApiException(Exception):

    def __init__(self, code: int, *args: object) -> None:
        super().__init__(*args)
        self._error_code = code
    
    @property
    def error_code(self) -> int:
        return self._error_code


class ResponseParser:

    def validate(self, result: dict):
        if result.get('state', False):
            return
        raise ApiException(result.get('err_code', 999999))

    def extract(self, result: dict) -> dict:
        return result.get('data', {})


class Client:

    def __init__(self) -> None:
        self._user_agent = 'Mozilla/5.0'
        session = requests.Session()
        session.headers.update({
            'User-Agent': self._user_agent
        })
        self._session = session

        self._ecc = ec115.Cipher()

    def import_cookie(self, cookies: dict):
        for name, value in cookies.items():
            self._session.cookies.set(
                name, value,
                domain='.115.com'
            )

    def setup_user_agent(self, app_version: str):
        self._user_agent = 'Mozilla/5.0 115Desktop/%s' % app_version
        self._session.headers.update({
            'User-Agent': self._user_agent
        })

    @property
    def user_agent(self):
        return self._user_agent

    def call_api(
            self,
            url: str, 
            params: dict = None, 
            form: dict = None,
            parser: ResponseParser = ResponseParser() 
        ):
        method = 'GET' if form is None else 'POST'
        resp = self._session.request(
            method=method, 
            url=url,
            params=params,
            data=form
        )
        result = resp.json()
        parser.validate(result)
        return parser.extract(result)
    
    def call_secret_api(
            self, 
            url: str, 
            params: dict, 
            form: dict,
            parser: ResponseParser = ResponseParser() 
        ):
        now = int(time.time())
        # Append k_ec parameter
        if params is None:
            params = {}
        params['k_ec'] = self._ecc.encode_token(now)
        # Encode request body
        data = self._ecc.encode(
            urllib.parse.urlencode(form)
        )
        # Send request
        resp = self._session.post(
            url=url, 
            params=params,
            data=data,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        # Decrypt response body
        result = json.loads(
            self._ecc.decode(resp.content)
        )
        parser.validate(result)
        return parser.extract(result)
