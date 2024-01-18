__author__ = 'deadblue'

from typing import Any, Dict, Union

from py115._internal.protocol.client import Client
from py115._internal.api import app, qrcode, upload

from py115 import services
from py115.types import Credential, LoginTarget, QrcodeSession, QrcodeStatus


_app_names = [
    'web', 'mac', 'linux', 'windows'
]


class Cloud:
    """115 cloud service.

    Args:
        credential (Any): Credential object.
        protocol_kwargs (dict): Settings for underlying protocol client.
    """

    _client: Client = None
    _app_ver: str = None
    _app_type: str = None
    _upload_helper: upload.Helper = None

    def __init__(
            self, 
            credential: Any = None, 
            protocol_kwargs: dict = None
        ) -> None:
        # Config protocol client
        protocol_kwargs = protocol_kwargs or {}
        self._client = Client(**protocol_kwargs)
        # Get latest app version
        self._app_ver = self._client.execute_api(app.GetVersionApi())
        self._client.setup_user_agent(
            app_version=self._app_ver
        )
        # Set credential
        if credential is not None:
            self.import_credential(credential)

    def import_credential(self, credential: Any) -> bool:
        """Import credential to cloud instance.

        Args:
            credential (Any): Credential object to identity user.

        Return:
            bool: Is credential valid.
        """
        cookies = _extract_cookies(credential)
        if cookies is None:
            return False
        self._client.import_cookies(cookies)
        return self._check_login()

    def export_credentail(self) -> Union[Credential, None]:
        """Export current credentail from cloud instance.

        Return:
            py115.types.Credential: Credential object, or None when credential is invalid.
        """
        # TODO: Check credential before return.
        return Credential.from_dict(
            self._client.export_cookies()
        )

    def qrcode_login(self, target: LoginTarget = LoginTarget.Web) -> QrcodeSession:
        """Start QRcode login session.

        Args:
            app_type (py115.types.AppType): App to login.

        Returns:
            py115.types.QrcodeSession: QRcode login session.
        """
        app_name = _app_names[target.value]
        token = self._client.execute_api(qrcode.TokenApi(app_name))
        qrcode_image = self._client.fetch(
            qrcode.get_image_url(app_name, token.get('uid'))
        )
        return QrcodeSession._create(
            app_name=app_name,
            uid=token.get('uid'), 
            time=token.get('time'),
            sign=token.get('sign'),
            image=qrcode_image
        )

    def qrcode_poll(self, session: QrcodeSession) -> QrcodeStatus:
        """Poll QRcode login status.

        Args:
            session (py115.types.QrcodeSession): QRcode login session.
        
        Returns:
            py115.types.QrcodeStatus: QRcode status.
        """
        status = self._client.execute_api(qrcode.StatusApi(
            uid=session._uid, time=session._time, sign=session._sign
        ))
        if status == 2:
            self._client.execute_api(qrcode.LoginApi(
                app_name=session._app_name, 
                uid=session._uid
            ))
            if self._check_login():
                return QrcodeStatus.Done
            else:
                return QrcodeStatus.Failed
        elif status < 0:
            return QrcodeStatus.Expired
        return QrcodeStatus.Waiting

    def _check_login(self) -> bool:
        try:
            # Get login app type
            self._app_type = self._client.execute_api(app.GetTypeApi())
            # Get upload key
            user_id, user_key = self._client.execute_api(upload.InfoApi())
            self._upload_helper = upload.Helper(
                self._app_ver, user_id, user_key
            )
            return True
        except:
            return False

    def offline(self) -> services.OfflineService:
        """Get offline service.

        Return:
            py115.services.OfflineService: Offline service instance.
        """
        return services.OfflineService._create(
            client=self._client, 
            app_ver=self._app_ver, 
            user_id=self._upload_helper.user_id
        )

    def storage(self) -> services.StorageService:
        """Get storage service.

        Return:
            py115.services.StorageService: Storage service instance.
        """
        return services.StorageService._create(
            client=self._client,
            app_type=self._app_type,
            uh=self._upload_helper
        )

def _extract_cookies(credential: Any) -> Union[Dict[str, str], None]:
    if isinstance(credential, Credential):
        return credential.to_dict()
    # Handle dict or object
    raw: Dict[str, Any] = None
    if isinstance(credential, dict):
        raw = credential
    elif hasattr(credential, '__dict__'):
        raw = credential.__dict__
    if raw is None:
        return None
    # Extract cookies from credentials
    cookies = {}
    for key, value in raw.items():
        key = key.upper()
        if key in ('UID', 'CID', 'SEID'):
            cookies[key] = str(value)
    return cookies
