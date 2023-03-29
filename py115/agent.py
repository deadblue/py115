__author__ = 'deadblue'

import random
import time
from typing import Generator

from py115.internal.webapi import client, api, file

class Agent:

    def __init__(self) -> None:
        self._client = client.Client()
        version_data = self._client.call_api(url=api.version_get)
        self._client.setup_user_agent(
            app_version=version_data['linux_115']['version_code']
        )
        # What's this?
        self._pro_key = 0 - random.randint(0, 100)
        self._pro_index = 0

    def _create_pro_id(self) -> str:
        pro_id = '%d_%d_%d' % (
            int(time.time() * 1000), 
            self._pro_key, self._pro_index
        )
        self._pro_index += 1

    def set_cookie(self, cookies: dict):
        self._client.import_cookie(cookies)
        self._client.call_api(api.user_get)

    def file_list(self, dir_id: str) -> Generator[file.File, None, None]:
        params = {
            'aid': '1',
            'cid': dir_id,
            'o': 'user_ptime',
            'asc': '0',
            'show_dir': '1',
            'offset': '0',
            'limit': '32',
            'natsort': '1',
            'format': 'json'
        }
        parser = file.FileListResponseParser()
        while True:
            result = self._file_list_internal(params, parser)
            for f in result['files']:
                yield f
            next_offset = result['offset'] + len(result['files'])
            if next_offset >= result['count']:
                break
            else:
                params['offset'] = next_offset

    def _file_list_internal(self, params, parser) -> dict:
        retry = True
        while retry:
            if params['o'] == 'file_name':
                api_url = api.file_list_by_name
            else:
                api_url = api.file_list
            try: 
                result = self._client.call_api(
                    url=api_url, params=params, parser=parser
                )
                return result
            except file.FileListException as ae:
                params['o'] = ae.order
                params['asc'] = ae.is_asc
        return None

    def file_move(self, dir_id: str, *file_ids: str):
        form = {
            'pid': dir_id,
            'move_proid': self._create_pro_id()
        }
        for index, fid in enumerate(file_ids):
            key = 'fid[%d]' % index
            form[key] = fid
        self._client.call_api(
            url=api.file_move, form=form
        )

    def file_rename(self, file_id: str, new_name: str):
        key = 'files_new_name[%s]' % file_id
        self._client.call_api(
            url=api.file_rename, form={
                key: new_name
            }
        )

    def file_delete(self, dir_id: str, *file_ids: str):
        form = {
            'pid': dir_id,
            'ignore_warn': '1'
        }
        for index, fid in enumerate(file_ids):
            key = 'fid[%d]' % index
            form[key] = fid
        self._client.call_api(
            url=api.file_delete, form=form
        )