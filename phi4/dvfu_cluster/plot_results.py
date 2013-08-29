#!/usr/bin/python
import os, re

def str_to_sec(t):
    time = t.split(':')
    time.reverse()
    sec = 0.
    for n in range(len(time)):
        try:
            sec += float(time[n])*60**n
        except ValueError:
            print "Warning:",time,time[n]
    #print t,"=",sec," secs"
    return sec

method = ['cuhre','vegas','divonne','suave']

list_dir = os.listdir('.')

p = [ [[],[],[]] for m in method ] ## <-- secs,rel_dev, neval
cumul_neval = [ [] for j in method ]
cumul_result = 0.
tmp_rel_dev = 1.

for j,m in enumerate(method):
    print '\n===', m, '==='
    files = [ d for d in list_dir if 'out_'+m in d ]

    for fName in files:
        f = open(fName,'r')
        data = [ i.strip() for i in f.readlines()[-7:] ]
        f.close()

        try: # dirty hack
            neval= [i for i in data[0].split('\t') if 'neval' in i][0].split()[1]
        except IndexError:
            continue
        res  = data[2]
        dev  = data[3]
        time = data[5].split()[2][:-7]
        secs = str_to_sec(time)
        p[j][0] += [secs]
        p[j][1] += [float(dev[9:])/abs(float(res[9:]))]
        p[j][2] += [neval]
        if p[j][1][-1] < tmp_rel_dev:
            cumul_result = res

        print '\t'.join((neval, time, res.split('=')[1].strip(), dev.split('=')[1].strip(),str(secs)))

import matplotlib.pyplot as plt
print p 
print 
markers = ['bs','go','rs','y^']

for j,m in enumerate(p):
    print m[0],m[1],markers[j]
    plt.semilogy(m[0],m[1],markers[j])
    max_time_idx = m[0].index(max(m[0]))
    plt.text(m[0][max_time_idx],m[1][max_time_idx],m[2][max_time_idx])
title = os.getcwd().split('/')[-1]
plt.title(title) # Title

x1,x2,y1,y2 = plt.axis()

plt.text((x2-x1)/4,0.5*y2,str(cumul_result)) ## Result


plt.legend(method)
plt.xlabel('Time, secs --->')
plt.ylabel('std_dev --->')
plt.savefig(title+'.pdf')
