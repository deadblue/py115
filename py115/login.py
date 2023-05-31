__author__ = 'deadblue'

import logging

from py115._internal.api import qrcode
from py115._internal.protocol.client import Client


_logger = logging.getLogger(__name__)


class _Handler:

    def _on_login(self) -> bool:
        return True


class QrcodeSession:
    """QRcode login session."""

    _client: Client
    _handler: _Handler
    _platform: str
    _uid: str
    _time: int
    _sign: str

    image_data: bytes
    """QRcode image data"""

    @classmethod
    def _create(cls, client: Client, handler: _Handler, platform: str, uid: str, time: int, sign: str):
        s = cls()
        s._client = client
        s._handler = handler
        s._platform = platform
        s._uid = uid
        s._time = time
        s._sign = sign
        s.image_data = client.fetch(qrcode.get_image_url(platform, uid))
        return s

    def poll(self) -> bool:
        """Poll QRcode status.
        This method will block until login is done, or QRcode is invalid.

        Returns:
            bool: Is login succeeded.
        """
        while True:
            # Query QRcode status
            status = self._client.execute_api(qrcode.StatusApi(
                uid=self._uid,
                time=self._time,
                sign=self._sign
            ))
            if status == 2:
                # Allowed, start login
                self._client.execute_api(qrcode.LoginApi(
                    platform=self._platform,
                    uid=self._uid
                ))
                return self._handler._on_login()
                
            elif status < 0:
                # Canceled or Expired
                return False
            else:
                # Waiting or Scanned
                _logger.debug('Continue waiting, status: %d', status)
