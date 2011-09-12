
from dummy_model import _phi3,_phi4
import moments
from graphs import Graph
from lines import Line
import roperation

def print_moments(_moments):
    if isinstance(_moments.keys()[0],Line):
        print dict([(x.idx(),_moments[x]._string) for x in _moments])
    else:
        print dict([(x,_moments[x]._string) for x in _moments])

phi4=_phi4('dummy')
#g1=Graph('e123-e45-444-555---')
#g1=Graph('e112-33-444-4e--')
#g1=Graph('e112-e3-333--')
g1=Graph('e111-e-')
print [x for x in g1.xInternalLines()]
phi4.SetTypes(g1)
g1.FindSubgraphs(phi4)
print "index:",moments.Generic(phi4, g1)

print_moments(g1._moments())
print [x for x in g1.xInternalLines()]
print g1._subgraphs_m
for g in phi4.dTau(g1):
    print "---------"
    roperation.strechMoments(g, phi4)

    print g.expr(phi4)
    print roperation.det(g,phi4)
    print roperation.subs_vars(g)

    print "======\n\n\n"
    expr=roperation.expr(g,phi4)
    print roperation.AvgByExtDir(expr)

print roperation.export_subs_vars(roperation.subs_vars(g)[1])
