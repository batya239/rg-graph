import sympy

from lines import Line
from nodes import Node
import moments

class _generic_model: 
    def __init__( self, name):
        self.name=name
        """ add model specific definitons here        
        """
    def Dim( self, obj ):
        """ using generic _Dim function
        """
        return _Dim(self,obj)

    def SetTypes(self, graph):
        """ using generic _setType
        """
        _SetTypes(graph)
    
    def GenerateMoment(self,graph):
        """ at present time GenerateMoment uses moments.Generic function
        """
        return moments.Generic(self,graph)

    def dTau(self, graph):
        """ applies \partial_{m^2}  on graph (m^2\equiv\tau). 
            returns list of graphs with modifiers
        """
        if 'tau' not in self.modifiers_dim:
            raise ValueError, "there is no tau modifier in model"
        else:
            return _dTau(graph,self)

    def propagator(self, line):
        tau=sympy.var('tau')
        res=1/(line.momenta.Squared()+tau)
        if 'tau' in line.modifiers:
            res=res.diff(tau)
        return res.subs(tau,1)
            
        

    def vertex(self, node):
        return sympy.Number(1)

    def checkmodifier(self,obj,modifier):
        print obj, obj.type
        if isinstance(obj, Line):
            if obj.type in self.lines_modifiers:
                return modifier in self.lines_modifiers[obj.type]
            else:
                return modifier in self.lines_modifiers['default']
        elif isinstance(obj, Node):
            if obj.type in self.nodes_modifiers:
                return modifier in self.nodes_modifiers[obj.type]
            else:
                return modifier in self.nodes_modifiers['default']


class _phi3(_generic_model):
    def __init__( self , name):
        self.name=name
        self.space_dim=6
        self.lines_dim={1:-2}
        self.modifiers_dim={'tau':-2,'p':-1}
        self.lines_modifiers={'default':['tau','p']}
        self.nodes_modifiers={None:[], 'default':['tau','p']}
        self.nodes_dim={1:0}
        self.checktadpoles=False
        
    
class _phi4(_generic_model):
    def __init__( self , name):
        self.name=name
        self.space_dim=4.
        self.lines_dim={1:-2}
        self.modifiers_dim={'tau':-2,'p':-1}
        self.lines_modifiers={'default':['tau','p']}
        self.nodes_modifiers={None:[], 1:[], 'default':['tau','p']}
        self.nodes_dim={1:0, 'e111-e-':2}
        self.checktadpoles=True
        self.reduce=True
        self.subgraphs2reduce=['e111-e-',]

    def vertex(self,node):
        def helper1(k2,B,e):
            return B*k2-(1.-B*k2)*sympy.ln(1.+B*k2)#+1./2.*e*(1.+B*k2)*sympy.ln(1.+B*k2)**2
        def helper2(k2,B,e):
            return -sympy.ln(1.+k2*B)
        if node.type=='e111-e-':
            u,t,d=sympy.var("u_%s_0 u_%s_1 d"%(node.idx(),node.idx()))
            e=self.space_dim-d
            k2=node.Lines()[0].momenta.Squared()
            gamma=sympy.special.gamma_functions.gamma
            B1=1./2.*(u*t*(1.-u)*(1.-u*t/2.))/(1.+t/2.*(1.-u)*(1.-u*t/2.))
            B2=1./2.*(u*t*(1.-u*t)*(1.-u/2.))/(t+1./2.*(1.-u*t)*(1.-u/2.))

            if 'tau' not in node.modifiers:
                res=(-gamma(1.+e)*gamma(2.-e/2.)**2/(4.*(1.-e))*u**(e/2.-1.)*
                        (1./(1.-u)**(1.-e/2.)*( helper1(k2,B1,e))/(1.+t/2.*(1.-u)*(1.-u*t/2.))**(2.-e/2.) + 
                        1./(1.-u*t)**(1.-e/2.)*( helper1(k2,B2,e))/(t+1./2.*(1.-u*t)*(1.-u/2.))**(2.-e/2.) ))
                print "NOT TAU"
            else:
                res=(-gamma(1+e)*gamma(2-e/2.)**2/(4.*(1-e))*u**(e/2.-1)*
                        (1/(1-u)**(1-e/2.)*( helper2(k2,B1,e))/(1+t/2.*(1-u)*(1-u*t/2.))**(2-e/2.) + 
                        1/(1-u*t)**(1-e/2.)*( helper2(k2,B2,e))/(t+1/2.*(1-u*t)*(1-u/2.))**(2-e/2.) ))
                print "TAU"
            return res
        else:
            return sympy.Number(1)


def _SetTypes(graph):
    """ set types for graph nodes and lines ( this implementation may be used only for models with 1 type of lines and 1 type of nodes)
    """
    for line in graph.xInternalLines():
        if line.type==None:
            line.type=1
    for node in graph.xInternalNodes():
        if node.type==None:
            node.type=1

def _Dim(model,obj):
    """ dimension calculation for graph  (nodes, lines and its modifiers)
    """
    if obj.type==None:
        raise ValueError , "cant determine Dim: type is None"
    if isinstance( obj, Line ):
        dim=model.lines_dim[obj.type]
    elif isinstance( obj, Node):
        dim=model.nodes_dim[obj.type]
    else:
        raise ValueError, 'unknown object'
    if obj.modifiers<>None:
        for mod in obj.modifiers:
            dim+=model.modifiers_dim[mod]
    return dim

def _dTau(graph, model):
    """ places tau modifier on each  graph line sequentlially
    """
    res=list()
    for line in graph.xInternalLines():
        if model.checkmodifier(line,'tau'):
            idx=graph.Lines().index(line)
            g=graph.Clone()
            newline=g._Line(idx)
            newline.AddModifier("tau")
            res.append(g)
    for node in graph.xInternalNodes():
        if model.checkmodifier(node,'tau'):
            idx=graph._nodes.index(node)
            g=graph.Clone()
            newnode=g._Node(idx)
            newnode.AddModifier("tau")
            res.append(g)
    return res
