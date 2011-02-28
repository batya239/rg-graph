#!/usr/bin/python
# -*- coding:utf8

import sympy
import re

def str2dict(string):
    if type(string) <> str:
         raise TypeError, 'Invalid type'
    if len(string) == 0:
        return dict()
    t_string=string.replace(" ","").replace("+",",+").replace("-",",-")
    if t_string[0] == ",":
        t_string = t_string[1:]
    t_list=t_string.split(",")
    t_dict={}
    for idxM in t_list:
        if re.match('^[+-]?[a-zA-Z]+\d*$',idxM): # +qwe23, -wewe334 , asd,
            if "+" in idxM:
                t_dict[idxM.replace("+","")]=1
            elif "-" in idxM:
                t_dict[idxM.replace("-","")]=-1
            else:
                t_dict[idxM]=1
        else:
            raise ValueError, 'invalid string: %s'%string
    return t_dict

def dict2str(dict_):
    str_=""
    for idxM in dict_:
        if re.match('^[a-zA-Z]+\d*$',idxM): 
            if dict_[idxM] == 1 :
                str_ = "%s+%s" %(str_, idxM)
            elif dict_[idxM] == -1 :
                str_ = "%s-%s" %(str_, idxM)
            else:
                raise ValueError, "invalid momenta %s" %dict_
            str_=str_.replace(" ","")
        else:
            raise ValueError, 'invalid dict key %s'%idxM
    return str_


def dict2sympy(dict_):
    str_=dict2str(dict_)
    if len(str_) == 0:
        return 0
    else:
        for idxM in dict_:
            sympy.var(idxM)
        t_sympy = eval(dict2str(dict_))
        return t_sympy


class Momenta:
    """ Class represents moments 
        string= | dict= | sympy= 
    """
    def __init__(self,**kwargs):
        if len(kwargs.keys()) <> 1:
            raise TypeError, 'wrong input data %s'%kwargs
        if "string" in kwargs:
             self.string = kwargs["string"].replace(" ","")
             if type(self.string) <> str:
                 raise TypeError, "Wrong type %s"%kwargs
             if self.string == "0":
                 self.string = ""
             self.dict = str2dict(self.string)
             self.sympy = dict2sympy(self.dict)
        elif "dict" in kwargs:
             self.dict = kwargs["dict"]
             if type(self.dict) <> dict:
                 raise TypeError, "Wrong type %s"%kwargs
	     self.sympy = dict2sympy(self.dict)
             self.string = dict2str(self.dict)
        elif "sympy" in kwargs:
             self.sympy = kwargs["sympy"]
             try:
                 if self.sympy <> 0 and self.sympy.__class__.__metaclass__ <> sympy.core.basic.BasicMeta:
                     raise TypeError, "Wrong type %s %s"%(kwargs,self.sympy.__class__.__metaclass__)
             except AttributeError:
                 raise TypeError, "Wrong type %s"%(kwargs)
             if self.sympy == 0:
                 self.string = ""
             else:
                 self.string = str(self.sympy).replace(" ","")
             self.dict = str2dict(self.string)
        else:
             raise TypeError, "unknown moment datatype kwargs = %s"%kwargs
    def __eq__(self,other):
#check other fields?
        return self.dict == other.dict

    def __neg__(self):
        return Momenta(sympy=-self.sympy) 
    
    def __add__(self, other):
        return Momenta(sympy=self.sympy+other.sympy)
    
    def __sub__(self, other):
        return Momenta(sympy=self.sympy-other.sympy)
    
    def __str__(self):
        return self.string
    
    def __abs__(self):
        return sympy.sqrt(self*self)

    def __mul__(self,other):
        if not isinstance(other,Momenta): 
            raise TypeError, "Cant multiply Momenta on non-Momenta %s" %other
        else:
            res = 0
            for atom1 in self.dict.keys():
                s_atom1=sympy.var(atom1)
                for atom2 in other.dict.keys():
                    s_atom2 = sympy.var(atom2)
                    if atom1 == atom2 :
                        res = res + self.dict[atom1]*other.dict[atom2]*s_atom1*s_atom2
                    elif atom1 > atom2 :
                        s_atom12 = sympy.var(atom2+"x"+atom1)
                        res = res + self.dict[atom1]*other.dict[atom2]*s_atom12
                    else:
                        s_atom12 = sympy.var(atom1+"x"+atom2)
                        res = res + self.dict[atom1]*other.dict[atom2]*s_atom12
        return res

    def SetZeros(self, zero_momenta):
        """ sets some moments to zero. zero_momenta - list of moments
        """
        t_sympy=self.sympy
        z_moment=list() # list of substitutions to set moments zero.
#        print t_sympy
        for idxZM in zero_momenta:
#            print "ZM : %s" %idxZM.string
            if len(idxZM.dict) == 1:
                if idxZM.string[0] == "-":
                    z_moment.append( (-idxZM.sympy, 0) )
                else:
                    z_moment.append( (idxZM.sympy, 0) )
            else:
                atoms_list = list(set(self.dict.keys()) & set(idxZM.dict.keys()))
                if len(atoms_list) > 0 :
                    if len(atoms_list)==1:
                         raise ValueError, "Unexpected zero_moments: moment=%s zero_moments=%s idxZM=%s"%(self,zero_momenta,idxZM)
                    t_left = atoms_list[0]
                    t_list=idxZM.dict.keys()
                    t_list.remove(t_left)
                    t_right=dict()
                    for idxM in t_list:
                        t_right[idxM]=idxZM.dict[idxM]/idxZM.dict[t_left]*(-1)
                    z_moment.append( (Momenta(string=t_left).sympy, Momenta(dict=t_right).sympy) )

# TODO: нужна ли сортировка?
        z_moment.sort()
#        print "SetZeros z_moment: ", z_moment
        if not( isinstance(t_sympy,int) or isinstance(t_sympy,float)):
            for idxZeq in z_moment:
                t_sympy=t_sympy.subs(idxZeq[0],idxZeq[1])

        return Momenta(sympy=t_sympy)
