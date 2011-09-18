#!/usr/bin/python

import time                                                

import sympy

def S(d):
    return d*sympy.pi**(d/2.)/sympy.special.gamma_functions.gamma(d/2.+1)


def series_lst(expr, var, n):
    """ f_0+var*f_1+...+var^n*f_n
    """
    if n<0:
        raise ValueError,  "n = %s <0"%n
    res=[]
    if isinstance(expr,(float,int)):
        t_expr=sympy.Number(expr)
    else:
        t_expr=expr
    for i in range(n+1):
        res.append(t_expr.subs(var,0))
        t_expr=t_expr.diff(var)/(i+1)
    return res

def series_f(expr,var, n):
    res=0.
    idx=0
    for expr in series_lst(expr,var,n):
        res=res+expr.evalf()*var**(idx)
        idx+=1
    return res

    


def norm(n,d):
    if n>0:
        res = 1.
    if n>1:
        res = res*S(d-1)/S(d)
    if n>2:
        res = res*S(d-2)/S(d)
    if n>3:
        res = res*S(d-3)/S(d)
    if n>4:
        raise NotImplementedError, "not implemented n=%s, d=%s"%(n,d)
    return res








class TimerStorage:
    def __init__(self):
        self._count=dict()
        self._time=dict()
        self.store=True

    def Add(self, name, time):
        if name in self._count.keys():
            self._count[name]+=1
            self._time[name]+=time
        else:
            self._count[name]=1
            self._time[name]=time
    def Print(self):
	print "\n\nTiming statistics:"
        for name in self._count.keys():
            print "%s : %s / %s = %s"%(name,self._time[name],self._count[name],self._time[name]/float(self._count[name]))
	print "---------------------"



# Storage for Nodes of all graphs
class Timer( object ):
    ## Stores the unique Singleton instance-
    _iInstance = None
 
    ## Class used with this Python singleton design pattern
 
    ## The constructor
    #  @param self The object pointer.
    def __init__( self ):
        # Check whether we already have an instance
        if Timer._iInstance is None:
            # Create and remember instanc
            Timer._iInstance = TimerStorage()
 
        # Store instance reference as the only member in the handle
        self._EventHandler_instance = Timer._iInstance
 
 
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


def timeit(method):

    def timed(*args, **kw):
	
	timer=Timer()
	if timer.store:
            ts = time.time()
            result = method(*args, **kw)
            te = time.time()
            timer.Add(method.__name__,te-ts)
        else:
            result = method(*args, **kw)

        return result

    return timed

