#!/usr/bin/python

import sympy
import copy

d12, d11, d13, d23=sympy.var('d_1_2 d_1_1 d_1_3 d_2_3')

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
            elif len(to_contract)==2 and (s_parsed[to_contract[0]][0]=='d' or s_parsed[to_contract[1]][0]=='d'):
                if s_parsed[to_contract[0]][0]=='d':
                    idx1, idx2=to_contract
                else:
                    idx2, idx1=to_contract
                name1, tuple1 =s_parsed[idx1]
                name2, tuple2 =s_parsed[idx2]
                tuple2_=substitute_idx(tuple1, tuple2, idx)
                res_list[idx2]=restore((name2, tuple2_))
                res_list.remove(res_list[idx1])
                res_list=contract_monom(res_list)
                break
    return res_list
            
print contract_monom([d11])
print
print contract_monom([d12, d13])
print
print contract_monom([d12, d12])
    
def expand_powers(monom):
    res=[]
    for term in monom:
        if isinstance(term,  sympy.Pow):
            term1, power = term.args
            for i in range(power):
                res.append(term1)
        else:
            res.append(term)
    return res

def expr_to_monoms(expr):
    eexpr=expr.expand()
    if isinstance(eexpr, sympy.Mul):
        return [map(str, expand_powers(eexpr.args))]
    if isinstance(eexpr, sympy.Pow):
        return [map(str, expand_powers([eexpr]))]        
    elif isinstance(eexpr, sympy.Add):
        res=[]
        for arg in eexpr.args:
            res=res+expr_to_monoms(arg)
        return res
    elif isinstance(eexpr, sympy.Symbol):
        return [[str(eexpr)]]
    else:
        raise TypeError, "unsupportd operation"
        
        
print expr_to_monoms(d11)
print expr_to_monoms(d12*d13+d11*d23)

def monoms_to_sympy(monoms):
    res=sympy.Number(0)
    for monom in monoms:
#        print monom, map(type, monom)
        tres=sympy.Number(1)
        for svar in monom:
#            print svar, type(svar)
            var=sympy.var(svar)
            tres=tres*var

        res=res+tres
    return res
    
def contract(expr):
    monoms=expr_to_monoms(expr)
    res=[]
#    print monoms
    for monom in monoms:
#        print "contract", monom,  map(type, monom)
        res.append(contract_monom(monom))
#        print "contract_mon", res[-1],  map(type, res[-1])
    return monoms_to_sympy(res)
    

print contract(d11)
print
print contract(d11*d23+d13*d12+d12*d12)
print
print contract(d13*d23)
