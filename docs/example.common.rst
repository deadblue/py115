=================
Common Operations
=================


Connect to Cloud
----------------

.. code:: python

    import py115
    import py115.types

    cloud = py115.connect(
        credential=py115.types.Credential(
            uid='', cid='', seid=''
        )
    )
    # Get storage service
    storage = cloud.storage()
    # Get offline service
    offline = cloud.offline()


List Files
----------

.. code:: python
    
    # List files under root directory
    for file in storage.list(dir_id='0'):
        print(f'File: ID={file.file_id}, Name={file.name}')


Download File
-------------

.. code:: python

    import subprocess

    # Request download ticket
    ticket = storage.request_download(pickcode='pickcode-of-file')
    # Download via curl command
    args = [
        'curl', ticket.url,
        '-o', ticket.file_name,
    ]
    for name, value in ticket.headers.items():
        args.extend([
            '-H', f'{name}: {value}'
        ])
    subprocess.call(args)


Upload File
-----------

.. code:: python

    # File to upload
    file_path = '/path/to/local-file'

    # Request upload ticket
    ticket = storage.request_upload(
        dir_id='0',
        file_path=file_path
    )
    if ticket is None:
        print('Request upload failed!')
    elif ticket.is_done:
        print('File has been imported to your cloud!')
    else:
        # Upload via "aliyun-oss-python-sdk"
        import oss2
        # Create OSS auth
        auth = oss2.StsAuth(**ticket.oss_token)
        # Get bucket object
        bucket = oss2.Bucket(
            auth=auth,
            endpoint=ticket.oss_endpoint,
            bucket_name=ticket.bucket_name,
        )
        # Upload file, that may take a looooong time
        por = bucket.put_object_from_file(
            key=ticket.object_key,
            filename=file_path,
            headers=ticket.headers, # DO NOT forget this!!!
        )
        # Parse result
        result = por.resp.response.json()
        print(f'Upload result: {result!r}')


List Tasks
----------

.. code:: python
    
    # List all offline tasks
    for task in offline.list():
        print(f'Task: ID={task.task_id}, Name={task.name}')


Add Task
--------

.. code:: python

    # Add offline task from download URL
    # Support HTTP/HTTPS/FTP/magnet/ed2k link
    offline.add_url(
        'ed2k://ed2k-file-link',
        'magnet:?xt=urn:btih:magnet-file-link'
    )
