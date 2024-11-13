__author__ = 'deadblue'

from datetime import datetime, timezone, timedelta


_DATETIME_FORMAT = '%Y-%m-%d %H:%M'

_TZ_CST = timezone(
    offset=timedelta(hours=8),
    name='Asia/Shanghai'
)

def to_timestamp(d: str | int) -> int:
    if isinstance(d, int):
        return d
    if '-' in d:
        dt = datetime.strptime(d, _DATETIME_FORMAT).replace(tzinfo=_TZ_CST)
        return int(dt.timestamp())
    else:
        return int(d, base=10)


def now_str() -> str:
    return int(datetime.now().timestamp())


def must_int(value: int | str) -> int:
    if isinstance(value, int):
        return value
    else:
        return int(value, base=10)
