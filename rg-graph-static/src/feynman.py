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
        print "term,key:=",self.key, " --- ", key
        if self.key == key:
            self.lambd = self.lambd + 1
            return True
        else:
            return False

class feynman:
    def __init__(self,G):
        self.graph = G.Clone()
        self.graph.DefineNodes()
        self.graph.FindSubgraphs()
        self.extra_multiplier = sympy.Number(1)
        
        self.terms=list()
        atoms = set()
        
        self.n = self.graph.NLoops()
        for idxL in self.graph.internal_lines:
            dots = self.graph.lines[idxL].dots
            self.graph.lines[idxL].dots = dict()
            key = line_serialize(self.graph.lines[idxL])
            print key, dots
            atoms = atoms | set(self.graph.lines[idxL].momenta.dict.keys())
            
            new = True
            for term in self.terms:
                if term.AddIfEq(key):
                    new = False
                    break
            if new:
                self.terms.append(feynman_term(G.lines[idxL]))

## TODO: add some property in dottype: how dot should be interpreted in feynman 
            if (1 in dots) and (dots[1] >=1):
                for term in self.terms:
                    if term.AddIfEq(key):
                        for i in range(dots[1]-1):
                            term.AddIfEq(key)
                            break
                del dots[1]
                
            self.graph.lines[idxL].dots = dots
                   
        print
        for term in self.terms:
            print term.key ,term.lambd
        print
            
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
                      swiginac.numeric(2)**(-self.n) )
                   
        res_str= str( swiginac.series_to_poly(res.series(s_e==0,self.graph.model.target - self.graph.NLoops()+1)).evalf())
        e = sympy.var('e')
        res_sympy = eval(res_str)
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

        

        e = sympy.var('e')
        print self.alpha,(self.graph.model.space_dim - e)/2
        if M.shape == (1,1):
            M_cofactormatrix = sympy.matrices.Matrix([sympy.Number(1)])
        else:
            M_cofactormatrix = M.cofactorMatrix()
        F = (C*M.det()-(A.T*(M_cofactormatrix*A))[0])

        
        F_s = F
        ext_moment_strech = sympy.var("p_strech")
        for str_atom in self.external_atoms:
            atom = sympy.var(str_atom)
            F_s = F_s.subs(atom, atom*ext_moment_strech)
        
        
        print " F_s = ",F_s
        self.B = F_s.subs(ext_moment_strech,0)
        self.D = F_s.diff(ext_moment_strech).diff(ext_moment_strech).subs(ext_moment_strech,0)/sympy.Number(2)    



        F_m = 1
        for idxU in range(len(u)):
            F_m = F_m * u[idxU]**(self.terms[idxU].lambd-1) 
        F_m = F_m * M.det()**(-(sympy.Number(int(self.graph.model.space_dim))-e)/2-(self.n*(sympy.Number(int(self.graph.model.space_dim)) - e)/2 - self.alpha))
        self.E = F_m

    def R(self):
        
        ext_moment = sympy.var('p e')
        sympy.var('E B D')
        t_res = (E * (B + ext_moment**2 * D) ** 
                 (self.n * (sympy.Number(int(self.graph.model.space_dim)) 
                            - e)/2 - self.alpha))
        
        if len(self.graph.external_lines)==3:
            raise NotImplementedError, " subgraphs with 3 ext_lines are not supported"
        
        d_res = t_res            
        for i in range(self.graph.dim+1):
            t_res = t_res - d_res.subs(ext_moment,0)
            d_res = d_res.diff(ext_moment)/(i+1)
        
        
        res = 0
        d_res = t_res
        for i in range(self.graph.model.target - self.graph.NLoops()+1):
            res = res+e**i*s_res.subs(e,0)
            d_res = d_res.diff(e)/(i+1)

        return d_res
    
    def L_n(self):
        
        ext_moment = sympy.var('p')
        e=sympy.var('e')
        sympy.var('E B D')
        t_res = (self.Gammas() * (B + ext_moment**2 * D) ** 
                 (self.n * (sympy.Number(int(self.graph.model.space_dim)) 
                            - e)/2 - self.alpha))
        print t_res
#        t_res = t_res.subs(E,self.Gammas())
        
        d_res = t_res
        t_res = t_res.subs(ext_moment,0)            
        for i in range(self.graph.dim+1):
            t_res = d_res.subs(ext_moment,0)
            d_res = d_res.diff(ext_moment)/(i+1)
        
            
        print t_res, "dim = ", self.graph.dim
        
        res = 0
        d_res = t_res
        
        if reduce(lambda x,y: x or y, 
                  map(lambda x: (str(x)=='inf') or (str(x)=='-inf'), 
                      d_res.expand().subs(e,0).atoms())):
            raise NotImplementedError, "Series on eps includes 1/eps term"
        for i in range(self.graph.model.target - self.graph.NLoops()+1):
            print e**i*d_res.expand().subs(e,0)
            res = res+e**i*d_res.expand().subs(e,0)
            d_res = d_res.diff(e)/(i+1)
        return res
                 
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
        cur_G=G.Clone()
        cur_G.lines[3].dots[1] = 1
        cur_G.WorkDir()
        cur_G.FindSubgraphs()
        if not CheckNodes(cur_G):
            print "%s has nodes with type <> 1 "%nickel
            continue
        G_s = StrechAllSubgraphs(cur_G)
        F=feynman(G_s)

        
        print nickel
        print 
        print "  F =  %s"%F
        F.QForm()
        print
        print "F.B = ", F.B
        print
        print "F.D = ", F.D
        print
        print "F.E = ",F.E
        print
        print "GAMMAS = %s"%F.Gammas()
        print 
        print F.L_n()

        print 
        print G_s.s_degree
        
        
        lines=dict()
        
