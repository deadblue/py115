# PY115

An API client of 115 cloud storage service.

## Example

```python
from py115 import Cloud, types

cloud = Cloud()
cred = types.Credential(
    uid='', cid='', seid=''
)
credential.set_credential(credential)

storage = cloud.storage()

for file in storage.list(dir_id='0'):
    print('File: %s', file)

```