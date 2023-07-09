__author__ = 'deadblue'

"""
Python SDK for 115 cloud storage service.

Example:

import py115
import py115.types

cloud = py115.connect(py115.types.Credential(
    uid='', cid='', seid=''
))
storage = cloud.storage()

for file in storage.list():
    print(f'File: {file.name}')

"""

VERSION = '0.0.2'

import py115.cloud
import py115.types

def connect(
        credential: py115.types.Credential = None,
        protocol_kwargs: dict=  None
) -> py115.cloud.Cloud:
    """Connect to 115 cloud.

    Args:
        credential (py115.types.Credential): 
            Credential data to identity user.
        protocol_kwargs (dict): 
            Keyword arguments for underlying protocol client.

    Return:
        py115.cloud.Cloud: Cloud instance.
    """
    return py115.cloud.Cloud(
        credential=credential, 
        protocol_kwargs=protocol_kwargs
    )
