#!/usr/bin/python

import sys
import os
import fnmatch
import re

import cluster.tools



method = sys.argv[1]

for dir in os.listdir('.'):
    if re.match('e.*-', dir):
       res__, err__, time__=cluster.tools.collect_result(cluster.tools.find_bestresult(dir))
       f=open('%s/result'%dir,'w')
       f.write(str(tuple(res__,err__)))
       f.close()
              
