#!/usr/bin/python
# -*- coding:utf8

class Storage:
        def __init__(self):            
            self._storage = dict()

        def _find_empty_idx(self):
             if len(self._storage.keys())==0:
                idx=1
             else:
                idx=int(max(self._storage.keys())+1)
             if idx in self._storage.keys():
                raise ValueError, "invalid index "
             return idx

        def Add(self, obj):
            idx=self._find_empty_idx()
            obj._store_idx=idx
            self._storage[idx]=obj
            return idx

        def Remove(self,idx):
#TODO: implement protection to avoid removing objects that don't belong to graph from which Remove is called ?
            if idx not in self._storage.keys():
                raise ValueError, "Remove: no such index idx:%s"%idx
            del self._storage[idx]
        def Get(self,idx):
            if idx not in self._storage.keys():
                raise ValueError, "Get: no such index idx:%s"%idx
            return self._storage[idx]

# Storage for Nodes of all graphs
class _Nodes( object ):
    ## Stores the unique Singleton instance-
    _iInstance = None
 
    ## Class used with this Python singleton design pattern
 
    ## The constructor
    #  @param self The object pointer.
    def __init__( self ):
        # Check whether we already have an instance
        if _Nodes._iInstance is None:
            # Create and remember instanc
            _Nodes._iInstance = Storage()
 
        # Store instance reference as the only member in the handle
        self._EventHandler_instance = _Nodes._iInstance
 
 
    ## Delegate access to implementation.
    #  @param self The object pointer.
    #  @param attr Attribute wanted.
    #  @return Attribute
    def __getattr__(self, aAttr):
        return getattr(self._iInstance, aAttr)
 
 
    ## Delegate access to implementation.
    #  @param self The object pointer.
    #  @param attr Attribute wanted.
    #  @param value Vaule to be set.
    #  @return Result of operation.
    def __setattr__(self, aAttr, aValue):
        return setattr(self._iInstance, aAttr, aValue)




# Storage for Lines of all graphs
class _Lines( object ):
    ## Stores the unique Singleton instance-
    _iInstance = None
 
    ## The constructor
    #  @param self The object pointer.
    def __init__( self ):
        # Check whether we already have an instance
        if _Lines._iInstance is None:
            # Create and remember instanc
            _Lines._iInstance = Storage()
 
        # Store instance reference as the only member in the handle
        self._EventHandler_instance = _Lines._iInstance
 
 
    ## Delegate access to implementation.
    #  @param self The object pointer.
    #  @param attr Attribute wanted.
    #  @return Attribute
    def __getattr__(self, aAttr):
        return getattr(self._iInstance, aAttr)
 
 
    ## Delegate access to implementation.
    #  @param self The object pointer.
    #  @param attr Attribute wanted.
    #  @param value Vaule to be set.
    #  @return Result of operation.
    def __setattr__(self, aAttr, aValue):
        return setattr(self._iInstance, aAttr, aValue)
