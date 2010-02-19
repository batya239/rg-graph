#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Feb 19, 2010

@author: 
'''


import sympy
from sympy.printing.repr import ReprPrinter
from sympy.printing.str import StrPrinter
from sympy.printing.precedence import precedence, PRECEDENCE
from sympy.core.basic import S


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