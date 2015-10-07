import os
import re
import subprocess
import sys
from setuptools import setup, find_packages, Extension

setup(
    name='swarm',
    version=0.1,
    description='Simple distributed computing.',
    author='Chris Wright',
    url='https://github.com/cjw85/swarm',
    long_description="""Simple client/server based distributed computing using only python standard library.""",
    packages=find_packages(),
    entry_points={
        'console_scripts':['swarm = swarm.components:main']
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
