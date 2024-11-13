__author__ = 'deadblue'

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Generic, TypeVar


R = TypeVar('R')


@dataclass
class ApiTimeout:
    """
    Timeout config for API.
    """

    connect: float
    """Connect timeout in seconds."""
    read: float
    """Read timeout in seconds."""


@dataclass
class Payload:
    """
    Payload describe API request payload.
    """
    
    mime_type: str
    """MIME type of payload content."""

    content: bytes
    """Payload content."""


class ApiSpec(Generic[R], ABC):
    """
    ApiSpec is the super class of all 115 APIs.
    """

    _api_url: str
    _use_ec: bool
    _timeout: ApiTimeout
    query: Dict[str, str]
    form: Dict[str, str]

    def __init__(self, api_url: str, use_ec: bool) -> None:
        self._api_url = api_url
        self._use_ec = use_ec
        self._timeout = ApiTimeout(
            connect=5.0, read=5.0
        )
        self.query = {}
        self.form = {}

    @property
    def use_ec(self) -> bool:
        return self._use_ec

    @property
    def timeout(self) -> ApiTimeout:
        return self._timeout

    def url(self) -> str:
        return self._api_url

    def payload(self) -> Payload | None:
        return None

    @abstractmethod
    def parse_result(self, result: bytes) -> R:
        pass
