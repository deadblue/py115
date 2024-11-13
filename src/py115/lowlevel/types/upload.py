__author__ = 'deadblue'

from dataclasses import dataclass


@dataclass
class UploadInfo:
    user_id: int
    user_key: str


@dataclass
class UploadInitOssResult:
    bucket: str
    object: str
    callback: str
    callback_var: str


@dataclass
class UploadInitDoneResult:
    pickcode: str


@dataclass
class UploadInitSignResult:
    sign_key: str
    sign_range: str


UploadInitResult = UploadInitOssResult | UploadInitDoneResult | UploadInitSignResult


@dataclass
class UploadToken:
    access_key_id: str
    access_key_secret: str
    security_token: str
    expiration: int