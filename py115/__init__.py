__author__ = 'deadblue'

"""
Python library for 115 cloud storage service.

Example:

import py115
from py115.types import Credential

cloud = py115.create(Credential(
    uid='', cid='', seid=''
))
storage = cloud.storage()

for file in storage.list():
    print(f'File: ${file.name}')

"""

VERSION = '0.0.1'

from .cloud import Cloud
from .types import Credential

def connect(
        credential: Credential = None,
        protocol_kwargs: dict=  None
) -> Cloud:
    """Connect to cloud storage service.

    Args:
        credential (py115.types.Credential): Credential data to identity user.
        protocol_kwargs (dict): Keyword arguments for underlying protocol client.

    Return:
        py115.cloud.Cloud: Cloud instance.
    """
    return Cloud(
        credential=credential, 
        protocol_kwargs=protocol_kwargs
    )
