"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import logging
from mlgit.config import get_key, config_verbose

MLGitLogger = None


def __level_from_string(level):
    if level == "debug":
        lvl = logging.DEBUG
    elif level == "info":
        lvl = logging.INFO
    elif level == "warning":
        lvl = logging.WARNING
    elif level == "error":
        lvl = logging.ERROR
    elif level == "critical":
        lvl = logging.CRITICAL
    else:
        lvl = logging.DEBUG
    return lvl


def init_logger():
    global MLGitLogger
    MLGitLogger = logging.getLogger("ml-git")
    MLGitLogger.setLevel(__level_from_string(get_key("log_level")))

    if config_verbose() is not None:
        handler = logging.StreamHandler()
        lvl = logging.WARNING
        if config_verbose() == "vv":
            lvl = logging.INFO
        elif config_verbose() == "vvv":
            lvl = logging.DEBUG
        handler.setLevel(lvl)
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        MLGitLogger.addHandler(handler)


def __log(level, log_message):
    global MLGitLogger
    try:
        log = MLGitLogger
        if level == 'debug':
            log.debug(log_message)
        elif level == 'info':
            log.info(log_message)
        elif level == 'error':
            log.error(log_message)
        elif level == 'warn':
            log.warn(log_message)
        elif level == 'fatal':
            log.fatal(log_message)
    except:
        print("ml-git: " + log_message)


def debug(msg):
    __log('debug', msg)


def info(msg):
    __log('info', msg)


def warn(msg):
    __log('warn', msg)


def error(msg):
    __log('error', msg)


def fatal(msg):
    __log('fatal', msg)