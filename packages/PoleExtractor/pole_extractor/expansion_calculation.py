__author__ = 'gleb'

import subprocess
import polynomial
import copy
import itertools
import math


class EpsExpansion:
    """
    Parent class for numerous epsilon expansions used in this program.
    self.expansion is dict: eps power -> coefficient
    """

    def __init__(self, expansion=None):
        if expansion is None:
            self.expansion = dict()
        elif isinstance(expansion, dict):
            self.expansion = copy.deepcopy(expansion)

    def keys(self):
        return self.expansion.keys()

    def mul_by_eps_in(self, deg):
        new_exp = dict()
        for k in self.keys():
            new_exp[k + deg] = copy.deepcopy(self.expansion.pop(k))
        self.expansion = copy.deepcopy(new_exp)

    def to_dict(self):
        return self.expansion

    def __getitem__(self, item):
        return self.expansion[item]

    def __setitem__(self, key, value):
        self.expansion[key] = copy.deepcopy(value)


class PolyEpsExpansion(EpsExpansion):
    def __add__(self, other):
        result = copy.deepcopy(self)
        for k in other.keys():
            if k in result.keys():
                result.expansion[k] += other.expansion[k]
            else:
                result[k] = other[k]
        return result


#class LogEpsExpansion(EpsExpansion):


class NumEpsExpansion(EpsExpansion):
    def __add__(self, other):
        result = copy.deepcopy(self)
        for k in other.keys():
            if k in result.keys():
                result[k] = map(lambda x: x[0] + x[1], zip(result[k], other[k]))
            else:
                result[k] = other[k]
        return result

    def __mul__(self, other):
        result = NumEpsExpansion()
        for k1 in self.keys():
            for k2 in other.keys():
                if k1 + k2 not in result.keys():
                    result[k1 + k2] = [0.0, 0.0]

                result[k1 + k2][0] += self[k1][0] * other[k2][0]
                result[k1 + k2][1] += self[k1][1] * other[k2][1] + self[k1][1] * other[k2][0] \
                    + self[k1][0] * other[k2][1]
        border_element = min(max(self.keys()) + min(other.keys()), max(other.keys()) + min(self.keys()))
        l = result.keys()
        for k in l:
            if k > border_element:
                result.expansion.pop(k)
        return result

    def merge(self, other):
        """
        Unites 2 numeric expansions in one, always choosing result with lesser error.
        """
        for k in other.keys():
            if k in self.keys():
                if other[k][1] < self[k][1]:
                    del self[k][:]
                    self[k] = other[k]
            else:
                self[k] = other[k]

    def principal_part(self):
        keys = self.keys()
        for k in keys:
            if k >= 0:
                self.expansion.pop(k)

    def stretch(self, coef):
        """
        stretches expansion variable, e.g. makes from expansion
        sum_n c_n * x^n
        expansion
        sum_n c_n * coef^n * x^n
        """
        for k in self.keys():
            self[k][0] *= coef ** k
            self[k][1] *= coef ** k


def ac_principal_part(polyprod, pole_var, var_degree_a, var_degree_b):
    """
    part of analytical continuation function. returns 1st of 3 parts of resulting eps expansion.
    """
    #TODO: tests tests tests
    result = dict()

    PList1 = [copy.deepcopy(polyprod), ]
    PList2 = []

    for _ in itertools.repeat(None, -var_degree_a - 1):
        for P in PList1:
            PList2 = PList2 + P.diff(pole_var)
        del PList1[:]
        PList1 = copy.deepcopy(PList2)
        del PList2[:]

    for i in list(xrange(0, len(PList1))):
        PList1[i] = PList1[i].set0toVar(pole_var)
        coefficient = polynomial.poly([(1, []), ], degree=1)
        coefficient.c *= (math.factorial(-1 - var_degree_a) ** (-1))
        coefficient.c *= (var_degree_b ** (-1))
        PList1[i] *= coefficient.toPolyProd()

    result[-1] = copy.deepcopy(PList1)

    return result


