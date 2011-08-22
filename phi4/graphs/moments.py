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

def _dict2str(dict):
    """
    """
    if len(dict)==0:
        return ""
    else:
        string=""
        for atom in dict:
            if dict[atom]>0:
                string+="+%s"%atom
            else:
                string+="-%s"%atom
        if string[0]=="+":
            return string[1:]
        else:
            return string
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
#            self._sympy = _dict2sympy(self._dict)
        elif 'dict' in kwargs:
            self._dict = kwargs['dict']
#            self._sympy = _dict2sympy(self._dict)
#            self._string = str(self._sympy).replace(" ","")
            self._string = _dict2str(self._dict)
        elif 'sympy' in kwargs:
            self._sympy = kwargs['sympy']
            self._string = str(self._sympy).replace(" ","")
            self._dict = _str2dict(self._string)
        else:
            raise TypeError,  'unknown datatype in kwargs: %s'%kwargs

    def sympy(self):
        if not "_sympy" in self.__dict__:
            self._sympy=_dict2sympy(self._dict)
        return self._sympy

    def __neg__(self):
        t_dict={}
        for atom in self._dict:
            t_dict[atom] = - self._dict[atom]
        return Momenta(dict=t_dict)

    def __add__(self, other):
#        return Momenta(sympy=(self._sympy+other._sympy))
        t_dict=copy(self._dict)
        for atom in other._dict:
            if atom in t_dict:
                t_dict[atom]+=other._dict[atom]
            else:
                t_dict[atom]=other._dict[atom]
            if t_dict[atom]==0:
                del t_dict[atom]
        return Momenta(dict=t_dict)


    def __sub__(self, other):
        t_dict=copy(self._dict)
        for atom in other._dict:
            if atom in t_dict:
                t_dict[atom]-=other._dict[atom]
            else:
                t_dict[atom]=-other._dict[atom]
            if t_dict[atom]==0:
                del t_dict[atom]
        return Momenta(dict=t_dict)
#        return Momenta(sympy=(self._sympy-other._sympy))

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
        moment=copy(self._dict)
        for atom in atomsset:
            str_atom=str(atom)
            if str_atom in moment:
                del moment[str_atom]
        return Momenta(dict=moment)

    def __eq__(self,other):
        return self._dict==other._dict

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

    def __repr__(self):
        return self._string

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

def xSimpleMoments(graph):
    """ simple alogritm: puting simple moments to some lines and trying to solve Krchhoff equations
    """
    int_lines = [x for x in graph.xInternalLines()]
    for i in comb.xUniqueCombinations(int_lines, graph.NLoops()):
        yield  Kirghoff(graph,i)


def ChainNodes(chain):
    nodes = set()
    intnodes = set()
    for line in chain:
        for node in line.Nodes():
            if node in nodes:
                intnodes.add(node)
            nodes.add(node)
    return list(intnodes),list(nodes-intnodes)

def SortedChain(chain):
    def _sort(chain):
        minidx=0
        for i in range(1,len(chain)):
            if chain[minidx].idx()>chain[i].idx():
                minidx=i
        return chain[minidx:]+chain[:minidx]

    if len(chain)==1:
        return chain
    elif len(chain)==2:
        if len(set(chain[0].Nodes())&set(chain[1].Nodes()))==2:
            return _sort(chain)
        else:
            return chain
    else:
        if len(set(chain[0].Nodes())&set(chain[-1].Nodes()))==1:
            return _sort(chain)
        else:
            return chain

def LoopsAndPaths(graph):
#TODO: check for equivalent paths due to graph symmetry
    Loops=list()
    Paths=list()
    for line in graph.Lines():
        if line.isInternal():
            Loops.append([line])
        else:
            Paths.append([line])
    flag=True
    intnodes=set(list(graph.xInternalNodes()))
    while flag:
        flag=False
        _Loops=list()
#        print "\nloops",Loops
        for loop in Loops:
            int,ext=ChainNodes(loop)
            if len(ext)==0:
                _Loops.append(loop)
            else:
                for node in ext:
                    for line in node.Lines():
                        if line in loop: continue
                        if not line.isInternal(): continue
                        if set(line.Nodes()) & set(int): continue

                        if node in loop[-1].Nodes():
                            _loop=SortedChain(loop+[line])
                        else:
                            _loop=SortedChain([line]+loop)

                        reversed_loop = _loop[1:] + _loop[:1]
                        reversed_loop.reverse()

                        if _loop not in _Loops and reversed_loop not in _Loops:
                            _Loops.append(_loop)
                            flag=True
