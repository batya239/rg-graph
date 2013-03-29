import sympy

from lines import Line
from nodes import Node
import moments
import subgraphs
from graphs import Graph


class _generic_model(object):
    def __init__( self, name):
        self.name = name
        """ add model specific definitons here        
        """

    def Dim( self, obj ):
        """ using generic _Dim function
        """
        return _Dim(self, obj)

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
            raise ValueError("there is no tau modifier in model")
        else:
            return _dTau(graph, self)

    def propagator(self, line):
        tau = sympy.var('tau')
        res = 1 / (line.momenta.Squared() + tau)
        if 'tau' in line.modifiers:
            res = res.diff(tau)
        return res.subs(tau, 1)

    def vertex(self, node):
        return sympy.Number(1)

    def toreduce(self, g):
        return []

    def checkmodifier(self, obj, modifier):
    #        print obj, obj.type
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

        else:
            raise TypeError, "Unsuppoerted object %s" % obj


class _phi3(_generic_model):
    def __init__( self, name):
        self.name = name
        self.space_dim = 6
        self.lines_dim = {1: -2}
        self.modifiers_dim = {'tau': -2, 'p': -1}
        self.lines_modifiers = {'default': ['tau', 'p']}
        self.nodes_modifiers = {None: [], 'default': ['tau', 'p']}
        self.nodes_dim = {1: 0}
        self.checktadpoles = False
        self.target = 4
        self.workdir = '/home/mkompan/work/rg-graph/phi_4/'


class _phi3_dyn(_generic_model):
    def __init__(self, name):
        self.name = name
        self.space_dim = 6
        self.freq_dim = 2
        self.space_dim_eff = self.space_dim + self.freq_dim

        self.lines_dim = {('a', 'A'): -2, ('A', 'a'): -2, ('a', 'a'): -4}
        self.modifiers_dim = {'tau': -2, 'p': -1}
        self.lines_modifiers = {'default': ['tau', 'p']}
        self.nodes_modifiers = {None: [], 'default': ['tau', 'p']}
        self.nodes_dim = {1: 0}
        self.checktadpoles = False
        self.target = 3
        self.workdir = '/home/mkompan/work/rg-graph/phi3_dyn/'


class _phi4_dyn(_generic_model):
    def __init__(self, name):
        self.name = name
        self.space_dim = 4
        self.freq_dim = 2
        self.space_dim_eff = self.space_dim + self.freq_dim

        self.lines_dim = {('a', 'A'): -2, ('A', 'a'): -2, ('a', 'a'): -4}
        self.modifiers_dim = {'tau': -2, 'p': -1}
        self.lines_modifiers = {'default': ['tau', 'p']}
        self.nodes_modifiers = {None: [], 'default': ['tau', 'p']}
        self.nodes_dim = {1: 0}
        self.checktadpoles = True
        self.target = 4
        self.workdir = 'phi4_dyn/'


class _phi4(_generic_model):
    def __init__( self, name):
        self.name = name
        self.space_dim = 4.
        self.lines_dim = {1: -2, 'e111-e-': 2, 'ee11-ee-': 0}
        self.modifiers_dim = {'tau': -2, 'p': -1}
        self.lines_modifiers = {'default': ['tau', 'p']}
        self.nodes_modifiers = {None: [], 1: [], 'default': ['tau', 'p']}
        self.nodes_dim = {1: 0, 2: 0}
        self.checktadpoles = True
        self.reduce = True
        self.subgraphs2reduce = ['e111-e-', 'ee11-ee-']
        self.use_analitic_sub = False
        #        self.subgraphs2reduce=['e111-e-', ]
        #        self.target=5
        #        self.workdir='/home/mkompan/work/rg-graph/phi_4/'
        self.target = 6
        self.workdir = '/home/mkompan/work/rg-graph/phi_4_6/'

    def propagator(self, line, neps=None):
        def helper1(k2,B,e):
