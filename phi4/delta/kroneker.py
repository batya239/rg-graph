#!/usr/bin/python

import sympy
import copy

d12, d11, d13=sympy.var('d_1_2 d_1_1 d_1_3')

def parse(symbol):
    s_var=str(symbol)
    t_list=s_var.split("_")
    ind_list=t_list[1:]
    return t_list[0], tuple(ind_list)

def restore(parsed):
    res=parsed[0]
    for idx in parsed[1]:
        res="%s_%s"%(res, idx)
    return res
    

def count_idx(parsed_list):
    idx_dict=dict()
    for (name, idx_tuple) in parsed_list:
        for idx in idx_tuple:
            if idx not in idx_dict:
                idx_dict[idx]=1
            else:
                idx_dict[idx]+=1
    return idx_dict
    
def find_idx(parsed_list, idx):
    res=list()
    for i in range(len(parsed_list)):
        (name, idx_tuple)=parsed_list[i]
        if idx in idx_tuple:
            res.append(i)
    return res
    
def substitute_idx(tuple1, tuple2, idx):
    if len(tuple1)<>2:
        raise ValueError, "d must have 2 indices, %s"%tuple1    
#    print tuple1, tuple2, idx
    idx2=tuple1[1-tuple1.index(idx)]
    _list=list(tuple2)
    _list[_list.index(idx)]=idx2
#    print tuple(_list), idx2
    return tuple(_list)

def contract_monom(s_list):
    s_parsed=list()
    for s in s_list:
        s_parsed.append(parse(s))
    res_list=copy.copy(s_list)
#    print res_list
    
    c_idx=count_idx(s_parsed)
    for idx in c_idx.keys():
#        print idx
        if c_idx[idx]<>2:
            continue
        else:
            to_contract=find_idx(s_parsed, idx)
            if len(to_contract)==1 and s_parsed[to_contract[0]][0]=='d':
                
                res_list[to_contract[0]]='n'
                res_list=contract_monom(res_list)
                break
            elif len(to_contract)==2 and s_parsed[to_contract[0]][0]=='d':
                idx1, idx2=to_contract
                name1, tuple1 =s_parsed[idx1]
                name2, tuple2 =s_parsed[idx2]
                tuple2_=substitute_idx(tuple1, tuple2, idx)
                res_list[idx2]=restore((name2, tuple2_))
#                print res_list
#                print s_parsed[idx1]
                res_list.remove(res_list[idx1])
                res_list=contract_monom(res_list)
                break
    return res_list
            
print contract_monom([d11])
print
print contract_monom([d12, d13])
print
print contract_monom([d12, d12])
    
