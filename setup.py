#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2017
Fraunhofer Institute for Manufacturing Engineering
and Automation (IPA)
Author: Daniel Stock
mailto: daniel DOT stock AT ipa DOT fraunhofer DOT com
See the file "LICENSE" for the full license governing this code.
"""

import os
import re
from setuptools import setup


def get_version(*file_paths):
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version("msb_client", "__init__.py")

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="msb-client-websocket-python",
    version=version,
    description="The Python client library to connect to the Websocket Interface of the VFK MSB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Daniel Stock",
    author_email="daniel.stock@ipa.fraunhofer.de",
    url="https://research.virtualfortknox.de/",
    project_urls={
        "Source Code": "https://github.com/research-virtualfortknox/msb-client-websocket-python.git",
        "Bug Tracker": "https://github.com/research-virtualfortknox/msb-client-websocket-python/issues",
    },
    packages=["msb_client"],
    package_data={
        "msb_client": ["*.json"]
    },
    include_package_data=True,
    install_requires=[
        "websocket-client==0.57.0",
        "jsonschema>=4.4.0",
        "enum34>=1.1.10",
    ],
    zip_safe=False,
    license='Apache-2.0',
)
