__author__ = 'deadblue'

from typing import (
    Any, Dict, Iterable, Tuple
)

from py115.lowlevel import Client
from py115.lowlevel.api import *
from py115.lowlevel.types import (
    CommonParams,
    AppName, 
    QrcodeClient, 
    QrcodeStatus
)
from py115.types import (
    Credential, QrcodeSession, File, Task
)


class OfflineService:

    _lac: Client
    _lcp: CommonParams

    def __init__(self, lac: Client, lcp: CommonParams) -> None:
        self._lac, self._lcp = lac, lcp
    
    def list(self) -> Iterable[Task]:
        page_num = 1
        while True:
            result = self._lac.call_api(OfflineListApi(page_num))
            yield from result.tasks
            page_num += 1
            if page_num > result.page_count:
                break

    def add(self, *urls: str, save_dir_id: str | None = None):
        if len(urls) == 0: return
        self._lac.call_api(OfflineAddUrlsApi(
            self._lcp, 
            urls, 
            save_dir_id=save_dir_id
        ))

    def delete(self, *task_ids: str, delete_files: bool = False):
        if len(task_ids) == 0: return
        self._lac.call_api(OfflineDeleteApi(
            info_hashes=task_ids, 
            delete_files=delete_files
        ))


class StorageService:

    _lac: Client
    _lcp: CommonParams

    def __init__(self, lac: Client, lcp: CommonParams) -> None:
        self._lac, self._lcp = lac, lcp
    
    def list_files(self, dir_id: str) -> Iterable[File]:
        spec = FileListApi(
            dir_id=dir_id,
            offset=0,
            limit=24
        )
        while True:
            result = self._lac.call_api(spec)
            yield from result.files
            spec.offset += result.limit
            if spec.offset >= result.count: break

    def search_files(self, dir_id: str, keyword: str) -> Iterable[File]:
        spec = FileSearchApi(
                keyword=keyword,
                dir_id=dir_id,
                offset=0,
                limit=24
            )
        while True:
            result = self._lac.call_api(spec)
            yield from result.files
            spec.offset += result.limit
            if spec.offset >= result.count: break


class Cloud:
    """115 cloud service."""

    _lac: Client
    _lcp: CommonParams

    def __init__(
            self, 
            credential: Any = None,
            *,
            app_ver: str | None = None
        ) -> None:
        self._lac = Client()
        # Get app version
        if app_ver is None:
            avr = self._lac.call_api(AppVersionApi())
            app_ver = avr.get(AppName.BROWSER_WINDOWS).version_code
        self._lac.set_user_agent(f'Mozilla/5.0 115Browser/{app_ver}')
        self._lcp = CommonParams(app_ver)
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
        self._lac.import_cookies(cookies)
        self._after_login()
        return True

    def _after_login(self):
        result = self._lac.call_api(UploadInfoApi())
        self._lcp.set_user_info(
            user_id=result.user_id,
            user_key=result.user_key
        )

    def export_credentail(self) -> Credential | None:
        """Export current credentail from cloud instance.

        Return:
            py115.types.Credential: Credential object, or None when credential is invalid.
        """
        cookies = self._lac.export_cookies()
        cred = Credential(
            uid=cookies.get('UID', None),
            cid=cookies.get('CID', None),
            seid=cookies.get('SEID', None)
        )
        return cred if cred else None

    def qrcode_start(self, client: QrcodeClient = QrcodeClient.WEB) -> QrcodeSession:
        """Start a QRcode login session.

        Args:
            client (QrcodeClient): Client type to simulate login.

        Returns:
            QrcodeSession: QRcode login session.
        """
        token = self._lac.call_api(QrcodeTokenApi(client=client))
        qrcode_image = self._lac.fetch(
            qrcode_get_image_url(client, token.uid)
        )
        return QrcodeSession(
            client=client,
            uid=token.uid,
            time=token.time,
            sign=token.sign,
            image_data=qrcode_image
        )

    def qrcode_poll(self, session: QrcodeSession) -> bool:
        """Poll QRcode login status.

        Args:
            session (QrcodeSession): QRcode login session.
        
        Returns:
            bool: True when login is done.
        """
        status = self._lac.call_api(QrcodeStatusApi(
            uid=session._uid,
            time=session._time,
            sign=session._sign
        ))
        if status == QrcodeStatus.ALLOWED:
            self._lac.call_api(QrcodeLoginApi(
                client=session._client,
                uid=session._uid
            ))
            self._after_login()
            return True
        elif status == QrcodeStatus.EXPIRED:
            # TODO: Raise custom exception.
            raise Exception('QRcode expired!')
        return False

    def offline(self) -> OfflineService:
        """Get offline service.

        Return:
            OfflineService: Offline service instance.
        """
        return OfflineService(self._lac, self._lcp)

    def storage(self) -> StorageService:
        """Get storage service.

        Return:
            StorageService: Storage service instance.
        """
        return StorageService(self._lac, self._lcp)

    def lowlevel(self) -> Tuple[Client, CommonParams]:
        """Get lowlevel client and parameters

        Returns:
            py115.lowlevel.Client: Low-level client for API calling.
            py115.lowlevel.types.CommonParams: Common-used parameters for low-leve API.
        """
        return (self._lac, self._lcp)


def _convert_to_cookies(credential: Any) -> Dict[str, str] | None:
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
