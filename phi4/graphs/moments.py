#!/usr/bin/python
# -*- coding:utf8 -*-
import sympy
from copy import copy

import comb     

import subgraphs

class TadpoleError(Exception):
    pass

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
        """ atomsset - set of sympy variables
        """
        smoment=self._sympy
        for atom in atomsset:
            smoment=smoment.subs(atom,0)
        return Momenta(sympy=smoment)

    def __eq__(self,other):
        return self._sympy==other._sympy

    def __ne__(self,other):
        return not (self==other)

    def isSimple(self):
        """ check if moment is simple. ex. "p0", "q0", not "p0+q0" 
        """
        if len(self._dict.keys())==1:
            return True
        else:
            return False

    def hasAtoms(self, atomsset):
        """ check if moment has all atomsets atoms in it
            atomsset - set of strings
        """
        res=True
        for atom in atomsset:
            if atom not in self._dict.keys():
                res=False
        return res
        
#     def SetZeros(self,zero_momenta):
#         pass
# 
#     def Clone(self):
#         pass
# 


def Generate(model,graph):
        if 'GenerateMoments' not in model.__dict__:
#TODO: change generic Exception 
            raise Exception, 'model does not have GenerateMoments method'
        else:
            if not isinstance(graph.__dict__['_subgraphs'],list):
                raise Exception, 'graph dots not have _subgraphs field'
            else:
                (graph._moments, _subgraphs)=model.GenerateMoment(graph)
                if _subgraphs <> None:
                    graph._subgraphs=_subgraphs

def Generic(model, graph):
    minMomentIndex = 10**13
    minkMoment = None
    minSubgraphs = None
    newSubgraphs = None
    int_lines = [x for x in graph.xInternalLines()]
    for i in comb.xUniqueCombinations(int_lines, graph.NLoops()):
        curkMoment = Kirghoff(graph,i)
#        print dict([(x.idx(),curkMoment[x]._string) for x in curkMoment]),[(x.idx(),x.isInternal()) for x in i]
        curkMoment = ZeroExtMoments(graph,curkMoment)
        if model.checktadpoles:
            try:
                newSubgraphs = CheckTadpoles(graph, curkMoment)
            except TadpoleError:
                continue
            graphs._subgraps_checktadpole = newSubgraphs
        curIndex = GetMomentaIndex(graph, curkMoment, checktadpoles=model.checktadpoles)
        print curIndex
        if (curIndex<minMomentIndex) and (curkMoment<>None):
            minMomentIndex = curIndex
            minkMoment = curkMoment
            if newSubgraphs <> None:
                minSubgraphs = newSubgraphs

    return minkMoment, minSubgraphs

def CheckTadpoles(graph,moments):
    res =  copy(graph._subgraphs)
    for sub in sorted(graph._subgraphs,key=len,reverse=True):
        if sub not in res:
            continue
        else:
            tadpoles=subgraphs.FindTadpoles(sub,res)
            momentpath=ExtMomentPath(graph,sub,moments)
            to_remove=list()
            for tadsub in tadpoles:
                if reduce(lambda x,y: x&y, [(idxL in sub) for idxL in momentpath]):
                    """ внешний для подграфа sub импульс протекает полностью через  подграф tadsub
                    """
                    to_remove.append(tadsub)
            if len(tadpoles)>0 and len(to_remove)<1:
                raise TadpoleError, "moment doesn't pass through subgraph that produced tadpole"
            for _sub in to_remove:
                res.remove(_sub)
            
    return res


def GetMomentaIndex(graph,moments, checktadpoles=False):
    """ calculates penalties for moment layouts.
         checktadpoles=False for phi3-like models only!!!
        phi4 model -> checktadpoles=True
        checktadpoles=True - generates new (redueced) _subfgraphs field
    """
    penalties={"badKirghoff":10**9, "badSub":10*6, "badIn":10000, "longInPath":100,"longMoment":1}
    result=0
    if moments==None:
        """ if Kirghoff returns None - it can't solve Kirghoff equtaions due to inconsistent initial conditions
        """
        return penalties["badKirghoff"], None

    if "_subgraphs" not in graph.__dict__:
        raise AttributeError, "no _subgraph in graph instance (run subgraphs.FindSubgraphs)"
    else:
        #print checktadpoles
        if not checktadpoles:
            _subgraphs=graph._subgraphs
        else:
            _subgraphs=graph._subgraphs_checktadpole

        for sub in _subgraphs:
            """ each subgraph must have number of simple moments equal to number of its  loops
            """
            nsimple=0
            for lineidx in sub:
                if moments[graph._Line(lineidx)].isSimple():
                    nsimple+=1
            if nsimple <> subgraphs.NLoopSub(sub):
                result+=penalties["badSub"]


            extnodes,extlines=subgraphs.FindExternal(sub)
#            if len(extlines)==2:
            if subgraphs.CountExtLegs(sub)==2:
                """ is external moment for self-energy subgraph simple?

                """
                if not moments[graph._Line(list(extlines)[0])].isSimple():
                    result+=penalties["badIn"]

                """ count length of external moment path for self-energy subgraph 
                """
                extpath=ExtMomentPath(graph, sub, moments)
                if len(extpath)>=2:
                    result+=penalties['longIn']*(len(extpath)-1)
        for moment in moments.values():        
            result+=penalties['longMoment']*(len(moment._dict.keys())-1)

    if checktadpoles==False:
        return result
    else:
        return result

def ExtMomentPath(graph,subgraph,moments):
    """ find subgraphs external moment path
    """
    extnodes,extlines=subgraphs.FindExternal(subgraph)
    extatoms=set()
    for i in extlines:
        extatoms=extatoms| set(moments[graph._Line(i)]._dict.keys()) 
    path=list()
    for lineidx in subgraph:
        if moments[graph._Line(lineidx)].hasAtoms(extatoms):
 #TODO: нужно ли требование наличия всех атомов или хотя бы одного? 
#если импульс разветвляется Momenta.hasAtoms его не найдет.
            path.append(lineidx)
    return path

def ZeroExtMoments(graph,moments):
    """ обнуление внешних импульсо для  вершинных диаграмм
    """
    if moments == None:
        return None
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
        moments[line]=Momenta(string='q%s'%intMomentCount)
        intMomentCount+=1
    #print  " Kirghoff 1" , moments
    extMomentNumber=len(graph.Lines())-len([x for x in graph.xInternalLines()])
    extMoment=Momenta(dict={})
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
                        moments[line]=extMoment
                    else:
                        moments[line]=-extMoment
                
    #print " Kirghoff2 2" , moments
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
            
            