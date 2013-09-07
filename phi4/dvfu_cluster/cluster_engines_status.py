#!/usr/bin/ipython
# encoding: utf8

## Запускаем ipcontroller на первом узле:
# [kirienko@n1 ]$ ipcontroller --ip=* --profile=test

## Запускаем вычислители на каждом узле:
# [kirienko@n1 ]$ for i in `cat mpd.test`; do ssh $i ipengine --ip=192.168.56.6 --profile=test &  done

from IPython.parallel import Client

def getnode():
    import platform
    return platform.node()

rc = Client(profile='test')
print "rc.ids =", rc.ids

dview = rc[:]
print dview.apply_sync(getnode)
