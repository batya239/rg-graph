#!/usr/bin/python

import sympy
import copy
from sympy.core.symbol import Symbol

def parse(symbol):
    """ parse symbol from abc_def_fgh_wew_323 to (abc,('def','fgh','wew','323'))
    abc - name, others - inidices
    """
    s_var=str(symbol)
    t_list=s_var.split("_")
    ind_list=t_list[1:]
    return t_list[0], tuple(ind_list)
    
def restore(parsed):
    """ inverse to parse from (abc,('def','fgh','wew','323')) produces 'abc_def_fgh_wew_323' 
    string (not sympy.Symbol)
    """
    res=parsed[0]
    if parsed[0]=='d':
        t_lst=sorted(parsed[1])
    else:
        t_lst=parsed[1]
        
    for idx in t_lst:
        res="%s_%s"%(res, idx)
    return res

def count_idx(parsed_list):
    """ for parsed monom counts indices and stores it to dict: index->cnt
    """
    idx_dict=dict()
    for (name, idx_tuple) in parsed_list:
        for idx in idx_tuple:
            if idx not in idx_dict:
                idx_dict[idx]=1
            else:
                idx_dict[idx]+=1
    return idx_dict
    
def find_idx(parsed_list, idx):
    """ find monom terms with coresponding idx. returns list of terms position in parsed_list
    """
    res=list()
    for i in range(len(parsed_list)):
        (name, idx_tuple)=parsed_list[i]
#        print idx, i, parsed_list[i]
        if idx in idx_tuple:
            res.append(i)
    return res
    
def substitute_idx(tuple1, tuple2, idx):
    """ len(tuple1)==2; idx in tuple1; idx in tuple2
    replaces idx in tuple2 by second index (not idx) in tuple1
    """
    if len(tuple1)<>2:
        raise ValueError, "d must have 2 indices, %s"%tuple1    
    idx2=tuple1[1-tuple1.index(idx)]
    _list=list(tuple2)
    _list[_list.index(idx)]=idx2
    return tuple(_list)

def contract_monom(s_list):
    """ contracts monom by repeating indices, assuming d means Kroneker symbol
    s_list monom as list of strings
    """
    s_parsed=list()
    for s in s_list:
        s_parsed.append(parse(s))
    res_list=copy.copy(s_list)
#    print s_parsed
    c_idx=count_idx(s_parsed)
#    print c_idx
    for idx in c_idx.keys():
        if c_idx[idx]<>2:
            continue
        else:
            to_contract=find_idx(s_parsed, idx)
#            print idx,to_contract
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
#                print res_list, idx1, idx2,  name1, name2

                res_list[idx2]=restore((name2, tuple2_))
                res_list.remove(res_list[idx1])
                res_list=contract_monom(res_list)
                break
            elif len(to_contract)==2 and (s_parsed[to_contract[0]][0] == s_parsed[to_contract[1]][0]):
                idx1, idx2=to_contract
                name1, tuple1 =s_parsed[idx1]
                name2, tuple2 =s_parsed[idx2]
                res_list[idx2]=name2
                res_list[idx1]=name1
                res_list=contract_monom(res_list)
                break
            elif len(to_contract)==2 and (s_parsed[to_contract[0]][0] <> s_parsed[to_contract[1]][0]):
                idx1, idx2=to_contract
                name1, tuple1 =s_parsed[idx1]
                name2, tuple2 =s_parsed[idx2]
                res_list[idx2]=sympy.var("%sX%s"%tuple(sorted([name1,name2])))
                res_list[idx1]=1
                res_list=contract_monom(res_list)
                break

    return res_list
    
def expand_powers(monom):
    """ expand terms like d_1_2**2 to d_1_2,d_1_2
    """
    res=[]
    for term in monom:
        if isinstance(term,  sympy.Pow):
            term1, power = term.args
            for i in range(power):
                res.append(term1)
        else:
            res.append(term)
#    print res
    return res

def expr_to_monoms(expr):
    """ converts expanded expr to list of monoms (monoms are lists of strings)
    """
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
        
def monoms_to_sympy(monoms):
    """ inverse to expr_to_monoms converts list of monoms to sympy expr
    """
    res=sympy.Number(0)
    for monom in monoms:
        tres=sympy.Number(1)
        for svar in monom:
#            print svar, type(svar)
            if (isinstance(svar,str) and svar[0].isalpha()):
                var=sympy.var(svar)
            elif isinstance(svar,Symbol):
                var=svar
            else:
                var=sympy.Number(svar)
            tres=tres*var

        res=res+tres
    return res
    
def contract(expr):
    """ contracts Kroneker symbols and return sympy expr. assumes that Kroneker hlooks like d_1_2
    """
    monoms=expr_to_monoms(expr)
    res=[]
    for monom in monoms:
        res.append(contract_monom(monom))
    return monoms_to_sympy(res)
