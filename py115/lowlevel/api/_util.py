__author__ = 'deadblue'

from datetime import datetime, timezone, timedelta
from typing import Any


_tz_cst = timezone(
    offset=timedelta(hours=8),
    name='Asia/Shanghai'
)

def to_int(source: Any) -> int:
    if isinstance(source, int):
        return source
    if isinstance(source, str):
        return int(source, 10)
    return 0


def to_https_url(url: str) -> str:
    if url.startswith('http://'):
        return f'https{url[4:]}'
    return url


_DATETIME_FORMAT = '%Y-%m-%d %H:%M'

def to_timestamp(d: Any) -> int:
    if isinstance(d, int):
        return d
    if '-' in d:
        dt = datetime.strptime(d, _DATETIME_FORMAT).replace(tzinfo=_tz_cst)
        return dt.timestamp()
    else:
        return int(d)
