__author__ = 'deadblue'

from setuptools import setup

setup(
    name='py115',
    version='0.0.1',
    description='API client of 115 cloud storage',
    author='deadblue',
    author_email='deadblue@newbie.town',
    packages=[ 'py115' ],
    requires=[
        'cryptography',
        'lz4',
        'pycryptodome',
        'pytz',
        'requests'
    ]
)
