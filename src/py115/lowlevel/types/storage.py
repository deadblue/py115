__author__ = 'deadblue'

from dataclasses import dataclass

@dataclass
class StorageInfo:

    total_size: int
    """Storage total size in bytes."""

    remain_size: int
    """Storage remain size in bytes."""

    used_size: int
    """Storage used size in bytes."""
