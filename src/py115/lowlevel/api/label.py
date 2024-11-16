__author__ = 'deadblue'

from py115.lowlevel.types.label import (
    LabelColor, LabelInfo, LabelListResult
)
from ._base import (
    JsonApiSpec, JsonResult, VoidApiSpec
)


class LabelListApi(JsonApiSpec[LabelListResult]):
    
    def __init__(self, offset: int = 0, limit: int = 11500) -> None:
        super().__init__('https://webapi.115.com/label/list')
        self.query['limit'] = str(limit)
        if offset > 0:
            self.query['offset'] = str(offset)

    def _parse_json_result(self, json_obj: JsonResult) -> LabelListResult:
        data_obj = json_obj['data']
        return LabelListResult(
            count=data_obj['total'],
            labels=[
                LabelInfo(label_obj)
                for label_obj in data_obj['list']
            ]
        )


class LabelAddApi(JsonApiSpec[LabelInfo]):

    def __init__(self, name: str, color: LabelColor) -> None:
        super().__init__('https://webapi.115.com/label/add_multi')
        self.form['name[]'] = f'{name}\x07{color.value}'

    def _parse_json_result(self, json_obj: JsonResult) -> LabelInfo:
        return LabelInfo(json_obj['data'][0])


class LabelEditApi(VoidApiSpec):

    def __init__(
            self, 
            label_id: str, 
            name: str | None = None, 
            color: LabelColor | None = None
        ) -> None:
        super().__init__('https://webapi.115.com/label/edit')
        self.form['id'] = label_id
        if name is not None:
            self.form['name'] = name
        if color is not None:
            self.form['color'] = color.value


class LabelDeleteApi(VoidApiSpec):
    
    def __init__(self, label_id: str) -> None:
        super().__init__('https://webapi.115.com/label/delete')
        self.form['id'] = label_id
