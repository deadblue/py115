__author__ = 'deadblue'

import datetime

import pytz

_tz_cst = pytz.FixedOffset(480)

def parse_datetime_str(s: str) -> datetime.datetime:
    if '-' in s:
        t = datetime.datetime.strptime(
            s, '%Y-%m-%d %H:%M'
        )
        t.replace(tzinfo=_tz_cst)
        return t
    else:
        return  datetime.datetime.fromtimestamp(
            float(s), tz=_tz_cst
        )

def make_datetime(ts: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(
        float(ts), tz=_tz_cst
    )
