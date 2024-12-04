__author__ = 'deadblue'

import os.path as ospath
from typing import (
    Any, Dict, Iterable, Tuple, BinaryIO
)

from py115._internal import oss
from py115._internal.crypto.hash import (
    digest, digest_range
)
from py115.lowlevel import Client
from py115.lowlevel.api import *
from py115.lowlevel.types import (
    CommonParams,
    AppName, 
    QrcodeClient, 
    QrcodeStatus,
    OfflineClearFlag,
    UploadInitOssResult,
    UploadInitDoneResult, 
    UploadInitSignResult
)
from py115.types import (
    Credential,
    QrcodeSession, 
    File, Task, 
    DownloadTicket, 
    UploadTicket,
    PlayTicket
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

    def add_urls(self, *urls: str, save_dir_id: str | None = None):
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

    def clear(self, flag: OfflineClearFlag = OfflineClearFlag.DONE):
        self._lac.call_api(OfflineClearApi(flag))


class StorageService:

    _lac: Client
    _lcp: CommonParams

    def __init__(self, lac: Client, lcp: CommonParams) -> None:
        self._lac, self._lcp = lac, lcp

    def list_files(self, dir_id: str) -> Iterable[File]:
        """Retrieve files under a directory.

        Args:
            dir_id (str): Directory ID where to retrive files.

        Yields:
            File: A file object under the directory.
        """
        spec = FileListApi(
            dir_id=dir_id,
            offset=0
        )
        while True:
            result = self._lac.call_api(spec)
            yield from result.files
            spec.offset += result.limit
            if spec.offset >= result.count: break

    def search_files(self, keyword: str, dir_id: str = '0') -> Iterable[File]:
        """Search files with keyword under a directory.

        Args:
            keyword (str): Keyword to search file.

            dir_id (str): Directory ID where to search files.

        Yields:
            File: A file object matches the keyword.
        """
        spec = FileSearchApi(
                keyword=keyword,
                dir_id=dir_id,
                offset=0
            )
        while True:
            result = self._lac.call_api(spec)
            yield from result.files
            spec.offset += result.limit
            if spec.offset >= result.count: break

    def move_files(self, target_dir_id: str, *file_ids: str):
        if len(file_ids) > 0:
            self._lac.call_api(FileMoveApi(
                target_dir_id, file_ids
            ))

    def remove_files(self, *file_ids: str):
        """Remove files from cloud.

        Args:
            *file_ids (str): ID of files to remove.
        """
        if len(file_ids) > 0:
            self._lac.call_api(FileDeleteApi(file_ids))

    def rename_file(self, file_id: str, new_name: str):
        """Rename file.
        """
        self._lac.call_api(FileBatchRenameApi({
            file_id: new_name
        }))

    def make_dir(self, parent_id: str, name: str) -> str:
        """Make a directory under parent directory.

        Args:
            parent_id (str): Parent Directory ID.
            name (str): Base name of new directroy.
        
        Returns:
            str: Created directory ID.
        """
        return self._lac.call_api(DirMakeApi(
            parent_id=parent_id,
            dir_name=name
        ))

    def request_download(self, pickcode: str) -> DownloadTicket:
        """Generate a downlaod ticket which contains all required information
        to download a file.

        Args:
            pickcode (str): Pickcode of file.
        
        Returns:
            DownloadTicket: Ticket to download files.
        """
        dr = self._lac.call_api(DownloadApi(pickcode=pickcode))
        ticket = DownloadTicket(
            url=dr.url,
            file_name=dr.file_name,
            file_size=dr.file_size
        )
        # Fill required headers
        ticket.headers['User-Agent'] = self._lac.user_agent
        cookies = self._lac.export_cookies(target_url=dr.url)
        if len(cookies) > 0:
            ticket.headers['Cookie'] = '; '.join([
                f'{name}={value}' for name, value in cookies.items()
            ])
        return ticket

    def request_upload(
            self, 
            dir_id: str, 
            file_path: str
        ) -> str | UploadTicket:
        """
        Try upload files to cloud.

        Args:
            dir_id (str): Remote directory ID to save the file.
            file_path (str): Local file path to upload.

        Returns:
            str|UploadTicket: 
                When str, it's the pickcode of the rapid-uploaded file.
                Or the upload ticket which contains all required information to 
                upload file to cloud.
        """
        save_name = ospath.basename(file_path)
        with open(file_path, 'rb') as fp:
            return self.request_upload_stream(dir_id, save_name, fp)

    def request_upload_stream(
            self, 
            dir_id: str,
            save_name: str,
            stream: BinaryIO
        ) -> str | UploadTicket:
        """
        Try upload data as a file to cloud.

        Args:
            dir_id (str): Remote directory ID to save the file.
            save_name (str): File name to save data on cloud.
            stream (BinaryIO): Data stream.

        Returns:
            str|UploadTicket: 
                When str, it's the pickcode of the rapid-uploaded data.
                Or the upload ticket which contains all required information to 
                upload data to cloud.
        """
        if not stream.seekable():
            # TODO: Use custom exception
            raise Exception('Can not upload unseekable stream!')
        dr = digest(stream)
        spec = UploadInitApi(
            self._lcp, dir_id, save_name, dr.size, dr.sha1
        )
        result = self._lac.call_api(spec)
        while True:
            if isinstance(result, UploadInitSignResult):
                spec.update_token(
                    sign_key=result.sign_key,
                    sign_value=digest_range(stream, result.sign_range)
                )
                result = self._lac.call_api(spec)
            elif isinstance(result, UploadInitDoneResult):
                return result.pickcode
            elif isinstance(result, UploadInitOssResult):
                token = self._lac.call_api(UploadTokenApi())
                return UploadTicket(
                    region=oss.REGION,
                    endpoint=oss.ENDPOINT,
                    access_key_id=token.access_key_id,
                    access_key_secret=token.access_key_secret,
                    security_token=token.security_token,
                    bucket_name=result.bucket,
                    object_key=result.object,
                    callback=oss.encode_header_value(
                        oss.replace_callback_sha1(result.callback, dr.sha1)
                    ),
                    callback_var=oss.encode_header_value(result.callback_var),
                    expiration=token.expiration
                )
    
    def request_play(self, pickcode: str) -> PlayTicket:
        """Generate a play ticket which contains all required information
        to download a video file.

        Args:
            pickcode (str): Pickcode of video file.
        
        Returns:
            PlayTicket: Ticket to play video file.
        """
        result = self._lac.call_api(VideoPlayWebApi(pickcode=pickcode))
        ticket = PlayTicket(result.play_url)
        ticket.headers['User-Agent'] = self._lac.user_agent
        cookies = self._lac.export_cookies(target_url=result.play_url)
        if len(cookies) > 0:
            ticket.headers['Cookie'] = '; '.join([
                f'{name}={value}' for name, value in cookies.items()
            ])
        return ticket


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
        self._lac.add_to_user_agent(f'115Browser/{app_ver}')
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
        """Export lowlevel client and parameters

        Returns:
            Client: Low-level API client.
            CommonParams: Common-used parameters for low-leve API.
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
