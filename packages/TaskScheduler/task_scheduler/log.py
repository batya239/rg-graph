#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


import logging
import os

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(message)s")
logger = logging.getLogger("task-scheduler")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(os.path.expanduser("~/task_scheduler.log"))
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(message)s"))
logger.addHandler(handler)


def set_format(a_format):
    logging.basicConfig(format=a_format)


def set_level(level):
    logger.setLevel(level)


def add_handler(handler):
    logger.addHandler(handler)


def is_debug_enabled():
    return logger.isEnabledFor(logging.DEBUG)


def warn(msg, *params):
    logger.warn(msg)


def debug(msg, *params):
    logger.debug(msg)


def info(msg, *params):
    logger.info(msg)


def error(msg, *params):
    logger.error(msg)