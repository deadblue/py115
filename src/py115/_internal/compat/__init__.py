__author__ = 'deadblue'

try:
    from enum import StrEnum
except ImportError:
    # Before Python 3.11
    from enum import Enum
    class StrEnum(str, Enum): pass


__all__ = [
    'StrEnum'
]
