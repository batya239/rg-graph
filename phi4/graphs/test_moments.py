#!/usr/bin/python
# -*- coding:utf8
from nose.tools import raises
from moments import *
import sympy


class Test_str2dict:
    @raises(TypeError)
    def test_wrongtype1(self):
            str2dict(1)

    @raises(TypeError)
    def test_wrongtype2(self):
            str2dict({})

    @raises(TypeError)
    def test_emptyargs(self):
        str2dict()

    def test_zerostring(self):
        assert str2dict('') == dict()

    def test_simple1(self):
        assert str2dict('q') == {'q':1}
        assert str2dict('+q') == {'q':1}
        assert str2dict(' + q2 ') == {'q2':1}
        assert str2dict(' qqqww234 ') == {'qqqww234':1}

    @raises(ValueError)
    def test_simple1_e1(self):
        str2dict('qq2qq')

    @raises(ValueError)
    def test_simple1_e2(self):
        str2dict('2')

    @raises(ValueError)
    def test_simple1_e3(self):
        str2dict('2*q2')


    @raises(ValueError)
    def test_simple1_e4(self):
        str2dict('q2*2')

    def test_simple2(self):
        assert str2dict('-q') == {'q':-1}
        assert str2dict(' - q1 ') == {'q1':-1}

    @raises(ValueError)
    def test_simple2_e1(self):
        str2dict('-qq2qq')

    @raises(ValueError)
    def test_simple2_e1(self):
        str2dict('-2')

    @raises(ValueError)
    def test_complex_e1(self):
        str2dict('q2+q3-2*q4') 

    def test_complex(self):
        assert str2dict('q2+q3-q4') == {'q2':1,'q3':1,'q4':-1}

class Test_dict2str:
    @raises(TypeError)
    def test_emptyargs(self):
        dict2str()

    def test_emptydict(self):
        assert dict2str({}) == ''

    def test_simple1(self):
        assert dict2str({'q':1}) == '+q'
        assert dict2str( {'q2':1}) == '+q2'

    @raises(ValueError)
    def test_simple1_e1(self):
        dict2str({'qq2qq':1})
    
    @raises(ValueError)
    def test_simple1_e2(self):
        dict2str({'2':1})


    @raises(ValueError)
    def test_simple1_e3(self):
        dict2str({'q2':2})


    def test_simple2(self):
        assert dict2str({'q':-1}) == '-q'
        assert dict2str( {'q2':-1}) == '-q2'

    @raises(ValueError)
    def test_simple2_e1(self):
        dict2str({'qq2qq':-1})

    @raises(ValueError)
    def test_simple2_e2(self):
        dict2str({'2':-1})

    @raises(ValueError)
    def test_simple2_e2(self):
        dict2str({'q2':-2})

    @raises(ValueError)
    def test_complex_e1(self):
        dict2str({'q2':1,'q3':1,'q4':-2} )

    def test_complex(self):
        res=['+q2+q3-q4','+q3+q2-q4','+q2-q4+q3',
             '+q3-q4+q2','-q4+q2+q3','-q4+q3+q2']   
        assert dict2str({'q2':1,'q3':1,'q4':-1}) in res

class Test_dict2sympy:
    @raises(TypeError)
    def test_wrongtype_1(self):
        dict2sympy("atr")

    @raises(TypeError)
    def test_wrongtype_2(self):
        dict2sympy(2)

    @raises(TypeError)
    def test_wrongtype_3(self):
        dict2sympy(['asa','2'])

    def test_empty(self):
        assert dict2sympy({}) == 0

    def test_complex(self):
        list_=[{'q1':1}, 
               {'q1':-1}, 
               {'q1':1,'q2':-1},
               {'qqq33':-1,'qwe445':-1}]
        for item in list_:
            assert str2dict(str(dict2sympy(item))) == item

    @raises(ValueError)
    def test_complex_e1(self):
        dict2sympy({'q1':2})

    @raises(ValueError)
    def test_complex_e2(self):
        dict2sympy({'q1':2,'q2':-1})


    @raises(ValueError)
    def test_complex_e3(self):
        dict2sympy({'q1q':1})


class Test_Momenta:
    @raises(TypeError)
    def test_wrong_args_1(self):
       m=Momenta()

    @raises(TypeError)
    def test_wrong_args_2(self):
       m=Momenta(qw='wq')

    @raises(TypeError)
    def test_wrong_args_3(self):
       m=Momenta(string='wq', dict={})

    @raises(TypeError)
    def test_wrong_args_4(self):
       m=Momenta("q1")

    def test_init_string_zero_1(self):
       m=Momenta(string="")
       assert m.string==""
       assert m.dict == {}
       assert m.sympy == 0

    def test_init_string_zero_2(self):
       m=Momenta(string="0")
       assert m.string==""
       assert m.dict == {}
       assert m.sympy == 0


    def test_init_string_1(self):
       m=Momenta(string="q1+q2")
       assert m.string=="q1+q2"
       assert m.dict == {'q1':1,'q2':1}
       sympy.var('q1 q2')
       assert m.sympy == q1+q2

    def test_init_string_2(self):
       m=Momenta(string="-q1+q2")
       assert m.string=="-q1+q2"
       assert m.dict == {'q1':-1,'q2':1}
       sympy.var('q1 q2')
       assert m.sympy == -q1+q2

    @raises(ValueError)
    def test_init_string_e1(self):
       m=Momenta(string="q2q")

    @raises(ValueError)
    def test_init_string_e2(self):
       m=Momenta(string="q2+2*q3")

    def test_init_dict_zero(self):
       m=Momenta(dict={})
       assert m.string==""
       assert m.dict == {}
       assert m.sympy == 0


    def test_init_dict_1(self):
       m=Momenta(dict={"q1":1,"q2":1})
       assert m.string=="+q1+q2"
       assert m.dict == {'q1':1,'q2':1}
       sympy.var('q1 q2')
       assert m.sympy == q1+q2

    def test_init_dict_2(self):
       m=Momenta(dict={'q1':-1,'q2':1})
       assert m.string=="-q1+q2"
       assert m.dict == {'q1':-1,'q2':1}
       sympy.var('q1 q2')
       assert m.sympy == -q1+q2

    @raises(ValueError)
    def test_init_dict_e1(self):
       m=Momenta(dict={"q2q":1})

    @raises(ValueError)
    def test_init_dict_e2(self):
       m=Momenta(dict={"q2":1,"q3":2})
    