#            return B*k2-(1.+B*k2)*sympy.ln(1.+B*k2)+1./2.*e*(1.+B*k2)*sympy.ln(1.+B*k2)**2
            return ( -1.0*sympy.ln(1.0 + B*k2) + B*k2 + 0.0505142257898985*e**3*sympy.ln(1.0 + B*k2) + 0.081871938683557*e**5*sympy.ln(1.0 + B*k2) -
                        1.48370055013617*e**2*sympy.ln(1.0 + B*k2) - 1.62383707071844*e**4*sympy.ln(1.0 + B*k2) - 1.0*B*k2*sympy.ln(1.0 + B*k2) +
                        0.0505142257898986*B*k2*e**3*sympy.ln(1.0 + B*k2) + 0.0818719386835572*B*k2*e**5*sympy.ln(1.0 + B*k2) -
                        1.48370055013617*B*k2*e**2*sympy.ln(1.0 + B*k2) - 1.62383707071844*B*k2*e**4*sympy.ln(1.0 + B*k2) + 0.5*e*sympy.ln(1.0 + B*k2)**2 +
                        0.741850275068085*e**3*sympy.ln(1.0 + B*k2)**2 + 0.811918535359222*e**5*sympy.ln(1.0 + B*k2)**2 -
                        0.0252571128949494*e**4*sympy.ln(1.0 + B*k2)**2 + 1.48370055013617*B*k2*e**2 + 0.5*B*e*k2*sympy.ln(1.0 + B*k2)**2 +
                        0.811918535359222*B*k2*e**5*sympy.ln(1.0 + B*k2)**2 + 0.741850275068085*B*k2*e**3*sympy.ln(1.0 + B*k2)**2 -
                        0.0252571128949494*B*k2*e**4*sympy.ln(1.0 + B*k2)**2 + 0.00841903763164975*e**5*sympy.ln(1.0 + B*k2)**3 -
                        0.247283425022695*e**4*sympy.ln(1.0 + B*k2)**3 - 0.166666666666667*e**2*sympy.ln(1.0 + B*k2)**3 - 0.0505142257898986*B*k2*e**3 +
                        0.00841903763164974*B*k2*e**5*sympy.ln(1.0 + B*k2)**3 - 0.247283425022695*B*k2*e**4*sympy.ln(1.0 + B*k2)**3 -
                        0.166666666666667*B*k2*e**2*sympy.ln(1.0 + B*k2)**3 + 0.0416666666666667*e**3*sympy.ln(1.0 + B*k2)**4 +
                        0.0618208562556737*e**5*sympy.ln(1.0 + B*k2)**4 + 1.62383707071844*B*k2*e**4 + 0.0618208562556737*B*k2*e**5*sympy.ln(1.0 + B*k2)**4 +
                        0.0416666666666667*B*k2*e**3*sympy.ln(1.0 + B*k2)**4 - 4.33680868994202e-19*e**5*sympy.ln(1.0 + B*k2)**5 -
                        0.00833333333333333*e**4*sympy.ln(1.0 + B*k2)**5 - 0.0818719386835573*B*k2*e**5 - 4.33680868994202e-19*B*k2*e**5*sympy.ln(1.0 + B*k2)**5 -
                        0.00833333333333333*B*k2*e**4*sympy.ln(1.0 + B*k2)**5 +0.00138888888888889*e**5*sympy.ln(1.0 + B*k2)**6 +
                        0.00138888888888889*B*k2*e**5*sympy.ln(1.0 + B*k2)**6)

        def helper2(k2,B,e):
#            return -sympy.ln(1.+k2*B)
            return (-1.0*sympy.ln(1.0 + B*k2) + 1.0*e*sympy.ln(1.0 + B*k2) + 1.705709009402*e**5*sympy.ln(1.0 + B*k2) + 1.53421477592607*e**3*sympy.ln(1.0 + B*k2) -
                        1.48370055013617*e**2*sympy.ln(1.0 + B*k2) - 1.67435129650834*e**4*sympy.ln(1.0 + B*k2) + 0.5*e*sympy.ln(1.0 + B*k2)**2 +
                        0.741850275068085*e**3*sympy.ln(1.0 + B*k2)**2 + 0.837175648254171*e**5*sympy.ln(1.0 + B*k2)**2 - 0.5*e**2*sympy.ln(1.0 + B*k2)**2 -
                        0.767107387963034*e**4*sympy.ln(1.0 + B*k2)**2 + 0.255702462654345*e**5*sympy.ln(1.0 + B*k2)**3 + 0.166666666666667*e**3*sympy.ln(1.0 + B*k2)**3 -
                        0.247283425022695*e**4*sympy.ln(1.0 + B*k2)**3 - 0.166666666666667*e**2*sympy.ln(1.0 + B*k2)**3 + 0.0618208562556737*e**5*sympy.ln(1.0 + B*k2)**4 +
                        0.0416666666666667*e**3*sympy.ln(1.0 + B*k2)**4 - 0.0416666666666667*e**4*sympy.ln(1.0 + B*k2)**4 + 0.00833333333333333*e**5*sympy.ln(1.0 + B*k2)**5 -
                        0.00833333333333333*e**4*sympy.ln(1.0 + B*k2)**5 + 0.00138888888888889*e**5*sympy.ln(1.0 + B*k2)**6)

        if line.type=='e111-e-':
            u,t,d=sympy.var("u_%sL_0 u_%sL_1 d"%(line.idx(),line.idx()))
            e=self.space_dim-d
            k2=line.momenta.Squared()
            gamma=sympy.special.gamma_functions.gamma
            B1=1./2.*(u*t*(1.-u)*(1.-u*t/2.))/(1.+t/2.*(1.-u)*(1.-u*t/2.))
            B2=1./2.*(u*t*(1.-u*t)*(1.-u/2.))/(t+1./2.*(1.-u*t)*(1.-u/2.))

            if 'tau' not in line.modifiers:
                res=(-1./(4.)*u**(e/2.-1.)*
                        (1./(1.-u)**(1.-e/2.)*( helper1(k2,B1,e))/(1.+t/2.*(1.-u)*(1.-u*t/2.))**(2.-e/2.) +
                        1./(1.-u*t)**(1.-e/2.)*( helper1(k2,B2,e))/(t+1./2.*(1.-u*t)*(1.-u/2.))**(2.-e/2.) ))
