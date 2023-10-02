#!/usr/bin/python3
# --------------------------------------------------------
# Software Name : Risk Scoring
#
# Copyright © 2020 Orange
#
# -------------------------------------------------------
# Authors     : Benoit HERARD <benoit.herard(at)orange.com>
#               Gaël LE LAN <gael.lelan(at)orange.com>
# -------------------------------------------------------


"""Setup for sensotrack."""
import os
from setuptools import setup, find_packages

import sensotrack

__author__ = sensotrack.__author__
__email__ = sensotrack.__email__
__version__ = sensotrack.__version__


setup(
    name='sensotrack',
    version=__version__,
    url='https://github.com/bherard/sensors-track',
    author=__author__,
    author_email=__email__,
    description='Sensors ingration platform',
    packages=find_packages(
        exclude=["*tests*"]
    ),
    long_description=open(
        'README.md'
    ).read(),
    zip_safe=False,
    install_requires=[
        open(
            'requirements.txt'
        ).read().split("\n")
    ],
    include_package_data=True,
    scripts=['bin/{}'.format(x) for x in os.listdir('bin') if x != '__pycache__']

)
