#!/usr/bin/python
# -*- coding: utf8 -*-

'''
Created on Apr 19, 2010

@author: mkompan
'''
import utils
import re

def atom_coeffs(momenta,internal_atoms_list, external_atoms_list):
    C=list()
    for atom in internal_atoms_list:
        if atom in momenta.dict.keys():
            C.append(momenta.dict[atom])
        else:
            C.append(0)
    B=list()
    for atom in external_atoms_list:
        if atom in momenta.dict.keys():
            B.append(momenta.dict[atom])
        else:
            B.append(0)
    return (B,C)
    
    
class feynman2_term:
    def __init__(self,C,B,idxL):
        self.lambd = 1
        self.c=C
        self.b=[B,]
        self.line_idx = [idxL,]
        
        
    def append(self,C,B,idxL):
        if self.c == C:
            self.lambd += 1
            self.b.append(B)
            self.line_idx.append(idxL)
            return True
        else:
            return False
        
    

class feynman2:
    def __init__(self,G):
        self.graph = G.Clone()
        self.extra_multiplier = 1.
        external_atoms = set()
        for idxL in G.external_lines:
            line = G.lines[idxL]
            external_atoms = external_atoms | set(line.momenta.dict.keys())
        self.external_atoms_list = list(external_atoms)
        self.external_atoms_list.sort()

        internal_atoms = set()
        for idxL in G.internal_lines:
            line = G.lines[idxL]
            internal_atoms = internal_atoms | (set(line.momenta.dict.keys())
                                               -external_atoms)
        self.internal_atoms_list = list(internal_atoms)
        self.internal_atoms_list.sort()
        self.n = len(self.internal_atoms_list)
        
        if len(self.external_atoms_list)>1:
            raise NotImplementedError, "Dont know what to do with \
more than one external atom: %s"%self.external_atoms_list
        
        self.terms=list()

        phi2nodes = dict()
        
        
        
        for idxL in G.internal_lines:
            line = G.lines[idxL]
            
            for atom in self.internal_atoms_list:
                if atom in line.momenta.dict.keys():
                    if line.momenta.dict[atom] == -1:
                        momenta = -line.momenta
                        break 
                    elif line.momenta.dict[atom] == 1:
                        momenta = line.momenta
                        break
                    else:
                        raise NotImplementedError, "Coefficient of leading \
atom is not equal to +-1. momenta:%s , leading atom: %s"%(line.momenta.string,atom) 


            (B,C)=atom_coeffs(momenta,self.internal_atoms_list,self.external_atoms_list)
            found = False
            for term in self.terms:
                if term.append(C,B,idxL):
                    found = True
                    break
            if not found :
                self.terms.append(feynman2_term(C,B,idxL))
            
            
        #for term in self.terms:
        #    print term.lambd, term.c, term.b, term.line_idx
    def alpha(self):
        res = 0
        for term in self.terms:
            res = res + term.lambd
        return res
    
    def SearchLine(self,idxL):
        for term in self.terms:
            if idxL in term.line_idx:
                return (term.c,term.b[term.line_idx.index(idxL)])
        return (None,None)
    
    def W(self,idxL1,idxL2):
        """ idxL1,idxL2 may be  line indexes in graph or positions in feynman representation 
        """
        if isinstance(idxL1,int): 
            (cur_C1,cur_B1) = self.SearchLine(idxL1)
        elif isinstance(idxL1,tuple) and len(idxL1)==3:
            cur_C1 = self.terms[idxL1[0]].c
            cur_B1 = self.terms[idxL1[0]].b[idxL1[1]]
        else:
            raise NotImplementedError, "unknown 1st argument :%s"%idxL1

        if isinstance(idxL2,int): 
            (cur_C2,cur_B2) = self.SearchLine(idxL2)
        elif isinstance(idxL2,tuple) and len(idxL2)==3:
            cur_C2 = self.terms[idxL2[0]].c
            cur_B2 = self.terms[idxL2[0]].b[idxL2[1]]
        else:
            raise NotImplementedError, "unknown 2nd argument :%s"%idxL2
                
        res = 0.
        
        #print cur_C1,cur_C2
        #print self.cofactorM
        for idx1 in range(self.n):
            for idx2 in range(self.n):
                res = res + cur_C1[idx1]*cur_C2[idx2]*self.cofactorM[idx1,idx2]
        return res
    
    def B(self,pos):
        if len(self.terms[pos[0]].b[pos[1]])<>1:
            raise NotImplementedError, "composite external moment not implemented"            
        return self.terms[pos[0]].b[pos[1]][0]

                



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
                        raise NotImplementedError, "number of dots %s is\
 %s"%(dot,dots[dot])
                    
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
            raise ValueError, "keys of added feynman terms must be equal!\
 (%s,%s)"%(self.key,other.key)
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
                raise NotImplementedError, "don't know what to do with node %s\
 type=%s"%(idxN,node.type)
            if (cur_G.model.node_types[node.type]['feynman'] == 0 and 
                cur_G.model.node_types[node.type]['feynman_sign'] == 1) :
                self.extra_multiplier = (self.extra_multiplier * node.Factor().other 
                                         * node.Factor().factor)
                continue
            else:
                raise ValueError, "invalid combination of feynman (%s) and feynman_sign\
 (%s) in node %s"%(cur_G.model.node_types[node.type]['feynman'],
                                                                                                          cur_G.model.node_types[node.type]['feynman_sign'], idxN)
        self.alpha = 0
        for key in self.terms:
            term  = self.terms[key]
            self.extra_multiplier = self.extra_multiplier * term.sign
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
            raise "Number of internal variables (%s) differs from nloops\
 (%s):"%(self.internal_atoms,self.n)

                
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
    
                