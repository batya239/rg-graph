#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dimas'

import collections
import rggraphutil
import polynomial
import multiindex
import eps_number
import copy
import polynomial_product
import math
import formatter


LogarithmAndPolyProd = collections.namedtuple("LogarithmAndPolyProd", ["poly_prod", "log"])


VarInfo = collections.namedtuple("VarInfo", ["var_index", "a", "b"])


def _create_var_info(var_index, eps_number):
    return VarInfo(var_index, -eps_number.a, eps_number.b)


def extract_poles_and_eps_series(poly_prod, order):
    """
    order - includes
    """
    _result = rggraphutil.emptyListDict()
    raw_eps_dict = _extract_poles(poly_prod, order)
    for o, raw_res in raw_eps_dict.iteritems():
        to_index = order - o
        for raw_pp in raw_res:
            expansion = raw_pp.epsExpansion(to_index + 1)
            if expansion is not None:
                main_expansion = expansion.main_expansion
                for o1, raw_res1 in main_expansion.iteritems():
                    sum_order = o + o1
                    if sum_order <= order:
                        _result[sum_order].append((expansion.factor, raw_res1))
    result = dict()
    for o, vs in _result.iteritems():
        flatten_values = []
        result[o] = flatten_values
        for f, _vs in vs:
            for v in _vs:
                flatten_values.append(LogarithmAndPolyProd(f, v))
    return result


def _extract_poles(poly_prod, order):
    """
    order - includes
    """
    pole_parameters = list()
    for p in poly_prod.polynomials:
        if len(p.monomials) == 1:
            m = p.monomials.items()[0]
            multi_index = m[0].vars.items()[0]
            var_name = multi_index[0]
            mi = multi_index[1] * p.degree
            if mi.a < 0:
                c = p.c * (m[1] ** p.degree) if p.degree.isRealNumber() else p.c * m[1]
                pole_parameters.append((_create_var_info(var_name, mi), p, c))
    result = {0: [poly_prod]}
    _order = order + len(pole_parameters) + 1
    for param in pole_parameters:
        current_result = rggraphutil.emptyListDict()
        for o, poly_prods in result.iteritems():
            for _poly_prod in poly_prods:
                npp = polynomial_product.PolynomialProduct(filter(lambda p: p != param[1], _poly_prod.polynomials)) * param[2]
                current_result[o - 1] += _pole_part(npp, param[0])
                _update_dict_with_other(current_result, _ac_part(npp, param[0], _order), o)
                current_result[0] += tail_part(npp, param[0])
        result = current_result
    return result


def _pole_part(poly_prod, var_info):
    a_ = var_info.a - 1
    index = var_info.var_index
    coefficient = (var_info.b * math.factorial(a_)) ** (-1)
    diff = map(lambda _pp: _pp.set0toVar(index) * coefficient, poly_prod.diff(index, a_))
    return diff


def _ac_part(poly_prod, var_info, order):
    """
    @param order - excluded
    """
    a_ = var_info.a - 2
    if a_ <= 0:
        return dict()

    b_factor = 1
    diff_cache = rggraphutil.emptyListDict()
    eps_expansion = rggraphutil.emptyListDict()
    for i in xrange(order):
        for k in xrange(a_ + 1):
            diff = diff_cache[k] if k in diff_cache else poly_prod.diff(var_info.var_index, k)
            coeff = (b_factor * (math.factorial(k) * (k - var_info.a + 1) ** (i + 1)) ** (-1))
            diff = map(lambda d: d * coeff, diff)
            eps_expansion[i] += diff
        b_factor *= - var_info.b
    return eps_expansion


def tail_part(poly_prod, var_info):
    stretch_var_name = "t%d" % var_info.var_index
    stretched = poly_prod.stretch(stretch_var_name, (var_info.var_index,))
    stretched_diff = stretched.diff(stretch_var_name, var_info.a)
    a_ = var_info.a - 1
    main_part = \
        map(lambda _pp: _pp * _var_in_power(var_info.var_index, eps_number.epsNumber((-var_info.a, var_info.b))),
            stretched_diff)
    if a_ == 0:
        return main_part
    coeff = ((math.factorial(a_) ** (-1)) * _stretch_prefix(stretch_var_name, a_))
    return map(lambda _pp: _pp * coeff, main_part)


def _stretch_prefix(var_index, power):
    return polynomial.Polynomial({multiindex.CONST: 1, multiindex.MultiIndex({var_index: 1}): -1}, degree=power)


def _var_in_power(var_index, power):
    return polynomial.Polynomial({multiindex.MultiIndex({var_index: 1}): 1}, degree=power)


def _update_dict_with_other(some_dict, to_add, shift):
    for k, v in to_add.iteritems():
        some_dict[k + shift] += v