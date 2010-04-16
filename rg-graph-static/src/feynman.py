#!/usr/bin/python
# -*- coding:utf8

model=None
import sys
import re
import rggraph_static as rggrf
import sympy

def usage(progname):
    return "%s -model phi3R [-overwrite] [-graph str_nickel] [-debug]"

if "-model" in sys.argv:
    model_module = sys.argv[sys.argv.index('-model')+1]
    try:
        exec('from %s import *'%model_module)
    except:
        print "Error while importing model!"
        sys.exit(1)
else:
    print "Usage : %s " %usage(sys.argv[0])
    sys.exit(1)


if "-graph" in sys.argv:
    g_list = [sys.argv[sys.argv.index('-graph')+1],]
else:
    g_list = model.GraphList()
    
if "-debug" in sys.argv:
    debug = True
else:
    debug = False


if "-nloops" in sys.argv:
    nloops = eval(sys.argv[sys.argv.index('-nloops')+1])
    if isinstance(nloops,int):
        nloops = [nloops,]
else:
    nloops = range(1,model.target+1)    

def CheckNodes(G):
    for idxN in G.internal_nodes:
        if G.nodes[idxN].type <> 1:
            return False
    return True

class feynman_term:
    def __init__(self, line):
        self.key = line_serialize(line)
        self.line = line
        self.lambd = 1
        
    def AddIfEq(self,key):
        if self.key == key:
            self.lambd = self.lambd + 1
            return True
        else:
            return False

class feynman:
    def __init__(self,G):
        self.graph = G
        self.terms=list()
        atoms = set()
        
        self.n = G.NLoops()
        for idxL in G.internal_lines:
            key = line_serialize(G.lines[idxL])
            atoms = atoms | set(G.lines[idxL].momenta.dict.keys())
            new = True
            for term in self.terms:
                if term.AddIfEq(key):
                    new = False
                    break
            if new:
                self.terms.append(feynman_term(G.lines[idxL]))
        self.alpha = 0
        for term in self.terms:
            self.alpha = self.alpha + term.lambd
        
        self.internal_atoms=set()
        self.external_atoms=set()
        for atom in atoms:
            if re.match("^q",atom):
                self.internal_atoms = self.internal_atoms | set([atom,])
            else:
                self.external_atoms = self.external_atoms | set([atom,])
        self.internal_atoms = tuple(self.internal_atoms)
        self.external_atoms = tuple(self.external_atoms)
        if len(self.internal_atoms) <> self.n:
            raise "Number of internal variables (%s) differs from nloops (%s):"%(self.internal_atoms,self.n)
            
        
    
    def __str__(self):
        res = dict()
        for idx in range(len(self.terms)):
            term = self.terms[idx]
            res[idx] = (term.key,term.lambd)
        res['alpha'] = self.alpha
        res['n'] = self.n
        res['internal'] = self.internal_atoms
        res['external'] = self.external_atoms
        return str(res)
    
    def Gammas(self):
        import swiginac
        s_e=swiginac.symbol('e')
        res = 1
        for term in self.terms:
            res = res / swiginac.tgamma(term.lambd)
        res = res * ( swiginac.tgamma(self.alpha - self.n*(swiginac.numeric(int(self.graph.model.space_dim))-s_e)/2)*
                      (swiginac.tgamma((swiginac.numeric(int(self.graph.model.space_dim))-s_e)/2))**self.n *
                      swiginac.numeric(2)**(-self.n) )*s_e
        res_str= str( swiginac.series_to_poly(res.series(s_e==0,self.graph.model.target - self.graph.NLoops()+1)).evalf())
        e = sympy.var('e')
        res_sympy = eval(res_str)
#        sympy.pretty_print(res_sympy)
        return res_sympy
        
            
    def QForm(self):
        u = dict()
        Q = 0
        for idxT in range(len(self.terms)):
            u[idxT] = sympy.var('u%s'%idxT)
            term = self.terms[idxT]
