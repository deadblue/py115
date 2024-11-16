__author__ = 'deadblue'

from datetime import datetime, timezone, timedelta
from email.mime import base


_FORMAT_115 = '%Y-%m-%d %H:%M'
_FORMAT_RFC3399 = '%Y-%m-%dT%H:%M:%SZ'


_TZ_CST = timezone(
    offset=timedelta(hours=8),
    name='Asia/Shanghai'
)


def to_timestamp(d: str | int) -> int:
    if isinstance(d, int):
        return d
    if '-' in d:
        dt = datetime.strptime(d, _FORMAT_115).replace(tzinfo=_TZ_CST)
        return int(dt.timestamp())
    else:
        return int(d, base=10)


def parse_rfc3399(time_str: str) -> int:
    return int(datetime.strptime(
        time_str, _FORMAT_RFC3399
    ).replace(tzinfo=timezone.utc).timestamp())


def now_str() -> str:
    return str(int(datetime.now().timestamp()))


def must_int(value: int | str) -> int:
    if isinstance(value, int):
        return value
    else:
        return int(value, base=10)
