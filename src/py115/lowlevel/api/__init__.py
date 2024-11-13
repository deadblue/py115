__author__ = 'deadblue'

from .app import (
    AppVersionApi
)
from .dir import (
    DirMakeApi, 
    DirSetOrderApi
)
from .download import DownloadApi
from .file import (
    FileListApi,
    FileSearchApi,
    FileStaredApi,
    FileLabeledApi,
    FileGetInfoApi,
    FileDeleteApi,
    FileMoveApi,
    FileBatchRenameApi,
    FileSetStarApi,
    FileSetLabelsApi,
    FileBatchAddLabelsApi,
    FileBatchRemoveLabelsApi,
    FileBatchSetLabelsApi,
    FileSetDescriptionApi,
    FileGetDescriptionApi,
    FileHideApi,
    FileSetTopApi,
    FileShowHiddenApi,
)
from .label import (
    LabelListApi, 
    LabelAddApi, 
    LabelEditApi, 
    LabelDeleteApi
)
from .offline import (
    OfflineListApi,
    OfflineDeleteApi,
    OfflineClearApi,
    OfflineAddUrlsApi
)
from .qrcode import (
    QrcodeTokenApi, 
    QrcodeStatusApi,
    QrcodeLoginApi,
    get_qrcode_image_url
)
from .storage import StorageInfoApi
from .user import UserInfoApi

__all__ = [
    AppVersionApi,

    DirMakeApi,
    DirSetOrderApi,

    DownloadApi,

    FileListApi,
    FileSearchApi,
    FileStaredApi,
    FileLabeledApi,
    FileGetInfoApi,
    FileDeleteApi,
    FileMoveApi,
    FileBatchRenameApi,
    FileSetStarApi,
    FileSetLabelsApi,
    FileBatchAddLabelsApi,
    FileBatchRemoveLabelsApi,
    FileBatchSetLabelsApi,
    FileSetDescriptionApi,
    FileGetDescriptionApi,
    FileHideApi,
    FileSetTopApi,
    FileShowHiddenApi,

    LabelListApi, 
    LabelAddApi, 
    LabelEditApi, 
    LabelDeleteApi,

    OfflineListApi,
    OfflineDeleteApi,
    OfflineClearApi,
    OfflineAddUrlsApi,

    QrcodeTokenApi,
    QrcodeStatusApi,
    QrcodeLoginApi,
    get_qrcode_image_url,

    StorageInfoApi,

    UserInfoApi,
]
