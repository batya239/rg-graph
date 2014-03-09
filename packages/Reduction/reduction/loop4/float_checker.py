__author__ = 'dima'

import os

for filename in os.listdir("./"):
    for s in open(filename):
        if "." in s:
            print filename