#                print "NOT TAU"
            else:
                res=-((-1./(4.)*u**(e/2.-1.)*
                        (1./(1.-u)**(1.-e/2.)*( helper2(k2,B1,e))/(1.+t/2.*(1.-u)*(1.-u*t/2.))**(2.-e/2.) +
                        1./(1.-u*t)**(1.-e/2.)*( helper2(k2,B2,e))/(t+1./2.*(1.-u*t)*(1.-u/2.))**(2.-e/2.) )))
 #               print "TAU"
            return res
#end of e111-e-
        elif line.type=='ee11-ee-':
            u,d=sympy.var("u_%sL_0 d"%(line.idx()))
            e=self.space_dim-d
            k2=line.momenta.Squared()
            print "neps=", neps
            if neps==None:
                gammas=0.5 - 0.25*e + 0.205616758356028*e**2 - 0.102808379178014*e**3 + 0.0591895518435779*e**4 - 0.0295947759217889*e**5 + 0.0153992358015224*e**6 - 0.00769961790076121*e**7
                if 'tau' not in line.modifiers:
                    res=gammas*k2*(u-2.*u*u)/((1.+k2*u*(1.-u))**(1.+e/2.))

                else:
                    res=gammas*(1.+k2*u*(1.-u))**(-1.-0.5*e)
                return res
            elif neps==0:
                k=k2**0.5
                if 'tau' not in line.modifiers:
                    res=1.-(4./k2+1.)**0.5/2.*sympy.ln(((4./k2+1.)**0.5+1.)**2*k2/4.)
                else:
                    res=1./(4./k2+1.)**0.5/k2*sympy.ln(((4./k2+1.)**0.5+1.)**2*k2/4.)
                return res
#                if 'tau' not in line.modifiers:
#                    res=1.-(4./(k2+1)+1.)**0.5/2.*sympy.ln(((4./(k2+1)+1.)**0.5+1.)/((4./(k2+1)+1.)**0.5-1.))
##                       res=1.
#                else:
##                       res=0.
#                    res=1./(4./(k2+1)+1.)**0.5/(k2+1)*sympy.ln(((4./(k2+1)+1.)**0.5+1.)/((4./(k2+1)+1.)**0.5-1.))
#                return res

        else:
            tau=sympy.var('tau')
            res=1/(line.momenta.Squared()+tau)
            if 'tau' in line.modifiers:
                res=-res.diff(tau)
            return res.subs(tau,1)

    def toreduce(self, g):
        res = []
        for sub in g._subgraphs:
            if str(sub.Nickel()) == 'e111-e-':
                res.append(sub)
            elif str(sub.Nickel()) == 'ee11-ee-':
                good = True
                for sub2 in g._subgraphs:
                    if sub <> sub2 and subgraphs.cover(sub, sub2):
                        if str(sub2.Nickel()) in self.subgraphs2reduce:
                            good = False
                            break
                if good:
                    res.append(sub)
        return res

    def SetTypes(self, graph):
        """ set types for graph nodes and lines ( this implementation may be used only for models with 1 type of lines and 1 type of nodes)
        """
        for line in graph.xInternalLines():
            if line.type is None:
                line.type = 1
        for node in graph.xInternalNodes():
            if node.type is None:
                if len(node.Lines()) == 2:
                    node.type = 2
                else:
                    node.type = 1


