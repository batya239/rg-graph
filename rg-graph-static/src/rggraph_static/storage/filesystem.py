#!/usr/bin/python
# -*- coding:utf8

'''
Created on Mar 2, 2010

@author: mkompan
'''

import os
import time

def NormalizeBaseName(name):
    if name[-1:] !="/":
        res = name +"/"
    else:
        res = name
    if res[0] == "~":
        res = os.environ['HOME']+res[1:]
    return res
    

def SaveGraphAsDict(G, overwrite=False):
    G.GenerateNickel()
    name = "%s/"%(G.nickel)
    pwd = NormalizeBaseName(G.model.basepath)
    dirname = pwd + name
    try:
        os.mkdir(dirname)
    except:
        if overwrite:
            file_list = os.listdir(dirname)
            for file in file_list:
                os.remove(dirname+file)
        else:
            raise Exception, "folder %s already exists" %dirname
    F = open(dirname+"Graph","w")
    F.write(str(G._ToDict()))
    F.close()
    
def LoadGraphAsDict(G, str_nickel=""):
    if len(str_nickel)==0:
        dirname = "./"
    else:
        pwd = NormalizeBaseName(G.model.basepath)
        dirname = pwd + str_nickel
        if dirname[-1:] != "/":
            dirname = dirname + "/"
    dict = eval(open(dirname+"Graph","r").read())
    return dict

def SaveResults(G):
    G.GenerateNickel()
    name = "%s/"%(G.nickel)
    pwd = NormalizeBaseName(G.model.basepath)
    dirname = pwd + name
    for idx in ['r1_dot_gamma','delta_gamma','dot_r1_gamma']:
        if idx in G.__dict__:
            F=open(dirname+idx,"w")
            F.write(str(G.__dict__[idx]))
            F.close()
            F=open(dirname + idx + time.strftime("-%Y-%m-%d-%H:%M:%S"),"w")
            F.write(str(G.__dict__[idx]))
            F.close()
