Examples
========

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

Retrieve Files
--------------

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
            '-H', f'{name}={value}'
        ])
    subprocess.call(args)


Upload File
-----------

.. code:: python

    # Upload file to root directory
    ticket = storage.request_upload(
        dir_id='0', 
        file_path='/path/to/local-file'
    )
    if ticket.is_done:
        print('File fast-uploaded!')
    else:
        import oss2
        

Retrieve Tasks
--------------

.. code:: python
    
    # List files under root directory
    for task in offline.list():
        print(f'Task: ID={task.task_id}, Name={task.name}')

Add Task
--------

.. code:: python

    # Add offline task from download URL
    # Support HTTP/HTTPS/FTP/magnet/ed2k links
    offline.add_url(
        'ed2k://ED2k-file-link',
        'magnet:?xt=urn:btih:magnet-file-link'
    )
