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
   threads=None
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

       regex=re.match(".*\s+(\d+)\s(thread|CPU)\(s\).*",line)
       if regex:
           threads=int(regex.groups()[0])


       regex=re.match(".*ncall=\s+(\d+)\s.*",line)
       if regex:
           ncall=int(regex.groups()[0])

       regex=re.match(".*itmx=\s+(\d+)\s.*",line)
       if regex:
           nit=int(regex.groups()[0])
           ncall_tot+=ncall*nit
           ncall=0

   return (res,std_dev,delta,time,ncall_tot, threads)

def find_bestresult(name):
    filelist =  os.listdir("%s/"%name)
    reslist = dict()
    for file in filelist:
        regex = re.match("(%s.*_E.*\.run)\.o.*"%name,file)
#        print file, regex
        if regex:
           iname = regex.groups()[0]
           result = get_results("%s/%s"%(name,file))
           (res, std_dev, delta, time, ncall,  threads) = result
           if res==None or std_dev==None:
               continue
           try:
               if math.isnan(res) or math.isnan(std_dev):
                   continue
           except:
               pass
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
    regex=re.compile('^(.*)_E(.*).run.*')
    name=None
    res=[None]*len(keys)
    err=[None]*len(keys)
    time=[0, ]*len(keys)    
    for i in keys:
        reg_=regex.match(i)
        if reg_:
            name=reg_.groups()[0]
            eps=int(reg_.groups()[1])
        else:
            raise ValueError, "invalid key %s"%i
        ((res_, std_dev_, delta_, time_, ncall_, thread_),fname) = res_dict[i]
        res[eps]=res_
        err[eps]=std_dev_
#        print time_ , thread_ , ncall_
        time[eps]=(time_/thread_/ncall_*10**6, (ncall_/10**5)/10.)
    return  res, err, time
    

def print_bad(reslist, accuracy, normalize, g):
   for iname  in reslist:
       ((res, std_dev, delta, time, ncall, thread),fname) = reslist[iname]
       if std_dev==None:
           print iname, "bad output!!!"
           continue
       res__,err__=normalize(g, (res, std_dev))
       if abs(err__)>abs(accuracy):
           ratio=abs(err__/accuracy)
           print iname, res__, err__, delta, time, ncall, " -> ", int(time*ratio**2),"( %10.2f h)"%(time*ratio**2/3600.),  int(ncall*ratio**2),"( %10.2f M)"%(ncall*ratio**2/1000000.),  fname

