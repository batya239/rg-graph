#!/usr/bin/python
# -*- coding:utf8

import sympy
import moments
from nose.tools import raises

class Test_convert:
    def  test_str2dict(self):
        """ Test str2dict conversion for moments
        """
        assert moments._str2dict('p')=={'p':1}
        assert moments._str2dict('')=={}
        assert moments._str2dict('p+q')=={'p':1,'q':1}
        assert moments._str2dict('p-q')=={'p':1,'q':-1}
        assert moments._str2dict('-p+q')=={'p':-1,'q':1}
        assert moments._str2dict('-p-q')=={'p':-1,'q':-1}
        assert moments._str2dict('-p-q+v')=={'p':-1,'q':-1,'v':1}
    def test_dict2sympy(self):
        """ Test dict2sympy conversion for moments
        """
        (p,q,v) = sympy.var('p q v')
        assert  moments._dict2sympy({})==0
        assert  moments._dict2sympy({'p':1})==p
        assert  moments._dict2sympy({'p':1,'q':1})==p+q
        assert  moments._dict2sympy({'p':1,'q':-1})==p-q
        assert  moments._dict2sympy({'p':1,'q':1,'v':-1})==p+q-v
        assert  moments._dict2sympy({'p':-1,'q':-1,'v':-1})==-p-q-v

class Test_Momenta:
    def test_init_string(self):
        (p,q,v)=sympy.var('p q v')
        pq=moments.Momenta(string='p+q')
        assert pq._string=='p+q'
        assert pq._dict=={'p':1,'q':1}
        assert pq._sympy==p+q

    def test_init_dict(self):
        (p,q,v)=sympy.var('p q v')
        pq=moments.Momenta(dict={'p':1,'q':1})
        assert pq._string=='p+q'
        assert pq._dict=={'p':1,'q':1}
        assert pq._sympy==p+q

    def test_init_sympy(self):
        (p,q,v)=sympy.var('p q v')
        pq=moments.Momenta(sympy=p+q)
        assert pq._string=='p+q'
        assert pq._dict=={'p':1,'q':1}
        assert pq._sympy==p+q

    @raises(TypeError)
    def test_init_err(self):
        p=moments.Momenta()

    def test_neg(self):
        p,q=sympy.var('p q')
        m1=moments.Momenta(sympy=p-q)
        m2=-m1
        assert m1._sympy==-m2._sympy
        
    def test_add(self):
        assert (moments.Momenta(string='p-q')+moments.Momenta(string='q-v'))._sympy==moments.Momenta(string='p-v')._sympy

    def test_sub(self):
        assert (moments.Momenta(string='p-q')-moments.Momenta(string='v-q'))._sympy==moments.Momenta(string='p-v')._sympy

    def test_abs(self):
        p,q,pOq=sympy.var('p q pOq')
        assert abs(moments.Momenta(sympy=p))==sympy.sqrt(p*p)
        print abs(moments.Momenta(sympy=p+q))
        assert abs(moments.Momenta(sympy=p+q))==sympy.sqrt(p*p+q*q+2*p*q*pOq)

    def test_mull(self):
        p,q,v,pOq,pOv,qOv=sympy.var('p q v pOq pOv qOv')
        print moments.Momenta(sympy=-p+q)*moments.Momenta(sympy=q-v)
        assert moments.Momenta(sympy=-p+q)*moments.Momenta(sympy=q-v)==-p*q*pOq+q*q+p*v*pOv-q*v*qOv

    def test_eq(self):
        assert moments.Momenta(sympy=0) == moments.Momenta(dict={})
        assert moments.Momenta(string="p+q") == moments.Momenta(string="q+p")


#     def test_setZeroesByAtoms(self):
 #         pass       pass