# PY115

An API client of 115 cloud storage service.

## Example

```python
import py115

agent = py115.Agent()
agent.set_cookie({
    'UID': '',
    'CID': '',
    'SEID': '',
})

for file in agent.file_list(dir_id='0'):
    print('File: %s', file)


```