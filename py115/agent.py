__author__ = 'deadblue'

import typing

from py115.internal import protocol
from py115.internal.api import file, offline, version, user

from py115 import models


class Agent:

    def __init__(self, **kwargs) -> None:
        self._client = protocol.Client()
        # Enable debug
        if kwargs.get('debug', False):
            self._client.enable_debug()
        # Get latest app version
        version_data = self._client.execute_api(version.GetApi())
        self._client.setup_user_agent(
            app_version=version_data['linux_115']['version_code']
        )

    def set_cookie(self, cookies: dict):
        self._client.import_cookie(cookies)
        user_info = self._client.execute_api(user.GetApi())


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
                spec.update_offset(next_offset)

    def _file_list_internal(self, spec) -> dict:
        while True:
            try: 
                result = self._client.execute_api(spec)
                return result
            except file.RetryException:
                pass

    def file_move(self, target_dir_id: str, *file_ids: str):
        spec = file.MoveApi(target_dir_id, *file_ids)
        self._client.execute_api(spec)

    def file_rename(self, file_id: str, new_name: str):
        spec = file.RenameApi(file_id, new_name)
        self._client.execute_api(spec)

    def file_delete(self, parent_id: str, *file_ids: str):
        spec = file.DeleteApi(parent_id, *file_ids)
        self._client.execute_api(spec)

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

    def offline_list(self) -> typing.Generator[models.Task, None, None]:
        page = 1
        spec = offline.ListApi(page)
        while True:
            result = self._client.execute_api(spec)
            for task in result['tasks']:
                yield models.Task(task)
            if page < result['page_count']:
                page += 1
                spec.set_page(page)
            else:
                break

    # def offline_add_tasks(self, *urls:str, **kwargs):
    #     # Prepare parameters
    #     save_path = kwargs.pop('save_path', '')
    #     data = {
    #         'ac': 'add_task_urls',
    #         'app_ver': self._client.app_version,
    #         'savepath': save_path,
    #         'uid': '1374893'
    #     }
    #     for i, url in enumerate(urls):
    #         key = 'url[%d]' % i
    #         data[key] = url
    #     key = m115.generate_key()
    #     result = self._client.call_secret_api(
    #         url=api.offline_add_task_urls,
    #         params={
    #             'ac': 'add_task_urls'
    #         },
    #         form={
    #             'data': m115.encode(key, json.dumps(data))
    #         }
    #     )
    #     result = m115.decode(key, result)
    #     _logger.info('Add urls result: %s', result)
    