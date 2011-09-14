
from dummy_model import _phi3,_phi4
import moments
from graphs import Graph
from lines import Line
import roperation
import sympy
import subgraphs

def print_moments(_moments):
    if isinstance(_moments.keys()[0],Line):
        print dict([(x.idx(),_moments[x]._string) for x in _moments])
    else:
        print dict([(x,_moments[x]._string) for x in _moments])

phi4=_phi4('dummy')
#g1=Graph('e123-e45-444-555---')
#g1=Graph('e112-33-444-4e--')
#g1=Graph('e112-e3-333--')
#g1=Graph('e111-e-')
#g1=Graph('e123-e23-e3-e-')
#g1=Graph('ee12-ee3-333--')
#g1=Graph('ee12-223-3-ee-')
#g1=Graph('e122-e22--')
#g1=Graph('ee12-e33-e33--')
#g1=Graph('ee12-e23-33-e-')
#g1=Graph('e112-e3-e33-e-')
#g1=Graph('ee11-22-33-ee-')
######g1=Graph('e112-e2-33-ee-')
#g1=Graph('ee11-23-e33-e-')
# g1=Graph('ee12-e22-e-')
#4loop
g1=Graph('e122-e33-33--')


#print [x for x in g1.xInternalLines()]
phi4.SetTypes(g1)
g1.FindSubgraphs(phi4)
subs_toremove=subgraphs.DetectSauseges(g1._subgraphs)
g1.RemoveSubgaphs(subs_toremove)
print moments.Generic(phi4, g1)

print_moments(g1._moments())


#print [x for x in g1.xInternalLines()]
#print g1._subgraphs_m
#print "\n\n\n"
jakob,subsvars=roperation.subs_vars(g1)
cnt=0
d=sympy.var('d')
for g in phi4.dTau(g1):
    f=open('test%s.c'%cnt,'w')
    roperation.strechMoments(g, phi4)
    print cnt, g
    

    det=roperation.det(g,phi4)
#    print roperation.AvgByExtDir(roperation.expr(g,phi4))

    expr=(jakob*det*roperation.AvgByExtDir(roperation.expr(g,phi4))).subs(d,phi4.space_dim)
    strechs=roperation.find_strech_atoms(expr)
    integrand=roperation.export_subs_vars_pv(subsvars,strechs)
    integrand+= "\nf[0]=0.;\n"

    integrand+= "f[0]+=%s;\n"%sympy.printing.ccode(expr)
#    integrand+='printf ("result = %20.18g %20.18g %20.18g %20.18g %20.18g %20.18g \\n", f[0],q0,q1,ct_0_1,st_0_1, z_0_1);\n'
    f.write(roperation.core_pv_code(integrand))
    f.close()
    cnt+=1      


