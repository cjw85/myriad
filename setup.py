import os
import re
import subprocess
import sys
from setuptools import setup, find_packages, Extension

version='0.1.3'

setup(
    name='myriad',
    version=version,
    description='Simple distributed computing.',
    author='Chris Wright',
    author_email='chris_wright1@outlook.com',
    url='https://github.com/cjw85/myriad',
    download_url='https://github.com/cjw85/myriad/tarball/{}'.format(version),
    long_description="""Simple client/server based distributed computing using only python standard library.""",
    packages=find_packages(),
    entry_points={
        'console_scripts':['myriad = myriad.components:main']
    },
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Distributed Computing'
    ]
)
