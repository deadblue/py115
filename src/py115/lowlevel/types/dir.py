__author__ = 'deadblue'

from py115.compat import StrEnum


class DirOrder(StrEnum):
    """
    Mode to order files under directory.
    """

    FILE_NAME = 'file_name'
    """Order files by name."""

    FILE_SIZE = 'file_size'
    """Order files by size."""

    FILE_TYPE = 'file_type'
    """Order files by type."""

    CREATED_TIME = 'user_ptime'
    """Order files by created time."""

    MODIFIED_TIME = 'user_utime'
    """Order files by last modified name."""

    OPENED_TIME = 'user_otime'
    """Order files by last opened time."""
