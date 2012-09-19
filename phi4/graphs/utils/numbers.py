#!/usr/bin/python
import sympy

def sqsum(a,b):
    return (a**2+b**2)**0.5
def sum(a,b):
    return abs(a+b)

add=sqsum
add=sum

err_add=lambda x,y: add(x.error,y.error)
err_sub=lambda x,y: add(x.error,y.error)

def err_div(a,b):
    if a.number==0:
        return 0
    else:
        return add(a.error/a.number,b.error/b.number)*a.number/b.number

def err_mul(a,b):
    if a.number==0 or b.number==0:
        return 0
    else:
        return add(a.error/a.number,b.error/b.number)*a.number*b.number

def err_pow(a,i):
    if a.number==0:
        return 0
    else:
        return (a.error/a.number*abs(i))*a.number**i



class Number:
    def __init__(self, number, error):
        self.number=sympy.Number(number)
        self.error=abs(sympy.Number(error))
        if str(self.error)=='nan':
            raise Exception, "NAN !! %s, %s"%(number,error)

    def __add__(self, other):
        if isinstance(other, sympy.Number) or isinstance(other, int) or isinstance(other, float):
            return Number(self.number+other, self.error)
        elif isinstance(other, Number):
            return Number(self.number+other.number, err_add(self, other))

    def __sub__(self, other):
        if isinstance(other, sympy.Number) or isinstance(other, int) or isinstance(other, float):
            return Number(self.number-other, self.error)
        elif isinstance(other, Number):
            return Number(self.number-other.number, err_sub(self, other))

    def __div__(self, other):
        if isinstance(other, sympy.Number) or isinstance(other, int) or isinstance(other, float):
            return Number(self.number/other, self.error/other)
        elif isinstance(other, Number):
            return Number(self.number/other.number, err_div(self, other))

    def __mul__(self, other):
        if isinstance(other, sympy.Number) or isinstance(other, int) or isinstance(other, float):
            return Number(self.number*other, self.error*other)
        elif isinstance(other, Number):
            return Number(self.number*other.number, err_mul(self, other))

    def __neg__(self):
        return Number(-self.number, self.error)

    def __radd__(self,other):
        return self+other

    def __rsub__(self, other):
        return (-self)+other

    def __rdiv__(self, other):
        if isinstance(other, sympy.Number) or isinstance(other, int) or isinstance(other, float):
            return Number(other/self.number, err_div( Number(other,0), self) )
        elif isinstance(other, Number):
            return Number(other.number/self.number, err_div(other, self))

    def __rmul__(self,other):
        return self*other

    def __repr__(self):
        return str((self.number, self.error))

    def __pow__(self, other):
        if isinstance(other, (sympy.Number, int, float)):
            return Number(self.number**other,err_pow(self, other))
        else:
            raise NotImplementedError, "pow of Number and not (int, float, sympy.Number)"

def sympyseries_to_list(expr,var,start=0,end=10):
    t=(expr/var**start).expand()
#    print t
    res=list()
    for i in range(end-start):
        res.append((t.subs(var,0),start+i))
        t=t.diff(var)/(i+1)
    return res


class Series:
    def __init__(self, series):
        self._series=dict()
        for term in series:
            number,pow=term
            if pow not in self._series.keys():
                self._series[pow]=number
            else:
                self._series[pow]+=number
    def as_list(self):
        res=list()
        for pow in self._series:
            res.append((self._series[pow],pow))
        return res

    def __neg__(self):
        return Series(map(lambda x: (-x[0],x[1]), self.as_list()))

    def __add__(self, other):
        if isinstance(other, Series):
            return Series(self.as_list()+other.as_list())
        else:
            return Series(self.as_list()+[(other,0)])

    def __radd__(self, other):
        return self+other

    def __sub__(self, other):
        if isinstance(other, Series):
            return Series(self.as_list()+(-other).as_list())
        else:
            return Series(self.as_list()+[(-other,0)])

    def __rsub__(self, other):
        return (-self)+other

    def __mul__(self, other):
        if isinstance(other, Series):
            res=list()
            for pow1 in self._series:
                for pow2 in other._series:
                    res.append((self._series[pow1]*other._series[pow2],pow1+pow2))
            return Series(res)
        elif isinstance(other, (Number, sympy.Number, int, float)):
            return Series(map(lambda x: (x[0]*other, x[1]), self.as_list()))
        else:
            raise TypeError, "cant multiply Series on %s, %s"%(type(other), other)

    def __rmul__(self, other):
        return self*other

    def __div__(self, other):
        if isinstance(other, (Number, sympy.Number, int, float)):
            return Series(map(lambda x: (x[0]/other, x[1]), self.as_list()))
        else:
            raise TypeError, "cant divide Series on %s, %s"%(type(other), other)

    def __str__(self):
        res=""
        for pow in sorted(self._series.keys()):
            res+="+%s*e**%s"%(self._series[pow],pow)
        return res

    def series(self,n):
        res=list()
        for pow in self._series:
            if pow<n:
                res.append((self._series[pow],pow))
        return Series(res)

    def sympy_series(self,n=None, var=None):
        if var==None:
            var=sympy.var('e')
        res=0
        for pow in sorted(self._series.keys()):
            if n==None or pow<n:
                res+=self._series[pow].number*var**pow
        return res

    def sympy_err_series(self,n=None, var=None):
        if var==None:
            var=sympy.var('e')
        res=0
        for pow in sorted(self._series.keys()):
            if n==None or pow<n:
                res+=self._series[pow].error*var**pow
        return res

