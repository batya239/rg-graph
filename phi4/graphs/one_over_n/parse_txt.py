#!/usr/bin/python
# -*- coding: utf8
import re
import sys

__author__ = 'mkompan'

_REGEX = re.compile("^kr1\[(.*)\] = (.*)$")
f = open(sys.argv[2], 'w')
f.write("ms6 = {\n")
for line in open(sys.argv[1]).readlines():
    res = _REGEX.match(line)
    f.write("    '%s': '%s',\n" % res.groups())
f.write("}\n")
