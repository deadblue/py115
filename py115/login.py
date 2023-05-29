__author__ = 'deadblue'


from py115._internal.api import qrcode
from py115._internal.protocol.client import Client

class _Handler:

    def _on_login(self) -> bool:
        return True

class QrcodeSession:

    _client: Client
    _handler: _Handler
    _platform: str
    _uid: str
    _time: int
    _sign: str

    image_url: str

    @classmethod
    def _create(cls, client: Client, handler: _Handler, platform: str, uid: str, time: int, sign: str):
        s = cls()
        s._client = client
        s._handler = handler
        s._platform = platform
        s._uid = uid
        s._time = time
        s._sign = sign
        s.image_url = qrcode.get_image_url(platform, uid)
        return s
    
    @property
    def image(self):
        return self._client.fetch(self.image_url)

    def poll(self) -> bool:
        """Wait until QRcode is allowed, canceled or expired.

        Returns:
            bool: Is login succeeded.
        """
        while True:
            status = self._client.execute_api(qrcode.StatusApi(
                uid=self._uid,
                time=self._time,
                sign=self._sign
            ))
            if status < 0:
                return False
            elif status == 2:
                self._client.execute_api(qrcode.LoginApi(
                    platform=self._platform,
                    uid=self._uid
                ))
                return self._handler._on_login()
            else:
                print(f'Continue waiting for status: {status}')
