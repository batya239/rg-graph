from dummy_model import _phi3,_phi4
import moments
from graphs import Graph
from lines import Line

def print_moments(_moments):
    if isinstance(_moments.keys()[0],Line):
        print dict([(x.idx(),_moments[x]._string) for x in _moments])
    else:
        print dict([(x,_moments[x]._string) for x in _moments])

phi4=_phi4('dummy')
#g1=Graph('e123-e45-444-555---')
g1=Graph('e112-e3-333--')
#g1=Graph('e111-e-')
print [x for x in g1.xInternalLines()]
phi4.SetTypes(g1)
g1.FindSubgraphs(phi4)
_moments,_subgraphs=moments.Generic(phi4, g1)

print_moments(_moments)
print [x for x in g1.xInternalLines()]
print _subgraphs
