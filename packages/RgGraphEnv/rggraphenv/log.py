# !/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

import logging


logging.basicConfig(format="%(asctime)s:%(levelname)s:%(message)s")
logger = logging.getLogger("rg-graph")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


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