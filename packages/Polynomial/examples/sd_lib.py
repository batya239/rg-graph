#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'

import copy

import polynomial


def sector_poly(poly, sec):
    """
    This functions performs sector decomposition of polynomial poly
    according to sector nomenclature sec, i.e. returns polynomial after
    variable transformations corresponding to sector sec.
    """
    for (main_var, other_vars) in sec:
        poly = poly.stretch(main_var, other_vars)
    return poly


def sector_diagram(poly, sec, delta_arg=None, remove_delta=True):
    """
    This functions performs sector decomposition of a whole diagram with
    polynomial poly being an integration element without the delta-function
    and d_arg being the delta-function argument according to sector nomenclature sec,
    i.e. returns polynomials after variable transformations corresponding to sector sec.
    If delta_arg<>None, first decomposition is considered primary.
    """

    def check_delta(delta_arg, sec):
        """
        Checks if delta_args consistent with sec[0]
        sec[0] decomposition space must be equal to set of delta_args variables.
        delta_args must be == \sum_i u_i i=...
        """
        if isinstance(delta_arg, type(None)):
            return True
        else:

            if delta_arg.degree <> (1, 0):
                return False
            arg_set = set()
            for monomial in delta_arg.monomials:
                if delta_arg.monomials[monomial] <> 1:
                    return False

                monomial_vars = list(monomial.getVarsIndexes())
                if len(monomial_vars) <> 1:
                    return False
                if monomial.vars[monomial_vars[0]] <> 1:
                    return False
                if monomial_vars[0] in arg_set:
                    return False
                arg_set = arg_set | set(monomial_vars)
            first_sector_set = set(sec[0][1]) | set([sec[0][0], ])

            if first_sector_set == arg_set:
                return True
            else:
                return False

    if not check_delta(delta_arg, sec):
        raise ValueError, 'Invalid delta functions arguments'

    result = [poly, delta_arg if not isinstance(delta_arg, type(None)) else polynomial.poly([])]
    """
    we can perform all sector transformations without removing delta function (if present),
    and remove delta only at last step (of course if primary decomposition in sector
    is consistent with delta function argument (d_arg))
    """
    result = map(lambda x: sector_poly(x, sec), result)
    """
    Now we should add Jacobian of performed variables transformations
    """
    for (main_var, other_vars) in sec:
        m = [main_var] * len(other_vars)
        J = polynomial.poly([(1, m)], degree=(1, 0))
        result[0] = result[0] * J.toPolyProd()

    """
    if delta_arg <> None (we have delta function)
    """

    if remove_delta:
        J = polynomial.poly([(1, [sec[0][0]])], degree=(1, 0))
        result[0] = result[0] * J.toPolyProd()
        substitution = result[1]
        result[0] = result[0].simplify()
        primary_var = sec[0][0]
        for p in result[0].polynomials:
            if len(p.monomials) == 1:
                monomial = p.monomials.keys()[0]
                if primary_var in monomial.vars.keys():
                    multiplier = copy.deepcopy(substitution).set1toVar(primary_var)
                    multiplier.degree = -p.degree * monomial.vars[primary_var]
                    result[0] = result[0] * multiplier.toPolyProd()
            else:
                if primary_var in p.getVarsIndexes():
                    raise ValueError, "Invalid decomposition: \nexpr: %s\n polynomial: %s\nprimary var %s" % (
                        result[0], p, primary_var)

        result[0] = result[0].set1toVar(primary_var)
        result[0] = result[0].simplify()
        result[1] = None
        return result[0]
    else:
        result[0] = result[0].simplify()
        result[1] = result[1].toPolyProd()

    return result


