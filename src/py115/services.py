__author__ = 'deadblue'

import os.path as ospath
from typing import (
    BinaryIO, Generator, Sequence, Tuple
)

from py115.lowlevel import (
    Client, CommonParams, api, utils
)
from py115 import types
from py115.types import (
    DownloadTicket,
    UploadTicket,
)


class OfflineService:
    """Offline task manager."""

    _llc: Client
    _cp: CommonParams

    def __init__(self, llc: Client, cp: CommonParams) -> None:
        self._llc = llc
        self._cp = cp

    def list(self) -> Generator[types.Task, None, None]:
        """Get all tasks.

        Yields:
            py115.types.Task: Task object
        """
        spec = api.OfflineListApi(page_num=1)
        while True:
            result = self._llc.call_api(spec)
            for task_obj in result.tasks:
                yield types.Task(task_obj)
            if result.page_num < result.page_count:
                spec.set_page(result.page_num + 1)
            else:
                break

    def add_url(self, *urls: str) -> Sequence[types.Task]:
        """Create task(s) from download URL.

        Args:
            *urls (str): Download URL, can be a http/ftp/ed2k/magnet link.

        Return:
            Iterable[py115.types.Task]: Task list for the download URLs.
        """
        if len(urls) == 0:
            return []
        add_results = self._llc.call_api(api.OfflineAddUrlsApi(
            self._cp, urls
        ))
        return [types.Task._create(r) for r in add_results]

    def delete(self, *task_ids: str):
        """Delete task(s).

        Args:
            *task_ids (str): The ID of tasks you wants to delete.
        """
        if len(task_ids) == 0:
            return
        self._llc.call_api(api.OfflineDeleteApi(task_ids))

    def clear(self, status: types.TaskStatus = types.TaskStatus.COMPLETE):
        """Clear tasks.

        Args:
            status (py115.types.TaskStatus): 
                Tasks in given status will be cleared. Set status to None to 
                clear all tasks.
        """
        spec = api.OfflineClearApi()
        self._llc.call_api(spec)