def ac_expansion_part(polyprod, pole_var, var_degree_a, var_degree_b, toIndex):
    """
    part of analytical continuation function. returns 2nd of 3 parts of resulting eps expansion.
    """
    #TODO: tests tests tests
    #    if var_degree_a > -2:
    #        continue
    result = dict()

    if var_degree_a > -2:
        result[0] = []
        return result

    for k in list(xrange(0, toIndex + 1)):
        coef_1 = ((-var_degree_b) ** k)
        PList1 = [copy.deepcopy(polyprod), ]
        PList2 = []

        if not k in result.keys():
            result[k] = []

        for i in list(xrange(0, -var_degree_a - 1)):
            coef_2 = (math.factorial(i) * (i + var_degree_a + 1) ** (k + 1)) ** (-1)
            for j in list(xrange(0, len(PList1))):
                P = copy.deepcopy(PList1[j])
                P = P.set0toVar(pole_var)
                coefficient = polynomial.poly([(1, []), ], degree=1)
                coefficient.c *= coef_1 * coef_2
                P *= coefficient.toPolyProd()
                result[k].append(copy.deepcopy(P))

            for P in PList1:
                PList2 = PList2 + P.diff(pole_var)

            del PList1[:]
            PList1 = copy.deepcopy(PList2)
            del PList2[:]

    return result


def ac_stretched_part(polyprod, pole_var, var_degree_a, var_degree_b):
    """
    part of analytical continuation function. returns 3rd of 3 parts of resulting eps expansion.
    """
    #TODO: tests tests tests

    result = dict()
    stretcher = 'a' + str(pole_var)
    PList1 = [copy.deepcopy(polyprod.stretch(stretcher, [pole_var, ])), ]
    PList2 = []

    for _ in itertools.repeat(None, -var_degree_a):
        for P in PList1:
            PList2 = PList2 + P.diff(stretcher)
        del PList1[:]
        PList1 = copy.deepcopy(PList2)
        del PList2[:]

    if var_degree_a <= -2:
        stretch_factor = polynomial.poly([(1, []), (-1, [stretcher, ])], degree=(-var_degree_a - 1, 0))
        PList1 = map(lambda x: x * stretch_factor, PList1)

    p = polynomial.poly([(1, [pole_var, ]), ], degree=(var_degree_a, var_degree_b))
    PList1 = map(lambda x: x * p.toPolyProd(), PList1)

    result[0] = copy.deepcopy(PList1)
    return result


def analytical_continuation(polyprod, pole_var, var_degree_a, var_degree_b, toIndex):
    result = dict()

    res1 = ac_principal_part(polyprod, pole_var, var_degree_a, var_degree_b)
    res2 = ac_expansion_part(polyprod, pole_var, var_degree_a, var_degree_b, toIndex)
    res3 = ac_stretched_part(polyprod, pole_var, var_degree_a, var_degree_b)

    all_keys = set(res1.keys() + res2.keys() + res3.keys())

    for k in list(all_keys):
        result[k] = []
        if k in res1.keys():
            result[k] += res1[k]
        if k in res2.keys():
            result[k] += res2[k]
        if k in res3.keys():
            result[k] += res3[k]
    return result


def remove_principal_part(poly_prod):
    """
    Removes a factorised pole from poly_prod if there is one and returns pole and poly_prod without it separately.
    """
    #TODO: tests tests tests
    def stretched(poly, var_index):
        str_name = 'a' + str(var_index)
        if str_name in poly.getVarsIndexes():
            return True
        else:
            return False

    for poly in poly_prod.polynomials:
        if poly.degree.a <= -1 and len(poly.monomials) == 1 and not len(poly.getVarsIndexes()) == 0:
            pole_var = list(poly.getVarsIndexes())[0]

            if not stretched(poly_prod, pole_var):
                result_poly = copy.deepcopy(poly_prod)
                coefficient = polynomial.poly([(1, []), ], degree=1)
                coefficient.c = poly.c
                result_poly.polynomials.remove(poly)
                result_poly *= coefficient
                return [result_poly, poly]

    return []