#            print "_loops_", _Loops
        Loops=_Loops
        _Paths=list()
        for path in Paths:
            int,ext=ChainNodes(path)
            nodelst=list(set(ext)&intnodes)
            if len(nodelst)==0:
                _Paths.append(path)
            elif len(nodelst)==1:
                for line in nodelst[0].Lines():
                    if (line not in path) and len(set(line.Nodes())&set(int))==0:
                        _path=copy(path)+[line]
                        if _path not in _Paths:
                            _Paths.append(_path)
                            flag=True
        Paths=_Paths
    _Paths=list()
    for p in Paths:
        if p[0].idx()>p[-1].idx():
            p.reverse()
        if not p in _Paths:
            _Paths.append(p)
#    print "LOOPS, path",Loops
    return Loops,_Paths
def SetChainPrimitives(chain,primitives, primitive):
    for line in chain:
        if line in primitives:
            primitives[line].append(primitive)
        else:
            primitives[line]=[primitive]

def SetChainMoments(chain,moments,moment):
#    print "SetChainMoments: chain", chain, moment
 #   print moments

    for line in chain:
        if chain.index(line)==0:
            curMoment=moment
        else:
#            print list(set(line.Nodes())&set(previous.Nodes())),line.Nodes(), previous.Nodes()

            nodes=list(set(line.Nodes())&set(previous.Nodes()))
            node=nodes[0]
            if not ((line.start==node and previous.end==node) or (line.end==node and previous.start==node)):
                curMoment=-curMoment

        if line in moments.keys():
            moments[line]=moments[line]+curMoment
        else:
            moments[line]=curMoment
        previous=line
#    print moments
#    print "-------------------"

def CheckLoopAndPath(loop,path,graph):
    lines=set()
    for l in loop:
       lines=lines|set(l)
#    _lines=set([x.idx() for x in list(lines)])
    if not lines == set(graph.asSubgraph()._lines):
#TODO: change set(graph.asSubgraph()._lines to smth more obvious
        return False
    else:
        for p in path:
            lines=lines|set(p)
#        _lines=set([x.idx() for x in list(lines)])
#    print _lines, set(graph._lines)
        if lines == set(graph._lines):
            return True
        else:
            return False

def xLoopMoments(graph):
    """ найти все циклы по которым могут течь импульсы + пути протечки
         внешних импульсов и раскидать по ним  простые импульсы
    """

#TODO: rewrite using chain primitives
    loops,paths = LoopsAndPaths(graph)
    print "loops:",len(loops),"paths:",len(paths)
    print "loops:",loops
    print "paths:",paths
    graph_as_sub=graph.asSubgraph()
    extnodes,extlines=graph_as_sub.FindExternal()
    
#    _extlines=[_lines_storage.Get(x) for x in extlines]
    pcnt=0
    for p in  comb.xUniqueCombinations(paths, graph_as_sub.CountExtLegs()-1):
        print "path:",pcnt
        if not set(reduce(lambda x,y: set(x)|set(y), p))&set(extlines)==set(extlines):
            """ if all lines included in selected path does not include all external lines - paths combination is invalid
            """
            continue
        lcnt=0
        for l in comb.xUniqueCombinations(loops,graph.NLoops()):
            print "loop:",lcnt, "(%s)"%pcnt
#            print l,p
            moment=dict()
#            primitives=dict()
            cnt=0
#            print CheckLoopAndPath(l,p,graph)
            if not CheckLoopAndPath(l,p,graph):
                lcnt+=1
                yield None
            else:
                for path in p:
                    curMoment=Momenta(string="p%s"%cnt)
#                    SetChainPrimitives(path, primitives,"p%s"%paths.index(path))
                    SetChainMoments(path, moment, curMoment)
                    cnt+=1
                cnt=0
                for loop in l:
                    curMoment=Momenta(string="q%s"%cnt)
#                    SetChainPrimitives(path, primitives,"p%s"%paths.index(path))
                    SetChainMoments(loop, moment, curMoment)
                    cnt+=1
                lcnt+=1
                yield moment
#                if len(moment.keys())==len(graph._lines):
#                    yield moment
#                else:
#                    yield None
        pcnt+=1


def Generic(model, graph):
    minMomentIndex = 10**13
    minkMoment = None
    minSubgraphs = None
    newSubgraphs = None
#    int_lines = [x for x in graph.xInternalLines()]
#    for i in comb.xUniqueCombinations(int_lines, graph.NLoops()):
#        _curkMoment = Kirghoff(graph,i)

