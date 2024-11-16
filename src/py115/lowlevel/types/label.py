__author__ = 'deadblue'

from dataclasses import dataclass
from typing import Any, Dict, List

from py115._internal.compat import StrEnum


@dataclass
class LabelColor(StrEnum):
    BLANK  = '#000000'
    RED    = '#FF4B30'
    ORANGE = '#F78C26'
    YELLOW = '#FFC032'
    GREEN  = '#43BA80'
    BLUE   = '#2670FC'
    PURPLE = '#8B69FE'
    GRAY   = '#CCCCCC'


@dataclass(init=False)
class LabelInfo:
    id: str
    name: str
    color: LabelColor

    def __init__(self, label_obj: Dict[str, Any]) -> None:
        self.id = label_obj['id']
        self.name = label_obj['name']
        self.color = LabelColor(label_obj['color'])


@dataclass
class LabelListResult:
    count: int
    labels: List[LabelInfo]