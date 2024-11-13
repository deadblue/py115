__author__ = 'deadblue'

from dataclasses import dataclass

@dataclass
class UserInfo:
    user_id: int
    name: str
    is_vip: bool
