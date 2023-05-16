__author__ = 'deadblue'

from py115._internal.protocol.client import Client
from py115._internal.api import upload, version

from py115.services import OfflineService, StorageService
from py115.types import Credential


class Cloud:
    """115 cloud service.
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

    def import_credential(self, credential: Credential):
        """Setup credential for cloud service.

        :param credential: Credential object.
        :type credential: Credential
        """
        self._client.import_cookies(credential.to_dict())
        # Initialize upload helper
        user_id, user_key = self._client.execute_api(upload.InfoApi())
        self._upload_helper = upload.Helper(
            self._app_ver, user_id, user_key
        )

    def export_credentail(self) -> Credential:
        """Export current credentail that cloud service used.

        :return: Credential object.
        :rtype: Credential
        """
        return Credential.from_dict(
            self._client.export_cookies()
        )

    def offline(self) -> OfflineService:
        """Get offline service.

        :return: Offline service instance.
        :rtype: OfflineService
        """
        return OfflineService._create(
            client=self._client, 
            app_ver=self._app_ver, 
            user_id=self._upload_helper.user_id
        )

    def storage(self) -> StorageService:
        """Get storage service.

        :return: Storage service instance.
        :rtype: StorageService
        """
        return StorageService._create(
            client=self._client,
            uh=self._upload_helper
        )
