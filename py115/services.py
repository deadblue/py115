__author__ = 'deadblue'

import os
import os.path
import typing

from py115._internal.api import offline, file, dir, space, upload, video
from py115._internal.protocol.client import Client

from py115 import types


_CLEAR_FLAG_MAPPING = {
    types.TaskStatus.Complete: 1,
    types.TaskStatus.Failed: 2,
    types.TaskStatus.Running: 3
}


class OfflineService:
    """Offline task manager."""

    _client: Client = None
    _app_ver: str = None
    _user_id: str = None

    @classmethod
    def _create(cls, client: Client, app_ver: str, user_id: str):
        s = cls()
        s._client = client
        s._app_ver = app_ver
        s._user_id = user_id
        return s

    def list(self) -> typing.Generator[types.Task, None, None]:
        """Get all tasks.

        Yields:
            py115.types.Task: Task object
        """
        spec = offline.ListApi()
        while True:
            result = self._client.execute_api(spec)
            for t in result['tasks']:
                yield types.Task._create(t)
            page, page_count = result['page'], result['page_count']
            if page < page_count:
                spec.set_page(page + 1)
            else:
                break

    def add_url(self, *urls: str) -> typing.Iterable[types.Task]:
        """Create task(s) from download URL.

        Args:
            *urls (str): Download URL, can be a http/ftp/ed2k/magnet link.

        Return:
            Iterable[py115.types.Task]: Task list for the download URLs.
        """
        if len(urls) == 0:
            return []
        add_results = self._client.execute_api(offline.AddUrlsApi(
            self._app_ver, self._user_id, urls
        ))
        return [types.Task._create(r) for r in add_results]

    def delete(self, *task_ids: str):
        """Delete task(s).

        Args:
            *task_ids (str): The ID of tasks you wants to delete.
        """
        if len(task_ids) == 0:
            return
        self._client.execute_api(offline.DeleteApi(task_ids))

    def clear(self, status: types.TaskStatus = types.TaskStatus.Complete):
        """Clear tasks.

        Args:
            status (py115.types.TaskStatus): 
                Tasks in given status will be cleared. Set status to None to 
                clear all tasks.
        """
        if status is None:
            # Clear all tasks
            flag = 1
        else:
            # Default to clear complete tasks.
            flag = _CLEAR_FLAG_MAPPING.get(status, 0)
        self._client.execute_api(offline.ClearApi(flag))