#    for _curkMoment in xSimpleMoments(graph):

    print "start generic"
    if model.checktadpoles:
        graph.FindTadpoles()
    for _curkMoment in xLoopMoments(graph):
#        print _curkMoment
        if _curkMoment==None:
            continue
        #print dict([(x.idx(),_curkMoment[x]._string) for x in _curkMoment]),[(x.idx(),x.isInternal()) for x in i]

        curkMoment = ZeroExtMoments(graph,_curkMoment)
        if model.checktadpoles:
            try:
                newSubgraphs = CheckTadpoles(graph, curkMoment)
#                print newSubgraphs
            except TadpoleError:
                continue
            graph._subgraphs_checktadpole = newSubgraphs
        curIndex = GetMomentaIndex(graph, curkMoment, checktadpoles=model.checktadpoles)
#        print curIndex
        if (curIndex<minMomentIndex) and (curkMoment<>None):
            minMomentIndex = curIndex
            minkMoment = curkMoment
            if newSubgraphs <> None:
                minSubgraphs = newSubgraphs
    graph._moments, graph._subgraphs = minkMoment, minSubgraphs
    return minMomentIndex

def CheckTadpoles(graph,moments):
    graph_as_sub=graph.asSubgraph()
    res =  copy(graph._subgraphs)
    res.append(graph_as_sub) #Durty trick
    for sub in [graph_as_sub] + sorted(graph._subgraphs,key=len,reverse=True):
        if sub not in res:
            continue
        else:
            tadpoles=sub.FindTadpoles(res)
#            print "tadpoles:",tadpoles
#            print sub
  #          print dict([(x.idx(),moments[x]._string) for x in moments])
            momentpath=ExtMomentPath(graph,sub,moments)

#            print "momentpath:",momentpath
            if len(tadpoles)>0 and len(momentpath)<1:
                raise TadpoleError, "moment doesn't pass through subgraph that produced tadpole"
            to_remove=list()
            for tadsub in tadpoles:
                if reduce(lambda x,y: x&y, [(idxL in tadsub._lines) for idxL in momentpath]):
                    """ внешний для подграфа sub импульс протекает полностью через  подграф tadsub
                    """
                    to_remove.append(tadsub)
#            print to_remove,res
            if len(tadpoles)>0 and len(to_remove)<1:
                raise TadpoleError, "moment doesn't pass through subgraph that produced tadpole"
            for _sub in to_remove:
                res.remove(_sub)
    res.remove(graph_as_sub)
    return res

def GetMomentaIndex(graph,moments, checktadpoles=False):
    """ calculates penalties for moment layouts.
         checktadpoles=False for phi3-like models only!!!
        phi4 model -> checktadpoles=True
        checktadpoles=True - generates new (redueced) _subfgraphs field
    """
    penalties={"badKirghoff":10**9, "badSub":10**6, "badIn":10000, "longInPath":100,"longMoment":1}
    result=0
    if moments==None:
        """ if Kirghoff returns None - it can't solve Kirghoff equtaions due to inconsistent initial conditions
        """
        return penalties["badKirghoff"]

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
            for line in sub._lines:
                if moments[line].isSimple():
                    nsimple+=1
            if nsimple <> sub.NLoopSub():
                result+=penalties["badSub"]


            extnodes,extlines=sub.FindExternal()
#            if len(extlines)==2:
            if sub.CountExtLegs()==2:
                """ is external moment for self-energy subgraph simple?

                """
                if not moments[list(extlines)[0]].isSimple():
                    result+=penalties["badIn"]

                """ count length of external moment path for self-energy subgraph
                """
                extpath=ExtMomentPath(graph, sub, moments)
                if len(extpath)>=2:
                    result+=penalties['longIn']*(len(extpath)-1)
        for moment in moments.values():
            result+=penalties['longMoment']*(len(moment._dict.keys())-1)

#    print "Index:", result
    return result

def ExtMomentPath(graph,subgraph,moments):
    """ find subgraphs external moment path
    """
    extnodes,extlines=subgraph.FindExternal()
    extatoms=set()
    for line in extlines:
        extatoms=extatoms| set(moments[line]._dict.keys())
    path=list()
    for line in subgraph._lines:
        if moments[line].hasAtoms(extatoms):
 #TODO: нужно ли требование наличия всех атомов или хотя бы одного?
#если импульс разветвляется Momenta.hasAtoms его не найдет.
            path.append(line)
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


