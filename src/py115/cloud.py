__author__ = 'deadblue'

from typing import Any, Dict, Tuple, Union

from py115.lowlevel import (
    Client, CommonParams, api
)
from py115.lowlevel.api.app import AppType
from py115.services import (
    OfflineService, StorageService
)
from py115.types import (
    Credential, QrcodeSession, QrcodeStatus
)


class Cloud:
    """115 cloud service.

    Args:
        credential (Any): Credential object.
        protocol_kwargs (dict): Settings for underlying protocol client.
    """

    _llc: Client
    """Low-level client"""
    _cp: CommonParams
    """Common parameters for low-level APIs."""

    def __init__(
            self, 
            credential: Any = None, 
            app_ver: Union[str, None] = None
        ) -> None:
        self._llc = Client()
        # Get app version
        if app_ver is None:
            app_ver = self._llc.call_api(api.AppVersionApi())
        self._cp = CommonParams(app_ver)
        self._llc.set_user_agent(f'Mozilla/5.0 115Desktop/{app_ver}')
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
        cookies = _convert_to_cookies(credential)
        if cookies is None:
            return False
        self._llc.import_cookies(cookies)
        return self._after_login()

    def _after_login(self) -> bool:
        try:
            result = self._llc.call_api(api.UploadInfoApi())
            self._cp.set_user_info(
                user_id=result.user_id,
                user_key=result.user_key
            )
            return True
        except:
            return False

    def export_credentail(self) -> Union[Credential, None]:
        """Export current credentail from cloud instance.

        Return:
            py115.types.Credential: Credential object, or None when credential is invalid.
        """
        cookies = self._llc.export_cookies()
        cred = Credential(
            uid=cookies.get('UID'),
            cid=cookies.get('CID'),
            seid=cookies.get('SEID')
        )
        return cred if cred else None

    def qrcode_login(self, app_type: AppType = AppType.WEB) -> QrcodeSession:
        """Start a QRcode login session.

        Args:
            target (py115.types.LoginTarget): Target to simulate login.

        Returns:
            py115.types.QrcodeSession: QRcode login session.
        """
        token = self._llc.call_api(api.QrcodeTokenApi(app_type))
        qrcode_image = self._llc.fetch(
            api.get_qrcode_image_url(app_type, token.uid)
        )
        return QrcodeSession(
            app_type=app_type,
            uid=token.uid,
            time=token.time,
            sign=token.sign,
            image_data=qrcode_image
        )

    def qrcode_poll(self, session: QrcodeSession) -> QrcodeStatus:
        """Poll QRcode login status.

        Args:
            session (py115.types.QrcodeSession): QRcode login session.
        
        Returns:
            py115.types.QrcodeStatus: QRcode status.
        """
        status = self._llc.call_api(api.QrcodeStatusApi(
            uid=session._uid, 
            time=session._time, 
            sign=session._sign
        ))
        if status == api.QrcodeStatus.ALLOWED:
            self._llc.call_api(api.QrcodeLoginApi(
                app_type=session._app_type, 
                uid=session._uid
            ))
            if self._after_login():
                return QrcodeStatus.DONE
            else:
                return QrcodeStatus.FAILED
        elif status == api.QrcodeStatus.EXPIRED:
            return QrcodeStatus.EXPIRED
        return QrcodeStatus.WAITING

    def offline(self) -> OfflineService:
        """Get offline service.

        Return:
            py115.services.OfflineService: Offline service instance.
        """
        return OfflineService(llc=self._llc, cp=self._cp)

    def storage(self) -> StorageService:
        """Get storage service.

        Return:
            py115.services.StorageService: Storage service instance.
        """
        return StorageService(llc=self._llc, cp=self._cp)

    def lowlevel(self) -> Tuple[Client, CommonParams]:
        """Get lowlevel client and parameters

        Returns:
            py115.lowlevel.Client: Low-level client for API calling.
            py115.lowlevel.CommonParams: Common parameters for low-leve API.
        """
        return (self._llc, self._cp)


def _convert_to_cookies(credential: Any) -> Union[Dict[str, str], None]:
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
