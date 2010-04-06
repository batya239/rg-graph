#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Feb 19, 2010

@author: 
'''
import swiginac

import sympy
from sympy.printing.repr import ReprPrinter
from sympy.printing.str import StrPrinter
from sympy.printing.precedence import precedence, PRECEDENCE
from sympy.core.basic import S

import re as regex

# A list of classes that should be printed using StrPrinter
STRPRINT = ("Add", "Infinity", "Integer", "Mul", "NegativeInfinity",
            "NegativeOne", "One", "Zero")

class GinacPrinter(ReprPrinter, StrPrinter):
    """A printer which converts an expression into its Ginac interpretation."""

    def __init__(self):
        ReprPrinter.__init__(self)
        StrPrinter.__init__(self)
        self.symbols = []
        self.functions = []

        # Create print methods for classes that should use StrPrinter instead
        # of ReprPrinter.
        for name in STRPRINT:
            f_name = "_print_%s"%name
            f = getattr(StrPrinter, f_name)
            setattr(GinacPrinter, f_name, f)

    def _print_Function(self, expr):
        func = expr.func.__name__
        if not hasattr(sympy, func) and not func in self.functions:
            self.functions.append(func)
        return StrPrinter._print_Function(self, expr)

    # procedure (!) for defining symbols which have be defined in print_ginac()
    def _print_Symbol(self, expr):
        symbol = self._str(expr)
        if symbol not in self.symbols:
            self.symbols.append(symbol)
        return StrPrinter._print_Symbol(self, expr)

    def _print_module(self, expr):
        raise Exception('Modules in the expression are unacceptable')

    def _print_Pow(self, expr):
        PREC = precedence(expr)
        if expr.exp is S.NegativeOne:
            return '1/%s'%(self.parenthesize(expr.base, PREC))
        else:
            return 'pow(%s,%s)'%(self.parenthesize(expr.base, PREC),
                             self.parenthesize(expr.exp, PREC))

    def _print_Real(self, expr):
        return str(expr)

def ginac(expr):
    """Return Ginac interpretation of passed expression
    """

    printer = GinacPrinter()
    expr = printer.doprint(expr)

    result = ''
    # Returning found symbols and functions
#    for symbol in printer.symbols:
#        result +=' symbol '+symbol+'(\"' + symbol + '\");\n'
#    for function in printer.functions:
#        result += function + ' = Function(\'' + function + '\')\n'

    result += 'ex f = ' + printer._str(expr) +';'
    return result

def print_ginac(expr):
    """Print output of ginac() function"""
    print ginac(expr)
    
def Swiginac(expr):
    """Return Ginac interpretation for swiginac of passed expression
    """

    printer = GinacPrinter()
    expr = printer.doprint(expr)

    result = ''
    # Returning found symbols and functions
    for symbol in printer.symbols:
        result +=symbol + ' = swiginac.symbol'+'(\"' + symbol + '\")\n'
#    for function in printer.functions:
#        result += function + ' = Function(\'' + function + '\')\n'

    result += 'swiginac_expr = ' + printer._str(expr) 
    return result

def print_swiginac(expr):
    """Print output of swiginac() function"""
    print Swiginac(expr)   

def sympy2swiginacFactorized(expr_f,expr_o):
    str = Swiginac(expr_f*expr_o)
    g_vars = dict()
    for idx in str.split("\n"):
        reg = regex.match("^([a-zA-Z].*) = swiginac.symbol", idx)
        if reg:
            exec(idx)
            g_vars[reg.groups()[0]] = eval(reg.groups()[0])

    str_f = Swiginac(expr_f)
    for idx in str_f.split("\n"):
        reg = regex.match("^([a-zA-Z].*) = swiginac.symbol", idx)
        if not reg:
            idx = idx.replace('log','swiginac.log').replace('pi','swiginac.Pi')
            exec(idx)
    out_f = swiginac_expr

    str_o = Swiginac(expr_o)
    for idx in str_o.split("\n"):
        reg = regex.match("^([a-zA-Z].*) = swiginac.symbol", idx)
        if not reg:
            idx = idx.replace('log','swiginac.log').replace('pi','swiginac.Pi')
            exec(idx)
    out_o = swiginac_expr
    
    return (out_f, out_o, g_vars)
    
def sympy2swiginac(expr):
    str = Swiginac(expr)
    g_vars = dict()
    for idx in str.split("\n"):
        reg = regex.match("^([a-zA-Z].*) = swiginac.symbol", idx)
        if reg:
            exec(idx)
            g_vars[reg.groups()[0]] = eval(reg.groups()[0])
        else:
            exec(idx)
    return (swiginac_expr, g_vars)

def GetVarsAsStr(sympy_expr):
    import re
    atoms = sympy_expr.atoms()
    atom_set = set([])
    for atom in atoms:
        
        reg = re.match("^[a-zA-Z]",str(atom))
        if reg :
            atom_set = atom_set | set([str(atom),])
#        reg = re.match("^(.+)x(.+)$",str(atom))
#        if reg :
#            atom_set = atom_set | set(reg.groups()) 
    return atom_set
        
