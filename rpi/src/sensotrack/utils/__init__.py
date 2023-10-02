# -*- coding: UTF-8 -*-

"""Sensors mediation layer."""

# --------------------------------------------------------
# Software Name : Sensor Track
#
# 2023 Orange
#
# -------------------------------------------------------
#   Benoit HERARD <benoit.herard(at)orange.com>
# -------------------------------------------------------
import json
import os

def dirname(file):
    """Return directory from a file path.

    :param file: Full path file name
    :type file: str
    :return: fullpath of folder containing the file
    :rtype: str
    """

    file_path = os.path.abspath(file)
    path_list = file_path.split(os.sep)
    return os.sep.join(path_list[0:len(path_list)-1])

def load_conf(filename):
    """Load configuration from json file.

    Load configuration from /etc/sonsotract/ if exists 
    or from embeded config if not.

    :param filename: Filename without path to load
    :type filename: str
    :return: Config
    :rtype: dict
    """

    conf = {}
    full_path = f"{dirname(__file__)}/../conf/sensotrack.json"
    if os.path.exists(f"/etc/sensotrack/{filename}"):
        full_path = f"/etc/sensotrack/{filename}"

    with open(full_path, encoding="utf-8") as data:
        conf = json.load(data)
    return conf
