__author__ = 'deadblue'

import json
import base64
from typing import Dict

REGION = 'cn-shenzhen'

ENDPOINT='https://oss-cn-shenzhen.aliyuncs.com'


def replace_callback_sha1(callback: str, file_sha1: str) -> str:
    cb_obj = json.loads(callback)
    cb_obj['callbackBody'] = cb_obj['callbackBody'].replace('${sha1}', file_sha1)
    return json.dumps(cb_obj)


def encode_header_value(v: str) -> str:
    return base64.b64encode(v.encode()).decode()
