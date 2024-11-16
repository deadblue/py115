# PY115

A Python API SDK of 115 cloud storage service.

**Version 0.1.x is under development.**

## Example

```python
from py115 import Cloud

# Connect to cloud
cloud = Cloud(credential={
    'UID':  'UID-value-in-cookie',
    'CID':  'CID-value-in-cookie',
    'SEID': 'SEID-value-in-cookie',
})

# Get storage service
storage = cloud.storage()
# Get file list under root directory
for file in storage.list_files(dir_id='0'):
    print('File: %r' % file)

# Get offline service
offline = cloud.offline()
# Get task list
for task in offline.list():
    print('Task: %r' % task)
# Add task by download URLs
offline.add_urls(
    'magnet:?xt=urn:btih:000123456789abcdef1151150123456789abcdef',
    'ed2k://|file|ED2k-file|115115115|1234567890abcdef1234567890abcdef|/',
    'https://dl.some-server.com/some/file.ext'
)
```

## License

MIT