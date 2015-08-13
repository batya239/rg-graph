#! /usr/bin/python
#! encoding: utf8

__author__ = "kirienko"

with open('diags_5_loops/count') as fd:
    data = fd.readlines()

data = [d.split("\t") for d in data]

print "topologies:\t",len(data)
print "All diags:\t",sum([int(d[1]) for d in data])
print "spine:\t\t",sum([int(d[2]) for d in data])
print "to calculate:\t",sum([int(d[3]) for d in data])

