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
    author_email='',
    url='',
    long_description="""Simple client/server based distributed computing using only python standard library.""",
    packages=find_packages(),
    entry_points={
        'console_scripts':['swarm = swarm.components:main']
    },
    install_requires=[
    ],
)
