__author__ = 'deadblue'

import typing

from py115._internal.protocol.client import Client
from py115._internal.api import qrcode, upload, version

from py115 import login, services
from py115.types import Credential, LoginPlatform


class Cloud(login._Handler):
    """115 cloud service.

    Args:
        credential (py115.types.Credential): Credential object.
        protocol_kwargs (dict): Settings for underlying protocol client.
    """

    _app_ver: str = None
    _client: Client = None
    _upload_helper: upload.Helper = None

    def __init__(
            self, 
            credential: Credential = None, 
            protocol_kwargs: dict = None
        ) -> None:
        # Config protocol client
        protocol_kwargs = protocol_kwargs or {}
        self._client = Client(**protocol_kwargs)
        # Get latest app version
        self._app_ver = self._client.execute_api(version.GetApi())
        self._client.setup_user_agent(
            app_version=self._app_ver
        )
        # Set credential
        if credential is not None:
            self.import_credential(credential)

    def import_credential(self, credential: Credential) -> bool:
        """Import credential to cloud instance.

        Args:
            credential (py115.types.Credential): Credential object to identity user.

        Return:
            bool: Is credential valid.
        """
        self._client.import_cookies(credential.to_dict())
        return self._on_login()

    def export_credentail(self) -> typing.Union[Credential, None]:
        """Export current credentail from cloud instance.

        Return:
            py115.types.Credential: Credential object, or None when credential is invalid.
        """
        # TODO: Check credential before return.
        return Credential.from_dict(
            self._client.export_cookies()
        )

    def qrcode_login(self, platform: LoginPlatform) -> login.QrcodeSession:
        """Start QRcode login session.

        Args:
            platform (py115.types.LoginPlatform): Platform to login.

        Returns:
            py115.login.QrcodeSession: QRcode login session.
        """
        token = self._client.execute_api(qrcode.TokenApi(platform.value))
        return login.QrcodeSession._create(
            client=self._client,
            handler=self,
            platform=platform.value,
            uid=token.get('uid'), 
            time=token.get('time'),
            sign=token.get('sign')
        )

    def _on_login(self) -> bool:
        try:
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
            uh=self._upload_helper
        )