def extract_eps_poles(polypr, toIndex):
    """
    returns dictionary eps degree -> polynomial product list
    every polynomial product list represents a sum
    :param polypr:
    :param toIndex:
    """

    old_expansion = dict()
    new_expansion = dict()
    old_expansion[0] = [polypr, ]
    need_another_go = False

    while True:
        for k in old_expansion.keys():
            need_another_go = False

            for i in list(xrange(0, len(old_expansion[k]))):
                old_expansion[k][i] = old_expansion[k][i].simplify()

            for current_poly_prod in old_expansion[k]:
                check_result = remove_principal_part(current_poly_prod)
                found_pole = (0 != len(check_result))

                if found_pole:
                    need_another_go = True
                    P1 = check_result[0]
                    poly = check_result[1]
                    pole_var = list(poly.getVarsIndexes())[0]

                    cont = analytical_continuation(P1, pole_var, poly.degree.a, poly.degree.b, toIndex)
                    for k1 in cont.keys():
                        if k + k1 in new_expansion.keys() and k + k1 <= toIndex:
                            new_expansion[k + k1] += copy.deepcopy(cont[k1])
                        else:
                            new_expansion[k + k1] = copy.deepcopy(cont[k1])
                else:
                    if k not in new_expansion.keys():
                        new_expansion[k] = []
                    new_expansion[k].append(copy.deepcopy(current_poly_prod))
        if not need_another_go:
            new_expansion.clear()
            break
        else:
            old_expansion.clear()
            old_expansion = copy.deepcopy(new_expansion)
            new_expansion.clear()

    for i in list(xrange(min(old_expansion.keys()), toIndex + 1)):
        new_expansion[i] = []

    refactored_exp = dict()
    for k in sorted(old_expansion.keys()):
        for current_poly_prod in old_expansion[k]:
            exp = current_poly_prod.epsExpansion(toIndex - k)

            for k2 in exp[1].keys():
                exp[1][k2] = filter(lambda a: a.c != 0, exp[1][k2])
                if len(exp[1][k2]) != 0:
                    refactored_exp[k2] = [exp[0], exp[1][k2]]

            for k2 in refactored_exp.keys():
                if k + k2 in new_expansion.keys():
                    new_expansion[k + k2].append(refactored_exp[k2])

            refactored_exp.clear()

    old_expansion.clear()
    old_expansion = copy.deepcopy(new_expansion)
    new_expansion.clear()

    for k in old_expansion.keys():
        if len(old_expansion[k]) == 0:
            old_expansion.pop(k, None)

    return old_expansion


def str_for_CUBA(expansion):
    result = '#ifndef INTEGRATE_H_' + '\n' + '#define INTEGRATE_H_' + '\n' + '#define NDIM '
    used_vars = set()
    for element in expansion:
        used_vars = used_vars.union(element[0].getVarsIndexes())
        for logarithm in element[1]:
            used_vars = used_vars.union(logarithm.polynomialProduct.getVarsIndexes())
    result += str(len(used_vars)) + '\n'
    result += 'static int Integrand(const int *ndim, const double xx[], const int *ncomp, double ff[], void *userdata)'
    result += '\n' + '{' + '\n'
    for v_num, v in enumerate(list(used_vars)):
        if isinstance(v, int):
            result += '#define u' + str(v) + ' xx[' + str(v_num) + ']' + '\n'
        else:
            result += '#define ' + str(v) + ' xx[' + str(v_num) + ']' + '\n'
    result += '#define f ff[0]' + '\n' + '\n' + 'f = '

    for element in expansion:
        for logarithm in element[1]:
            result += polynomial.formatter.format(logarithm, polynomial.formatter.CPP)
            result += ' * '
            result += polynomial.formatter.format(element[0], polynomial.formatter.CPP)
            result += ' + '

    result = result[:-3] + ';' + '\n' + '\n'
    result = result + 'return 0;' + '\n' + '}' + '\n' + '#endif /*INTEGRATE_H_*/'
    return result


def compute_exp_via_CUBA(expansion):
    """
    So for now in order for everything to work properly you have to have files integrate.c and integrate.h
    in the folder where the script you are calling this func from is. I will fix it later, honestly.
    """
    #TODO: fix the fast_nickel call, this is bs
    result = dict()
    for k in expansion.keys():
        header_str = str_for_CUBA(expansion[k])
        f = open('integrate.h', 'w')
        f.write(header_str)
        f.close()
        mc_integral = subprocess.Popen(['./run_integration.sh'], shell=True,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)

        out, err = mc_integral.communicate()
        m = out.split(' ', 2)
        result[k] = [0.0, 0.0]
        try:
            result[k][0] = float(m[0])
            result[k][1] = float(m[1])
        except ValueError:
            print 'Something went wrong during integration. Here\'s what CUBA said:'
            print str(out)

    return result