def _SetTypes(graph):
    """ set types for graph nodes and lines ( this implementation may be used only for models with 1 type of lines and 1 type of nodes)
    """
    for line in graph.xInternalLines():
        if line.type == None:
            line.type = 1
    for node in graph.xInternalNodes():
        if node.type == None:
            node.type = 1


def _Dim(model, obj):
    """ dimension calculation for graph  (nodes, lines and its modifiers)
    """
    if obj.type == None:
        raise ValueError, "cant determine Dim: type is None"
    if isinstance(obj, Line):
        dim = model.lines_dim[obj.type]
    elif isinstance(obj, Node):
        dim = model.nodes_dim[obj.type]
    else:
        raise ValueError, 'unknown object'
    if obj.modifiers <> None:
        for mod in obj.modifiers:
            dim += model.modifiers_dim[mod]
    return dim


class _phi4_d3(_generic_model):
    def __init__(self, name):
        self.name = name
        self.space_dim = 3.
#        self.lines_dim = {1: -2}
#        self.modifiers_dim = {'tau': -2, 'p': -1}
#        self.lines_modifiers = {'default': ['tau', 'p']}
#        self.nodes_modifiers = {None: [], 1: [], 'default': ['tau', 'p']}
#        self.nodes_dim = {1: 0, 2: 0}
#        self.checktadpoles = True
#        self.reduce = True
#        self.subgraphs2reduce = ['e111-e-', 'ee11-ee-']
#        self.use_analitic_sub = False
        #        self.subgraphs2reduce=['e111-e-', ]
        #        self.target=5
        #        self.workdir='/home/mkompan/work/rg-graph/phi_4/'
        self.subgraphDim = True
        self.target = 6
        self.workdir = '/home/mkompan/work/rg-graph/phi_4_d3/'
        self.removeRoots = False

    def Dim(self, obj):
        if isinstance(obj, Graph):
            if obj.ExternalLines() == 2:
                return 0
            else:
                return -1
        elif isinstance(obj, subgraphs.Subgraph):
            if obj.CountExtLegs() == 2:
                return 0
            else:
                return -1
        else:
            raise NotImplementedError("Dim not defined for %s" % obj)

    @staticmethod
    def normalizeN(graph, result):
        import sympy
        G = sympy.special.gamma_functions.gamma
        (res_, err_) = result
        n = graph.NLoops()
    #    return map(lambda x: (x[0] / graph.sym_coef(),), result)
        return map(lambda x: (x[0] / graph.sym_coef() * (G(n / 2.) / sympy.pi ** (n / 2.)).evalf(),), result)


class _phi4_d2(_generic_model):
    def __init__(self, name):
        self.name = name
        self.space_dim = 2.
        self.subgraphDim = True
        self.target = 6
        self.workdir = '/home/mkompan/work/rg-graph/phi_4_d2/'
        self.removeRoots = False
#        self.subtractionOperators = "from dynamics import to1, D1, mK0\n"

    def Dim(self, obj):
        if isinstance(obj, Graph):
            if obj.ExternalLines() == 2:
                return 0
            else:
                return -1
        elif isinstance(obj, subgraphs.Subgraph):
            if obj.CountExtLegs() == 2:
                return 0
            else:
                return -1
        else:
            raise NotImplementedError("Dim not defined for %s" % obj)

    @staticmethod
    def normalizeN(graph, result):
        import sympy
        G = sympy.special.gamma_functions.gamma
        (res_, err_) = result
        n = graph.NLoops()
        #    return map(lambda x: (x[0] / graph.sym_coef(),), result)
        return map(lambda x: (x[0] / graph.sym_coef() * (G(n)).evalf(),), result)


class _phi4_d2_s2(_phi4_d2):
    def __init__(self, name):
        self.name = name
        self.space_dim = 2.
        self.subgraphDim = True
        self.target = 6
        self.workdir = '/home/mkompan/work/rg-graph/phi_4_d2_s2/'
        self.removeRoots = False
        self.subtractionOperators = "from dynamics import to1\nfrom dynamics import mK1 as mK0\nfrom dynamics import D2s as D1\n"
