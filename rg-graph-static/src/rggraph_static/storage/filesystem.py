#!/usr/bin/python
# -*- coding:utf8

'''
Created on Mar 2, 2010

@author: mkompan
'''

import os
import time
import sympy
import re as regex
import pickle 

def NormalizeBaseName(name):
    if name[-1:] !="/":
        res = name +"/"
    else:
        res = name
    if res[0] == "~":
        res = os.environ['HOME']+res[1:]
    return res

def GetGraphList(model):
    pwd =  NormalizeBaseName(model.basepath)
    filelist=os.listdir(pwd)
    res=[]
    for file in filelist:
        if regex.match('^e.*',file):
            res.append(file)
    return res
               

def SaveGraphAsPickle(G, overwrite=False):
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

    F = open(dirname+"Graph.obj","w")
    pickle.dump(G,F)
    F.close()

def LoadGraphFromPickle(model,str_nickel=""):
    if len(str_nickel)==0:
        dirname = "./"
    else:
        pwd = NormalizeBaseName(model.basepath)
        dirname = pwd + str_nickel
        if dirname[-1:] != "/":
            dirname = dirname + "/"
    F=open(dirname+"Graph.obj","r")
    res = pickle.load(F)
    F.close()
#TODO: check that model of graph equal to model provided in args
#?    res.model = model    
    return res


def SaveGraphAsDict(G, overwrite=False):
#TODO: remove
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
#        else:
#            raise Exception, "folder %s already exists" %dirname
    F = open(dirname+"Graph","w")
    F.write(str(G._ToDict()))
    F.close()
    
def LoadGraphAsDict(G,str_nickel=""):
#TODO: remove
    if len(str_nickel)==0:
        dirname = "./"
    else:
        pwd = NormalizeBaseName(G.model.basepath)
        dirname = pwd + str_nickel
        if dirname[-1:] != "/":
            dirname = dirname + "/"
    dict = eval(open(dirname+"Graph","r").read())
    return dict

def SaveResults(G,res_list=[]):
    
    G.GenerateNickel()
    name = "%s/"%(G.nickel)
    pwd = NormalizeBaseName(G.model.basepath)
    dirname = pwd + name
    time_str=time.strftime("-%Y-%m-%d-%H:%M:%S")
    if len(res_list)==0:
        lst = ['r1_dot_gamma','delta_gamma','r1_gamma', 'r1_dot_gamma_err', 'npoints', 'method', "delta", "reduced_nloops"]
    else:
        lst = res_list

    for idx in lst:
        
        if idx in G.__dict__:
            F=open(dirname+idx,"w")
            F.write(str(G.__dict__[idx]))
            F.close()
            F=open(dirname + idx + time_str,"w")
            F.write(str(G.__dict__[idx]))
            F.close()

def LoadResults(G,strvars):
    sympy.var(strvars)
    G.GenerateNickel()
    name = "%s/"%(G.nickel)
    pwd = NormalizeBaseName(G.model.basepath)
    dirname = pwd + name
    for idx in ['r1_dot_gamma','delta_gamma','r1_gamma','r1_dot_gamma_err','npoints', 'method', 'delta', 'reduced_nloops','time']:
        file_name = idx
        if idx == 'npoints': 
            var_name = "%s_r"%idx
        else:
            var_name = idx
        try:
            if var_name == "method":
                G.__dict__[var_name] = open(dirname+file_name,"r").read()
            else:
                G.__dict__[var_name] = eval(open(dirname+file_name,"r").read())
        except IOError:
            G.__dict__[idx] = None
            
def ChangeToWorkDir(G):
    G.GenerateNickel()
    os.chdir("%s/%s/"%(NormalizeBaseName(G.model.basepath), G.nickel))     