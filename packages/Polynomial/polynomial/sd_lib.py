#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'

import polynomial


def sectorPoly(poly, sec):
    if isinstance(poly, list):
        return map(lambda x: sectorPoly_(x, sec), poly)
    else:
        return sectorPoly_(poly, sec)


def sectorPoly_(poly, sec):
    """
    This functions performs variable transformation of polynomial poly
    according to sector nomenclature sec.
    """
    for (main_var, other_vars) in sec:
        poly = poly.stretch(main_var, other_vars)
    return poly


def check_delta(delta_arg, sec):
    """
    Checks if delta_args consistent with sec[0]
    sec[0] decomposition space must be equal to set of delta_args variables.
    delta_args must be == \sum_i u_i i=...
    """
    if delta_arg is None:
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

        return first_sector_set == arg_set


def sectorDiagram(expr_, sec, delta_arg=None, remove_delta=True):
    """
    This functions performs variable transformation of a whole diagram according to sector nomenclature sec.
    Where polynomial poly being an integration element of diagram without the delta-function
    and d_arg being the delta-function argument ,
    If (delta_arg<>None and remove_delta) , first decomposition is considered primary.
    """

    if not isinstance(expr_, list):
        expr = [expr_]
    else:
        expr = expr_


    if remove_delta and not check_delta(delta_arg, sec):
        raise ValueError, 'Invalid delta functions arguments'

    result = [expr, delta_arg if delta_arg is not None else polynomial.poly([])]

    #
    #    we can perform all sector transformations without removing delta function (if present),
    #    and remove delta only at last step (of course if primary decomposition in sector
    #    is consistent with delta function argument (d_arg))
    #

    result = map(lambda x: sectorPoly(x, sec), result)

    #
    #    Now we should add jacobian of performed variables transformations
    #

    for (main_var, other_vars) in sec:
        m = [main_var] * len(other_vars)
        jacobian = polynomial.poly([(1, m)], degree=(1, 0))
        result[0] = map(lambda x: x * jacobian.toPolyProd(), result[0])

    if remove_delta:
        if delta_arg is None:
            raise ValueError, "Can't remove delta: no delta_arg provided"

        #
        # substitution - transformed argument of delta function
        #
        substitution = result[1]
        deltaMultiplier = polynomial.poly([(1, [sec[0][0]])], degree=(1, 0))
        #
        # additional multiplier from delta function delta(Lx-1)=1/L delta(x-1/L) = x delta(x-1/L)
        #
        result[0] = map(lambda x: x * deltaMultiplier.toPolyProd(), result[0])
        primaryVar = sec[0][0]

        #
        # Now we remove delta function by replacing primaryVar to substitution.set1toVar(primaryVar)**(-1)
        # after decomposition primaryVar must be factorized and result[0]~ primaryVar**a*f(doesn't depend
        # on primaryVar)
        # If we have nontrivial primaryVar dependence like (u1+u2)**a than smth goes wrong and we got exception
        #
        # Removal of delta function performed in two stages. At first one for each factorized primaryVar we add
        # multiplier substitution.set1toVar(primaryVar)**(-1), on the second we set primaryVar = 1
        #
        result0_ = list()
        for expr in result[0]:
            multiplier = substitution.set1toVar(primaryVar)
            primaryVarDegree = expr.calcPower(primaryVar)
            multiplier = multiplier.changeDegree(-primaryVarDegree)
            expr = expr * multiplier.toPolyProd() * polynomial.poly([(1, [primaryVar])],
                                                                    degree=-primaryVarDegree).toPolyProd()

            # (second stage)
            expr = expr.set1toVar(primaryVar)
            result0_.append(expr)

        result[0] = result0_

#        result[0] = result[0].simplify()
        result[1] = None
    else:
#        result[0] = result[0].simplify()
        if delta_arg is None:
            result[1] = None
    return result


