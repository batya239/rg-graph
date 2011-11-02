#!/usr/bin/python
# -*- coding: utf8
from dummy_model import _phi3,_phi4
import moments
from graphs import Graph
from lines import Line
import roperation
import sympy
import subgraphs
import calculate
import sys
import roperation

def print_moments(_moments):
    if isinstance(_moments.keys()[0],Line):
        print dict([(x.idx(),_moments[x]._string) for x in _moments])
    else:
        print dict([(x,_moments[x]._string) for x in _moments])

phi4=_phi4('dummy')
#g1=Graph('e123-e45-444-555---')
#g1=Graph('e112-e3-334-5-555--')
#g1=Graph('e112-33-444-4e--')
#g1=Graph('e112-e3-333--')
#g1=Graph('e111-e-')
#g1=Graph('e123-e23-e3-e-')
#g1=Graph('ee12-ee3-333--')  #8
#g1=Graph('ee12-223-3-ee-')
#g1=Graph('e122-e22--') #N5
#g1=Graph('ee12-e33-e33--')
#g1=Graph('ee12-e23-33-e-')
#g1=Graph('e112-e3-e33-e-')
#g1=Graph('ee11-22-33-ee-')
######g1=Graph('e112-e2-33-ee-')
#g1=Graph('ee11-23-e33-e-')
# g1=Graph('ee12-e22-e-')
#4loop
#g1=Graph('e122-e33-33--')
#g1=Graph('e112-e3-333--') #арбуз в арбузе


g1=Graph(sys.argv[1])
#phi4.reduce=False
name=str(g1.GenerateNickel())
print name
phi4.SetTypes(g1)
g1.FindSubgraphs(phi4)

#g1=g1.ReduceSubgraphs(phi4)
#g1.FindSubgraphs(phi4)
#print g1
subs_toremove=subgraphs.DetectSauseges(g1._subgraphs)
g1.RemoveSubgaphs(subs_toremove)

subgraphs.RemoveTadpoles(g1)
phi4.checktadpoles=False

print "moment index: ", moments.Generic(phi4, g1, level=10**6)

print_moments(g1._moments())
print "subgraphs: ",g1._subgraphs

roperation.strechMoments(g1, phi4, external_strech=False)
#print_moments(g1._moments())

qi=roperation.feynman_qi_lambda(g1)
print "qi=",qi
if len(sys.argv)==3:
    order=eval(sys.argv[2])
    if not isinstance(order,list):
        raise ValueError, "second argument should be list, arv[2]=%s"%sys.argv[2]
else:
    order=None

print "order=",order

B=roperation.feynman_B(qi,order=order)
print "B=",B
(c,b,v)=roperation.decompose_B(B)
print "c=",c
print "b=", b
print "v=\n", v
det=v.det()
Cdet=((b.transpose()*v.adjugate()*b)[0] -c*det).expand()

det1=roperation.SubsSquaresStrechs(det)
Cdet1=roperation.SubsSquaresStrechs(Cdet)

print "det(v)=", det1
print "det(v)*C = ", Cdet1
#calculate.save(name,g1,phi4)

#calculate.compile(name,phi4)

#(res,err) = calculate.execute(name, phi4, neps=0)
#for i in range(len(res)):
#    print i, (res[i],err[i])
