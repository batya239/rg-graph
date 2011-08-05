#!/usr/bin/python
# -*- coding:utf8 -*-
import sympy

def _str2dict(string):
    """ converts string representation of momenta to dict by moment atoms.
        Assumed that atmos has coefficients +/- 1
    """
    if len(string) == 0 or string=='0':
        return dict()
    else:
        t_string=string.replace("+",",+").replace("-",",-")
        if t_string[0] == ",":
            t_string = t_string[1:]
        t_dict={}
        for atom in t_string.split(","):
            if "-" in atom:
                t_dict[atom.replace("-","")]=-1
            else:
                t_dict[atom.replace("+","")]=1
        return t_dict

def _dict2sympy(dict):
    """ converts dict (from str2dict) to sympy expression
    """ 
    res=0
    for atom in dict:
        s_atom = sympy.var(atom)
        res = res + s_atom*dict[atom]
    return res

class Momenta:
    def __init__(self,**kwargs):
        if 'string' in kwargs:
            self._string = kwargs['string'].replace(" ","")
            self._dict = _str2dict(self._string)
            self._sympy = _dict2sympy(self._dict)
        elif 'dict' in kwargs:
            self._dict = kwargs['dict']
            self._sympy = _dict2sympy(self._dict)
            self._string = str(self._sympy).replace(" ","")
        elif 'sympy' in kwargs:
            self._sympy = kwargs['sympy']
            self._string = str(self._sympy).replace(" ","")
            self._dict = _str2dict(self._string)
        else:
            raise TypeError,  'unknown datatype in kwargs: %s'%kwargs

    def __neg__(self):
        t_dict={}
        for atom in self._dict:
            t_dict[atom] = - self._dict[atom]
        return Momenta(dict=t_dict)

    def __add__(self, other):
        return Momenta(sympy=(self._sympy+other._sympy))

    def __sub__(self, other):
        return Momenta(sympy=(self._sympy-other._sympy))

    def __str__(self):
        return self._string

    def __abs__(self):
        return sympy.sqrt(self.Squared())

    def __mul__(self, other):
        if not isinstance(other, Momenta):
            raise TypeError, "cant multiply momenta on %s"%s
        else:
            res = 0
            for atom1 in self._dict.keys():
                s_atom1=sympy.var(atom1)
                for atom2 in other._dict.keys():
                    s_atom2 = sympy.var(atom2)
                    if atom1 == atom2 :
                        res = res + self._dict[atom1]*other._dict[atom2]*s_atom1*s_atom2
                    elif atom1 > atom2 :
                        s_atom12 = sympy.var(atom2+"O"+atom1)
                        res = res + self._dict[atom1]*other._dict[atom2]*s_atom12*s_atom1*s_atom2
                    else:
                        s_atom12 = sympy.var(atom1+"O"+atom2)
                        res = res + self._dict[atom1]*other._dict[atom2]*s_atom12*s_atom1*s_atom2
#NOTE: q1Oq2 - нормированное скалярное произведение (q1xq2/q1/q2)
            return res

    def Squared(self):
        return self*self

    def setZerosByAtoms(self,atomsset):
        smoment=self._sympy
        for atom in atomsset:
            smoment=smoment.subs(atom,0)
        return Momenta(sympy=smoment)

    def __eq__(self,other):
        return self._sympy==other._sympy

    def __ne__(self,other):
        return not (self==other)
#     def SetZeros(self,zero_momenta):
#         pass
# 
#     def Clone(self):
#         pass
# 


def Generate(graph, model):
        if 'GenerateMoments' not in model.__dict__:
#TODO: change generic Exception 
            raise Exception, 'model does not have GenerateMoments method'
        else:
            if not isinstance(graph.__dict__['_subgraphs'],list):
                raise Exception, 'graph dots not have _subgraphs field'
            else:
                graph._moments=model.GenerateMoment(graph)

def Generic(graph, model):
    minMomentIndex = 10**13
    minkMoment = None
    int_lines = [x for x in graph.xInternalLines()]
    for i in comb.xUniqueCombinations(int_lines, G.NLoops()):
        curkMoment = Kirghoff(graph,i)
        curkMoment = ZeroExtMoments(curkMoment)
        curIndex = GetMomentaIndex(graph,curkMoment)
        if curIndex<minMomentIndex:
            minMomentIndex = curIndex
            minkMoment = curkMoment

    return minkMoment

def GetMomentaIndex(graph,moments):
    pass

def ZeroExtMoments(moments):
    """ обнуление внешних импульсо для  вершинных диаграмм
    """
    res=dict()
    extMomentNumber=len(graph.Lines())-len([x for x in graph.xInternalLines()])
    if extMomentNumber >2:
        zeroatomset=set([sympy.var('p%s'%x) for x in range(extMomentNumber-1)])
        for line in moments.keys():
            res[line]=moments[line].setZerosByAtoms(zeroatomset)
        return res
    else:
        return moments
        

def SolveNodeKirghoff(node,moments):
    count=0
    moment=Momenta(dict={})
    for line in node.Lines():
        if line in moments:
            count+=1
            if line.Nodes()[0]==node:
                moment=moment - moments[line]
            else:
                moment=moment + moments[line]
        else:
            _line=line
    if count == len(node.Lines())-1:
        if _line.Nodes()[0]==node:
            return (_line, moment)
        else:
            return (_line, -moment)
    else:
        return (None,None)

def Kirghoff(graph,simple_moments):
    flag = True
    moments={}
    intMomentCount=0
    extMomentCount=0
    for line in simple_moments:
        moments[line.idx()]=Momenta(string='q%s'%intMomentCount)
        intMomentCount+=1
    extMomentNumber=len(graph.Lines())-len([x for x in graph.xInternalLines()])
    extMoment=Moment(dict={})
    for node in graph.xInternalNodes():
        for line in node.Lines():
            if not line.isInternal():
                if extMomentCount<extMomentNumber-1:
                        moments[line]=Momenta(string='p%s'%extMomentCount)
                        if line.Nodes()[0] == node:
                            extMoment=extMoment-moments[line]
                        else:
                            extMoment=extMoment+moments[line]
                        extMomentCount+=1
                else:
                    if line.Nodes()[0]==node:
                        moment[line]=extMoment
                    else:
                        moment[line]=-extMoment
                
    while flag:
        flag=False
        for node in graph.xInternalNodes():
            (_line,_moment)=SolveNodeKirghoff(node,moments)
            if not _line == None:
                moments[_line]=_moment
                flag=True
                
    if len(moments.keys()) == len(graph.Lines()):
        return moments
    else:
        return None
            
            