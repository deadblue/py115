__author__ = 'deadblue'

import os
import typing

from py115._internal.api import file, dir, space, upload
from py115._internal.protocol.client import Client

from py115.types import File, DownloadTicket, UploadTicket


class StorageService:

    _client: Client = None
    _upload_helper: upload.Helper = None

    @classmethod
    def _create(cls, client: Client, uh: upload.Helper):
        s = cls()
        s._client = client
        s._upload_helper = uh
        return s

    def space(self) -> typing.Tuple[int, int]:
        """
        Get total size and used size of the storage.
        The unit of returned sizes is byte.

        :return: (total_size, used_size)
        """
        result = self._client.execute_api(space.GetApi())
        if result is not None:
            total = int(result['all_total']['size'])
            used = int(result['all_use']['size'])
            return (total, used)
        else:
            return (0, 0)

    def list(self, dir_id: str = '0') -> typing.Generator[File, None, None]:
        """
        Get files under a cloud directory.

        :param dir_id: The ID of cloud directory.
        :return: Files genetator.
        """
        spec = file.ListApi(dir_id)
        while True:
            result = self._client.execute_api(spec)
            for f in result['files']:
                yield File(f)
            next_offset = result['offset'] + len(result['files'])
            if next_offset >= result['count']:
                break
            else:
                spec.set_offset(next_offset)

    def move(self, target_dir_id: str, *file_ids: str) -> None:
        self._client.execute_api(file.MoveApi(target_dir_id, *file_ids))

    def rename(self, file_id: str, new_name: str) -> None:
        self._client.execute_api(file.RenameApi(file_id, new_name))

    def delete(self, parent_id: str, *file_ids: str) -> None:
        self._client.execute_api(file.DeleteApi(parent_id, *file_ids))

    def make_dir(self, parent_id: str, name: str) -> File:
        result = self._client.execute_api(dir.AddApi(parent_id, name))
        result['pid'] = parent_id
        return File(result)

    def download(self, pickcode: str) -> DownloadTicket:
        result = self._client.execute_api(file.DownloadApi(pickcode))
        if len(result.values()) > 0:
            _, down_info = result.popitem()
            ticket = DownloadTicket(down_info)
            ticket.headers.update({
                'User-Agent': self._client.user_agent
            })
            return ticket
        return None

    def upload_file(self, dir_id: str, file_path: str) -> UploadTicket:
        """
        Upload local file to cloud storage.

        :param dir_id: Directory ID on cloud storage.
        :param file_path: Local file path.
        """
        if not os.path.exists(file_path):
            return None
        file_name = os.path.basename(file_path)
        with open(file_path, 'rb') as file_io:
            return self.upload_data(dir_id, file_name, file_io)

    def upload_data(
            self, 
            dir_id: str, 
            file_name: str, 
            file_io: typing.BinaryIO, 
        ) -> UploadTicket:
        """
        Upload data as a file to cloud storage.

        :param dir_id: Directory ID on cloud storage.
        :param file_name: File name to be saved on cloud storage.
        :param file_io: Data stream.
        """
        if not (file_io.readable() and file_io.seekable()):
            return None
        init_result = self._client.execute_api(upload.InitApi(
            target_id=f'U_1_{dir_id}',
            file_name=file_name,
            file_io=file_io,
            helper=self._upload_helper
        ))
        ticket = UploadTicket(init_result)
        if not ticket.is_done:
            token_result = self._client.execute_api(upload.TokenApi())
            ticket.set_oss_token(token_result)
        return ticket
