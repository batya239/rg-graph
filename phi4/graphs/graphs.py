#!/usr/bin/python
# -*- coding:utf8

import copy

import nickel

def _find_empty_idx(keys_):
   idx=0
   while idx in keys_:
       idx+=1
   return idx


class Graph:
    def __init__(self,arg):
        self._lines = dict()
        self._nodes = dict()
        if isinstance(arg,str):
# construct graph from nickel index
            self._from_lines_list(nickel.Nickel(string=arg).edges)
        elif isinstance(arg,list):
# construct graph from edges 
            self._from_lines_list(arg)
        else:
            raise TypeError, "Unsupproted type of argument: %s"%arg

    def _from_lines_list(self,list_):
        list__=copy.copy(list_)
        list__.sort()
        for line in list__:
            self._add_line(line)

    def _add_line(self,line):
        if isinstance(line,list):
            if len(line) == 2:
                idx = _find_empty_idx(self._lines.keys())

                self._lines[idx] = line
                for node in line:
                    if node in self._nodes.keys():
                       self._nodes[node].append(idx)
                    else:
                       self._nodes[node] = [idx,]
            else:
                raise ValueError, "Invalid line %s"%line
        else:
            raise TypeError, "Invalid type of argument: %s"%line
                
    def edges(self):
        res=[]
        for idx in self._lines:
            res.append(self._lines[idx])
        res.sort()
        return res
                        

    def _remove_line(self,line):
        pass
