#!/usr/bin/ipython
# encoding: utf8

## Запускаем ipcontroller на первом узле:
# [kirienko@n1 ]$ ipcontroller --ip=* --profile=test

## Запускаем вычислители на каждом узле:
# [kirienko@n1 ]$ for i in `cat mpd.test`; do ssh $i ipengine --ip=192.168.56.6 --profile=test &  done

from IPython.parallel import Client
from sys import argv, exit

def getnode():
    import platform
    return platform.node()

try:
    p = argv[1]
except IndexError:
    print "profile does not set, use 'ssh'"
    p = 'ssh'

try:
    rc = Client(profile=p)
except IOError:
    print "error: it seems ipCluster is not active"
    exit()
print "rc.ids =", rc.ids

dview = rc[:]
print sorted(dview.apply_sync(getnode))
