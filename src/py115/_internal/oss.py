__author__ = 'deadblue'

import base64

ENDPOINT='https://oss-cn-shenzhen.aliyuncs.com'

def encode_header_value(v: str) -> str:
    return base64.b64encode(v.encode()).decode()