class StorageService:
    """Cloud file/directory manager."""

    _llc: Client
    _cp: CommonParams

    def __init__(self, llc: Client, cp: CommonParams) -> None:
        self._llc = llc
        self._cp = cp

    def space(self) -> Tuple[int, int]:
        """
        Get total size and used size of the storage.

        Returns:
            Tuple[int, int]: Total size and used size in byte.
        """
        result = self._llc.call_api(api.SpaceInfoApi())
        return (result.total_size, result.used_size)

    def list(self, dir_id: str = '0') -> Generator[types.File, None, None]:
        """Get files under a directory.

        Args:
            dir_id (str): Directory ID to list, default is "0" which means root directory.

        Yields:
            py115.types.File: File object under the directory.
        """
        spec = api.FileListApi(dir_id=dir_id, limit=32)
        while True:
            result = self._llc.call_api(spec)
            for file_obj in result.files:
                yield types.File(file_obj)
            next_offset = result.offset + result.limit
            if next_offset >= result.count:
                break
            else:
                spec.set_offset(next_offset)

    def search(self, keyword: str, dir_id: str = '0'):
        """Recursively search files under a directory.

        Args:
            keyword (str): Keyword to search files.
            dir_id (str): Directory ID to search.

        Yields:
            py115.types.File: File object whose name contains the keyword.
        """
        spec = api.FileSearchApi(keyword=keyword, dir_id=dir_id)
        while True:
            result = self._llc.call_api(spec)
            for file_obj in result.files:
                yield types.File(file_obj)
            next_offset = result.offset + result.limit
            if next_offset >= result.count:
                break
            else:
                spec.set_offset(next_offset)

    def move(self, target_dir_id: str, *file_ids: str):
        """Move files to a directory.

        Args:
            target_dir_id (str): ID of target directory where to move files.
            *file_ids (str): ID of files to be moved.
        """
        if len(file_ids) == 0:
            return
        self._llc.call_api(api.FileMoveApi(target_dir_id, file_ids))

    def rename(self, file_id: str, new_name: str):
        """Rename file.
        
        Args:
            file_id (str): ID of file to be renamed.
            new_name (str): New name for the file.
        """
        self._llc.call_api(api.FileRenameApi({
            file_id: new_name
        }))

    def batch_rename(self, *pairs: Tuple[str, str]):
        """Batch rename files

        Args:
            *pair (Tuple[str, str]): Pair of file_id and new_name.
        """
        new_names = {}
        for file_id, new_name in pairs:
            new_names[file_id] = new_name
        self._llc.call_api(api.FileRenameApi(new_names))

    def delete(self, *file_ids: str):
        """Delete files.

        Args:
            *file_ids (str): ID of files to be deleted.
        """
        if len(file_ids) == 0:
            return
        self._llc.call_api(api.FileDeleteApi(file_ids))

    def make_dir(self, parent_id: str, name: str) -> str:
        """Make new directory under a directory.
        
        Args:
            parent_id (str): ID of parent directory where to make new directory.
            name (str): Name for the new directory.
        
        Return:
            str: File ID for the created directory.
        """
        return self._llc.call_api(api.DirAddApi(
            parent_id=parent_id,
            dir_name=name
        ))

    def request_download(self, pickcode: str) -> types.DownloadTicket:
        """Download file from cloud storage.

        Args:
            pickcode (str): Pick code of file.

        Returns:
            py115.types.DownloadTicket: A ticket contains all required fields to 
            download file from cloud.
        """
        result = self._llc.call_api(api.DownloadApi(pickcode))
        if result is None:
            return None
        ticket = DownloadTicket(
            url=result.url,
            file_name=result.file_name,
            file_size=result.file_size
        )
        # Export cookies for download URL
        cookies = self._llc.export_cookies(target_url=result.url)
        ticket.headers.update({
            'User-Agent': self._llc.user_agent,
            'Cookie': '; '.join([
                f'{k}={v}' for k, v in cookies.items()
            ])
        })
        return ticket

    def request_upload(self, dir_id: str, file_path: str) -> types.UploadTicket:
        """Upload local file to cloud storage.

        Args:
            dir_id (str): ID of directory where to store the file.
            file_path (str): Path of the local file.
        
        Return:
            py115.types.UploadTicket: A ticket contains all required fields to
            upload file to cloud, should be used with aliyun-oss-python-sdk.
        """
        if not ospath.exists(file_path):
            return None
        file_name = ospath.basename(file_path)
        with open(file_path, 'rb') as fp:
            return self.request_upload_data(dir_id, file_name, fp)

    def request_upload_data(
            self, 
            dir_id: str, 
            save_name: str, 
            stream: BinaryIO, 
        ) -> types.UploadTicket:
        """Upload data as a file to cloud storage.

        Args:
            dir_id (str): ID of directory where to store the file.
            save_name (str): File name to be saved.
            stream (BinaryIO): IO stream of data.

        Return:
            py115.types.UploadTicket: A ticket contains all required fields to
            upload file to cloud, should be used with aliyun-oss-python-sdk.
        """
        if not (stream.readable() and stream.seekable()):
            return None
        
        dr = utils.digest(stream)
        init_spec = api.UploadInitApi(
            cp=self._cp,
            dir_id=dir_id,
            file_name=save_name,
            file_size=dr.size,
            file_sha1=dr.sha1
        )
        while True:
            init_ret = self._llc.call_api(init_spec)
            if isinstance(init_ret, api.UploadInitSignResult):
                sign_value = utils.digest_range(stream, init_ret.sign_range)
                init_spec.update_token(init_ret.sign_key, sign_value)
            elif isinstance(init_ret, api.UploadInitDoneResult):
                ticket = UploadTicket()
                ticket.is_done = True
                ticket.pickcode = init_ret.pickcode
                return ticket
            elif isinstance(init_ret, api.UploadInitOssResult):
                token = self._llc.call_api(api.UploadTokenApi())
                ticket = UploadTicket()
                ticket.is_done = False
                ticket.oss_key_id = token.access_key_id
                ticket.oss_key_secret = token.access_key_secret
                ticket.oss_security_token = token.security_token
                ticket.oss_endpoint = init_ret.endpoint
                ticket.bucket_name = init_ret.bucket
                ticket.object_key = init_ret.object
                ticket.callback_url = init_ret.callback
                ticket.callback_var = init_ret.callback_var
                ticket.expiration = token.expiration
                return ticket
            else:
                return None

    def request_play(self, pickcode: str) -> types.PlayTicket:
        """Play a video file on cloud, returns required parameters as a ticket.

        Args:
            pickcode (str): Pick code of file.
        
        Returns:
            py115.types.PlayTicket: A ticket contains all required fields to 
            play the media file on cloud.
        """
        if self._app_type == 'web':
            spec = api.VideoPlayWebApi(pickcode=pickcode)
        else:
            spec = api.VideoPlayDesktopApi(pickcode=pickcode, cp=self._cp)
        play_url = self._llc.call_api(spec)
        ticket = types.PlayTicket(
            url=play_url
        )
        if self._app_type == 'web':
            # Prepare headers for playing
            cookies = self._llc.export_cookies(url=ticket.url)
            ticket.headers.update({
                'User-Agent': self._client.user_agent,
                'Cookie': '; '.join([
                    f'{k}={v}' for k, v in cookies.items()
                ])
            })
        return ticket
