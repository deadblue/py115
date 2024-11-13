__author__ = 'deadblue'

from typing import Any, Dict


class ApiException(Exception):

    _ec: int
    _result: Dict[str, Any]

    def __init__(
            self, 
            error_code: int, 
            result: Dict[str, Any] = None
        ) -> None:
        self._ec = error_code
        self._result = result
        super().__init__(f'API error: {error_code}')
   
    @property
    def error_code(self) -> int:
        return self._ec

    @property
    def raw_result(self) -> Dict[str, Any]:
        return self._result


class RetryException(Exception):

    def __init__(self) -> None:
        super().__init__()

