__author__ = 'deadblue'

import json
from abc import abstractmethod
from typing import Any, Dict, TypeVar, Union
from urllib.parse import urlencode

from py115.lowlevel._crypto import m115
from py115.lowlevel.api._json import JsonApiSpec, JsonResult


R = TypeVar('R')
M115Result = Dict[str, Any]

class M115ApiSpec(JsonApiSpec[R]):

    _mkey: bytes

    def __init__(self, api_url: str, use_ec: bool = False) -> None:
        super().__init__(api_url, use_ec)
        self._mkey = m115.generate_key()

    def payload(self) -> Union[bytes, None]:
        data = m115.encode(self._mkey, json.dumps(self.form))
        return urlencode({
            'data': data
        }).encode()

    def _parse_json_result(self, json_obj: JsonResult) -> R:
        m115_obj = m115.decode(self._mkey, json_obj.get('data'))
        return self._parse_m115_result(json.loads(m115_obj))
    
    @abstractmethod
    def _parse_m115_result(self, m115_obj: M115Result) -> R:
        pass
