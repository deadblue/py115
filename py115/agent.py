__author__ = 'deadblue'

import os.path
import typing

from py115 import models
from py115.internal.protocol import api, client
from py115.internal.api import file, dir, task, version, upload
from py115.types import TaskClearFlag

class Agent:

    _app_ver: str = None
    _user_id: int = None
    _upload_helper: upload.Helper = None

    def __init__(self, protocol_kwargs: dict = None) -> None:
        # Config protocol client
        protocol_kwargs = protocol_kwargs or {}
        self._client = client.Client(**protocol_kwargs)
        # Get latest app version
        self._app_ver = self._client.execute_api(version.GetApi())
        self._client.setup_user_agent(
            app_version=self._app_ver
        )

    def set_cookie(self, cookies: dict):
        self._client.import_cookie(cookies)
        # Init upload helper
        user_id, user_key = self._client.execute_api(upload.InfoApi())
        self._upload_helper = upload.Helper(
            self._app_ver, user_id, user_key
        )

    def file_list(self, dir_id: str) -> typing.Generator[models.File, None, None]:
        spec = file.ListApi(dir_id)
        while True:
            result = self._file_list_internal(spec)
            for f in result['files']:
                yield models.File(f)
            next_offset = result['offset'] + len(result['files'])
            if next_offset >= result['count']:
                break
            else:
                spec.set_offset(next_offset)
    def _file_list_internal(self, spec) -> dict:
        while True:
            try: 
                result = self._client.execute_api(spec)
                return result
            except api.RetryException:
                pass

    def file_move(self, target_dir_id: str, *file_ids: str):
        self._client.execute_api(file.MoveApi(target_dir_id, *file_ids))

    def file_rename(self, file_id: str, new_name: str):
        self._client.execute_api(file.RenameApi(file_id, new_name))

    def file_delete(self, parent_id: str, *file_ids: str):
        self._client.execute_api(file.DeleteApi(parent_id, *file_ids))

    def file_download(self, pickcode: str) -> models.DownloadTicket:
        spec = file.DownloadApi(pickcode)
        result = self._client.execute_api(spec)
        if len(result.values()) > 0:
            file_id, down_info = result.popitem()
            ticket = models.DownloadTicket(down_info)
            ticket.headers.update({
                'User-Agent': self._client.user_agent
            })
            return ticket
        return None

    def dir_add(self, parent_id: str, name: str) -> models.File:
        result = self._client.execute_api(dir.AddApi(parent_id, name))
        # TODO: Format result
        return None

    def upload_file(self, dir_id: str, file_path: str) -> models.UploadTicket:
        """
        Upload local file to cloud storage.

        :param dir_id: Directory ID on cloud storage.
        :param file_path: Local file path/
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
        ) -> models.UploadTicket:
        """
        Upload data as a file to cloud storage.

        :param dir_id: Directory ID on cloud storage.
        :param file_name: File name to be saved on cloud storage.
        :param file_io: 
        """
        if not (file_io.readable() and file_io.seekable()):
            return None
        spec = upload.InitApi(
            target_id=f'U_1_{dir_id}',
            file_name=file_name,
            file_io=file_io,
            helper=self._upload_helper
        )
        while True:
            try:
                init_result = self._client.execute_api(spec)
                break
            except api.RetryException:
                pass
        ticket = models.UploadTicket(init_result)
        if not ticket.is_done:
            token_result = self._client.execute_api(upload.TokenApi())
            ticket.set_oss_token(token_result)
        return ticket

    def task_list(self) -> typing.Generator[models.Task, None, None]:
        spec = task.ListApi()
        while True:
            result = self._client.execute_api(spec)
            for t in result['tasks']:
                yield models.Task(t)
            page, page_count = result['page'], result['page_count']
            if page < page_count:
                spec.set_page(page + 1)
            else:
                break

    def task_add_urls(self, *urls: str):
        """
        Add tasks by URLs.
        """
        add_results = self._client.execute_api(task.AddUrlsApi(
            self._app_ver, self._user_id, *urls
        ))
        return [models.Task(r) for r in add_results]

    def task_delete(self, *task_ids: str):
        """
        Delete tasks.

        :param task_ids: ID of task to delete.
        """
        self._client.execute_api(task.DeleteApi(*task_ids))

    def task_clear(self, target: TaskClearFlag = TaskClearFlag.Done):
        """
        Clear offline tasks.
        """
        self._client.execute_api(task.ClearApi(target.value))
