#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

from IPython.parallel import Client
from rggraphenv import log
import cuba_integration

try:
    c = Client()
    dview = c[:]
    imap = dview.map_sync
    log.debug("IPython concurrency enabled")
except BaseException as e:
    print e
    imap = map
    log.debug("no enabled concurrency")


def kr11(kr_operation, graph_state_as_str):
    answer = zeroDict()

    for local_answer in imap(lambda integrand: cuba_integration.cuba_integrate(*integrand), kr_operation(graph_state_as_str)):
        for d, a in local_answer.items():
            answer[d] += a

    return answer
