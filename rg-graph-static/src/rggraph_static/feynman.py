#!/usr/bin/python
# -*- coding: utf8 -*-

'''
Created on Apr 19, 2010

@author: mkompan
'''
import utils
import sympy
import re

class feynman_term:
    def __init__(self, model=None, Line=None):
        if model<>None and Line <> None:
            dots = Line.dots
            new_dots = dict()
            cnt = 1
            self.sign = 1
            for dot in dots:
                if 'feynman' in model.dot_types[dot]:
                    if dots[dot]<>1:
                        raise NotImplementedError, "number of dots %s is %s"%(dot,dots[dot])
                    
                    cnt = cnt + model.dot_types[dot]['feynman'] 
                    self.sign = self.sign * model.dot_types[dot]['feynman_sign']
                else:
                    new_dots[dot] = dots[dot]
                if cnt > 2:
                    raise NotImplementedError, "total number of dots >1 (%s)"%(cnt-1)
            Line.dots = new_dots
            self.key = utils.line_serialize(Line)
            self.line = Line
            self.lambd = cnt
        else:
            self.sign = 1
            self.key = ""
            self.line = None
            self.lambd = 0

        
    def __add__(self, other):
        if self.key <> other.key:
            raise ValueError, "keys of added feynman terms must be equal! (%s,%s)"%(self.key,other.key)
        new_ft = feynman_term()
        new_ft.sign = self.sign*other.sign
        new_ft.key = self.key
        new_ft.line = self.line
        new_ft.lambd = self.lambd + other.lambd
        return new_ft
        
        
        
class feynman:
    def __init__(self,G):
        cur_G = G.Clone()
        self.terms = dict()
        self.graph = cur_G
        self.n = self.graph.NLoops()
        self.extra_multiplier = 1
        self.line_map = dict()
        atoms = set()
        for idxL in cur_G.internal_lines:
            line = cur_G.lines[idxL]
            atoms = atoms | set(line.momenta.dict.keys())
            
            t_term = feynman_term(cur_G.model, line)
            self.line_map[idxL] = t_term.key
            
            if t_term.key in self.terms:
                self.terms[t_term.key] = self.terms[t_term.key] + t_term
            else:
                self.terms[t_term.key] = t_term

        for idxN in cur_G.internal_nodes:
            node = cur_G.nodes[idxN]
            if 'feynman' not in cur_G.model.node_types[node.type]:
                raise NotImplementedError, "don't know what to do with node %s type=%s"%(idxN,node.type)
            if (cur_G.model.node_types[node.type]['feynman'] == 0 and 
                cur_G.model.node_types[node.type]['feynman_sign'] == 1) :
                self.extra_multiplier = self.extra_multiplier * node.Factor().other * node.Factor().factor
                continue
            else:
                raise ValueError, "invalid combination of feynman (%s) and feynman_sign (%s) in node %s"%(cur_G.model.node_types[node.type]['feynman'],
                                                                                                          cur_G.model.node_types[node.type]['feynman_sign'], idxN)
        self.alpha = 0
        for key in self.terms:
            term  = self.terms[key]
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
        for key in self.terms:
            term = self.terms[key]
            res[key] = (term.lambd, term.sign)
        res['extra_multiplier'] = self.extra_multiplier
        res['alpha'] = self.alpha
        res['n'] = self.n
        res['internal'] = self.internal_atoms
        res['external'] = self.external_atoms  
        return str(res)
    
#    def Gammas(self):
#        import swiginac
#        s_e=swiginac.symbol('e')
#        res = 1
#        for key in self.terms:
#            term = self.terms[key]
#            res = res / swiginac.tgamma(term.lambd)
#        res = res * ( swiginac.tgamma(self.alpha - self.n*(swiginac.numeric(int(self.graph.model.space_dim))-s_e)/2)*
#                      (swiginac.tgamma((swiginac.numeric(int(self.graph.model.space_dim))-s_e)/2))**self.n *
#                      swiginac.numeric(2)**(-self.n) )
#                   
#        res_str= str( swiginac.series_to_poly(res.series(s_e==0,self.graph.model.target - self.graph.NLoops()+1)).evalf())
#        e = sympy.var('e')
#        res_sympy = eval(res_str)
#        return res_sympy


                