#            Q = Q + u[idxT]*(term.line.momenta.Squared() + 1)
            Q = Q + u[idxT]/term.line.Propagator()     
        Q=ExpandScalarProds(Q).subs(sympy.var('tau'),1)
        
        #remove scalar prods q1xq2 pxq1 ...
        for atom in Q.atoms():
            if re.search('x',str(atom)):
                Q = Q.subs(atom,1)
        
        M=sympy.matrices.Matrix(self.n,self.n, lambda i,j:0)
        A=sympy.matrices.Matrix([0 for i in range(self.n)])
        C=Q
        for i in range(self.n):
            qi=sympy.var(self.internal_atoms[i])
            C=C.subs(qi,0)
            A[i] = Q.diff(qi)/sympy.Number(2)
            for j in range(self.n):
                qj=sympy.var(self.internal_atoms[j])
                A[i]=A[i].subs(qj,0)
                if i>=j:
                    M[i,j] = Q.diff(qi).diff(qj)/sympy.Number(2)
                    if i<>j:
                        M[j,i] = M[i,j]

        
                
#        print C
#        print A
#        print M
#        print M.det()
        e = sympy.var('e')
        print self.alpha,(self.graph.model.space_dim - e)/2
        if M.shape == (1,1):
            M_cofactormatrix = sympy.matrices.Matrix([sympy.Number(1)])
        else:
            M_cofactormatrix = M.cofactorMatrix()
        F = (C*M.det()-(A.T*(M_cofactormatrix*A))[0])**(self.n*(sympy.Number(int(self.graph.model.space_dim)) - e)/2 - self.alpha)
        
        F_s = F
        ext_moment_strech = sympy.var("p_strech")
        for str_atom in self.external_atoms:
            atom = sympy.var(str_atom)
            F_s = F_s.subs(atom, atom*ext_moment_strech)
        
#        sympy.var('AA BB p')
#        F_s = (AA+p*p*ext_moment_strech*ext_moment_strech*BB)**(1-e)
        
        print " F_s = ",F_s    
        F_p = F_s.subs(ext_moment_strech,1)
        t_F_s = F_s
        for i in range(self.graph.dim + 1):
            print " ===> ",t_F_s.subs(ext_moment_strech,0)
            F_p = F_p - t_F_s.subs(ext_moment_strech,0)
            t_F_s = t_F_s.diff(ext_moment_strech)/(i+1)
        F_p = F_p.expand()
            
#        print "============="    
#        print F_p
#        print "============="    
#        print F_p.subs(e,0)
#        print "============="    
        
        F_pe = 0
        t_F_p = F_p
        for i in range(self.graph.model.target - self.graph.NLoops()+1):
            F_pe = F_pe+e**i*t_F_p.subs(e,0)
            t_F_p = t_F_p.diff(e)/(i+1)
        
        F_pe = (F_pe/e).expand()
        
#        print "------------"    
#        print F_pe
#        print "------------"    
#        print F_pe.subs(e,0)


        F_m = 1
        for idxU in range(len(u)):
            F_m = F_m * u[idxU]**(self.terms[idxU].lambd-1) 
        F_m = F_m * M.det()**(-(sympy.Number(int(self.graph.model.space_dim))-e)/2-(self.n*(sympy.Number(int(self.graph.model.space_dim)) - e)/2 - self.alpha))
        print "F_m = ", F_m
        #print F_m
        return F_pe
        
def StrechAllSubgraphs(G):
    cur_G=G.Clone()
    cur_G.s_degree=dict()
    for sub in cur_G.subgraphs:
        sub_ext_atoms_str = FindExtMomentAtoms(sub)
        strech_var_str = "s%s"%cur_G.subgraphs.index(sub)
        sub_ext_path = [(i[0],i[1],strech_var_str) for i in FindExtMomentPath(sub, sub_ext_atoms_str)]
        for idx in sub_ext_path:
            if idx[1]=="L":
                obj = cur_G.lines[idx[0]]
            elif idx[1]=="N":
                obj = cur_G.nodes[idx[0]]
            model.AddStrech(obj, strech_var_str, sub_ext_atoms_str)
        cur_G.s_degree[strech_var_str] = subgraph_dim_with_diff(cur_G, sub) +1
        
        
    return cur_G
                     
        

for nickel in g_list: 
    G = model.LoadGraph(nickel)
    if G.NLoops() in nloops:
        G.WorkDir()
        G.FindSubgraphs()
        if not CheckNodes(G):
            print "%s has nodes with type <> 1 "%nickel
            continue
        G_s = StrechAllSubgraphs(G)
        F=feynman(G_s)

        
        print nickel
        print "    %s"%F
#        print "\n%s"%F.QForm()
        print
        print "GAMMAS = %s"%F.Gammas()
        print 
        print G_s.s_degree
        
        
        lines=dict()
        
