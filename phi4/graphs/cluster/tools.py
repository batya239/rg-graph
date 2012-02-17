#!/usr/bin/python

import sys
import os
import fnmatch
import re
import math

def get_results(fname):
   res=None
   std_dev=None
   delta=None
   time=None
   ncall_tot=0
   for line in open(fname).readlines():
       regex=re.match("^std_dev = (.*)$",line)
       if regex:
           std_dev=float(regex.groups()[0])

       regex=re.match("^result = (.*)$",line)
       if regex:
           res=float(regex.groups()[0])

       regex=re.match("^delta = (.*)$",line)
       if regex:
           delta=float(regex.groups()[0])

       regex=re.match("^time = (.*)$",line)
       if regex:
           time=float(regex.groups()[0])

       regex=re.match(".*ncall=\s+(\d+)\s.*",line)
       if regex:
           ncall=int(regex.groups()[0])

       regex=re.match(".*itmx=\s+(\d+)\s.*",line)
       if regex:
           nit=int(regex.groups()[0])
           ncall_tot+=ncall*nit
           ncall=0

   return (res,std_dev,delta,time,ncall_tot)

def find_bestresult(name):
    filelist =  os.listdir("%s/"%name)
    reslist = dict()
    for file in filelist:
        regex = re.match("(%s_E.*\.run)\.o.*"%name,file)
        if regex:
           iname = regex.groups()[0]
           result = get_results("%s/%s"%(name,file))
           (res, std_dev, delta, time, ncall) = result
           if res==None or std_dev==None:
               continue
           if math.isnan(res) or math.isnan(std_dev):
               continue
           if iname in reslist.keys():
               if None in reslist[iname][0] and None not in reslist:
                     reslist[iname] = (result, file)
                     continue

               if abs(std_dev) < reslist[iname][0][1]:
                     reslist[iname] = (result, file)
           else:
                     reslist[iname] = (result, file)

    return reslist
    
def collect_result(res_dict):
    keys = res_dict.keys()
    regex=re.compile('^(.*)_E(.*)_O.run.*')
    name=None
    res=[None]*len(keys)
    err=[None]*len(keys)    
    for i in keys:
        reg_=regex.match(i)
        if reg_:
            name=reg_.groups()[0]
            eps=int(reg_.groups()[1])
        else:
            raise ValueError, "invalid key %s"%i
        ((res_, std_dev_, delta_, time, ncall),fname) = res_dict[i]
        res[eps]=res_
        err[eps]=std_dev_
    return  res, err
    

def print_bad(reslist, accuracy):
   for iname  in reslist:
       ((res, std_dev, delta, time, ncall),fname) = reslist[iname]
       if std_dev==None:
           print iname, "bad output!!!"
           continue
       if abs(std_dev)>abs(accuracy):
           ratio=abs(std_dev/accuracy)
           print iname, res, std_dev, delta, time, ncall, " -> ", int(time*ratio**2),"( %10.2f h)"%(time*ratio**2/3600.),  int(ncall*ratio**2),"( %10.2f M)"%(ncall*ratio**2/1000000.),  fname

