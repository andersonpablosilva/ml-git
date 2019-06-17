"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import yaml


def yaml_load(file):
    hash = {}
    try:
        with open(file) as yfile:
            hash = yaml.load(yfile, Loader=yaml.SafeLoader)
    except Exception as e:
        print(e)
        pass
    return hash


def yaml_save(hash, file):
    with open(file, 'w') as yfile:
        yaml.dump(hash, yfile, default_flow_style=False)


def ensure_path_exists(path):
    assert (len(path) > 0)

    dirs = path.split(os.sep)

    dut = ""
    if path[0] == "/":
        dut = "/"

    for dir in dirs:
        dut = os.path.join(dut, dir)
        if os.path.exists(dut) == False:
            os.mkdir(dut)


def getListOrElse(options, option, default):
    try:
        if isinstance(options,dict):
            return options[option].split(",")
        ret = options(option)
        if ret in ["", None]: return default
        return ret
    except:
        return default


def getOrElse(options, option, default):
    try:
        if isinstance(options,dict):
            return options[option]
        ret = options(option)
        if ret in ["", None]: return default
        return ret
    except:
        return default