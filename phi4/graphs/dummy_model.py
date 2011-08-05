from lines import Line
from nodes import Node

class _phi3():
    def __init__( self , name):
        self.name=name
        self.space_dim=6
        self.lines_dim={1:-2}
        self.modifiers_dim={'tau':-2,'p':-1}
        self.nodes_dim={1:0}
    def Dim( self, obj ):
        """ using generic _Dim function
        """
        return _Dim(self,obj)

    def SetTypes(self, graph):
        """ using generic _setType
        """
        _SetTypes(graph)
        

def _SetTypes(graph):
    """ set types for graph nodes and lines ( this implementation may be used only for models with 1 type of lines and 1 type of nodes)
    """
    for line in graph.xInternalLines():
        line.type=1
    for node in graph.xInternalNodes():
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

class _phi4():
    def __init__( self , name):
        self.name=name
        self.space_dim=4
        self.lines_dim={1:-2}
        self.modifiers_dim={'tau':-2,'p':-1}
        self.nodes_dim={1:0}
    def Dim( self, obj ):
        """ using generic _Dim function
        """
        return _Dim(self,obj)

    def SetTypes(self, graph):
        """ using generic _setType
        """
        _SetTypes(graph)