class StorageService:
    """Cloud file/directory manager."""

    _client: Client
    _app_type: str
    _upload_helper: upload.Helper

    @classmethod
    def _create(cls, client: Client, app_type: str, uh: upload.Helper):
        s = cls()
        s._client = client
        s._app_type = app_type
        s._upload_helper = uh
        return s

    def space(self) -> typing.Tuple[int, int]:
        """
        Get total size and used size of the storage.

        Returns:
            Tuple[int, int]: Total size and used size in byte.
        """
        result = self._client.execute_api(space.GetApi())
        if result is not None:
            total = int(result['all_total']['size'])
            used = int(result['all_use']['size'])
            return (total, used)
        else:
            return (0, 0)

    def list(self, dir_id: str = '0') -> typing.Generator[types.File, None, None]:
        """Get files under a directory.

        Args:
            dir_id (str): Directory ID to list, default is "0" which means root directory.

        Yields:
            py115.types.File: File object under the directory.
        """
        spec = file.ListApi(dir_id)
        while True:
            result = self._client.execute_api(spec)
            for f in result['files']:
                yield types.File._create(f)
            next_offset = result['offset'] + len(result['files'])
            if next_offset >= result['count']:
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
        spec = file.SearchApi(keyword=keyword, dir_id=dir_id)
        while True:
            result = self._client.execute_api(spec)
            for f in result['files']:
                yield types.File._create(f)
            next_offset = result['offset'] + len(result['files'])
            if next_offset >= result['count']:
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
        self._client.execute_api(file.MoveApi(target_dir_id, file_ids))

    def rename(self, file_id: str, new_name: str):
        """Rename file.
        
        Args:
            file_id (str): ID of file to be renamed.
            new_name (str): New name for the file.
        """
        spec = file.RenameApi()
        spec.add_file(file_id, new_name)
        self._client.execute_api(spec)

    def batch_rename(self, *pairs: typing.Tuple[str, str]):
        """Batch rename files

        Args:
            *pair (Tuple[str, str]): Pair of file_id and new_name.
        """
        spec = file.RenameApi()
        for file_id, new_name in pairs:
            spec.add_file(file_id, new_name)
        self._client.execute_api(spec)

    def delete(self, *file_ids: str):
        """Delete files.

        Args:
            *file_ids (str): ID of files to be deleted.
        """
        if len(file_ids) == 0:
            return
        self._client.execute_api(file.DeleteApi(file_ids))

    def make_dir(self, parent_id: str, name: str) -> types.File:
        """Make new directory under a directory.
        
        Args:
            parent_id (str): ID of parent directory where to make new directory.
            name (str): Name for the new directory.
        
        Return:
            py115.types.File: File object of the created directory.
        """
        result = self._client.execute_api(dir.AddApi(parent_id, name))
        result['pid'] = parent_id
        return types.File._create(result)

    def request_download(self, pickcode: str) -> types.DownloadTicket:
        """Download file from cloud storage.

        Args:
            pickcode (str): Pick code of file.

        Returns:
            py115.types.DownloadTicket: A ticket contains all required fields to 
            download file from cloud.
        """
        result = self._client.execute_api(file.DownloadApi(pickcode))
        if result is None or 'url' not in result:
            return None
        ticket = types.DownloadTicket(
            url=result.get('url'),
            file_name=result.get('file_name'),
            file_size=result.get('file_size')
        )
        # Required headers for downloading
        cookies = self._client.export_cookies(url=result['url'])
        ticket.headers.update({
            'User-Agent': self._client.user_agent,
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
        if not os.path.exists(file_path):
            return None
        file_name = os.path.basename(file_path)
        with open(file_path, 'rb') as file_io:
            return self.request_upload_data(dir_id, file_name, file_io)

    def request_upload_data(
            self, 
            dir_id: str, 
            save_name: str, 
            data_io: typing.BinaryIO, 
        ) -> types.UploadTicket:
        """Upload data as a file to cloud storage.

        Args:
            dir_id (str): ID of directory where to store the file.
            save_name (str): File name to be saved.
            data_io (BinaryIO): IO stream of data.

        Return:
            py115.types.UploadTicket: A ticket contains all required fields to
            upload file to cloud, should be used with aliyun-oss-python-sdk.
        """
        if not (data_io.readable() and data_io.seekable()):
            return None
        init_result = self._client.execute_api(upload.InitApi(
            target_id=f'U_1_{dir_id}',
            file_name=save_name,
            file_io=data_io,
            helper=self._upload_helper
        ))
        token_result = None
        if not init_result['done']:
            token_result = self._client.execute_api(upload.TokenApi())
        return types.UploadTicket._create(init_result, token_result)

    def request_play(self, pickcode: str) -> types.PlayTicket:
        """Play a video file on cloud, returns required parameters as a ticket.

        Args:
            pickcode (str): Pick code of file.
        
        Returns:
            py115.types.PlayTicket: A ticket contains all required fields to 
            play the media file on cloud.
        """
        if self._app_type == 'web':
            spec = video.WebPlayApi(pickcode=pickcode)
        else:
            spec = video.PcPlayApi(
                pickcode=pickcode,
                user_id=self._upload_helper.user_id,
                app_ver=self._upload_helper.app_version
            )
        play_url = self._client.execute_api(spec)
        ticket = types.PlayTicket(
            url=play_url
        )
        if self._app_type == 'web':
            # Prepare headers for playing
            cookies = self._client.export_cookies(url=ticket.url)
            ticket.headers.update({
                'User-Agent': self._client.user_agent,
                'Cookie': '; '.join([
                    f'{k}={v}' for k, v in cookies.items()
                ])
            })
        return ticket
