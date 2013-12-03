__author__ = 'gleb'

import polynomial
import subprocess
import os
from sympy import mpmath
import reduced_vl
import itertools


class NumEpsExpansion():
    """
    Class representing Laurent eps-series.
    """

    def __init__(self, exp=None):
        """
        """
        if exp is None:
            self._elements = dict()
            return

        if not type(exp) == dict:
            raise ValueError('Your argument is bad and you should feel bad.')
        if not all(map(lambda x: len(x) == 2, exp.values())):
            raise ValueError('Your argument is bad and you should feel bad.')

        self._elements = dict()
        for k in exp.keys():
            self._elements[k] = tuple(exp[k])

    def keys(self):
        return self._elements.keys()

    def cut(self, toIndex):
        n_elements = dict()
        for k in self.keys():
            if k <= toIndex:
                n_elements[k] = self[k]
            else:
                n_elements[k] = (0.0, 0.0)
        return NumEpsExpansion(n_elements)

    @staticmethod
    def gammaCoefficient(rvl, theory, max_index):
        assert(isinstance(rvl, reduced_vl.ReducedVacuumLoop))
        if 3 == theory:
            deg = -3
        else:
            deg = -2
        g11 = sum(rvl.edges_weights()) + deg * rvl.loops()
        g12 = rvl.loops()
        d = rvl.loops()
        g21 = -deg
        g22 = -1

        g_coef_1 = get_gamma(g11, g12, max_index)
        g_coef_2 = get_gamma(g21, g22, max_index)
        for _ in itertools.repeat(None, d - 1):
            g_coef_2 *= get_gamma(g21, g22, max_index)
        return g_coef_2 * g_coef_1

    @staticmethod
    def unite(e1, e2):
        assert(isinstance(e1, NumEpsExpansion))
        assert(isinstance(e2, NumEpsExpansion))
        result_base = dict()
        for k in list(set(e1.keys() + e2.keys())):
            if k not in e1.keys():
                result_base[k] = e2[k]
            elif k not in e2.keys():
                result_base[k] = e1[k]
            else:
                if e1[k][1] < e2[k][1]:
                    result_base[k] = e1[k]
                else:
                    result_base[k] = e2[k]
        return NumEpsExpansion(exp=result_base)

    def __getitem__(self, item):
        return self._elements[item]

    def __mul__(self, other):
        if isinstance(other, NumEpsExpansion):
            if self.keys() and other.keys():
                ks = range(min(self.keys()) + min(other.keys()),
                           1 + min(min(self.keys()) + max(other.keys()), max(self.keys()) + min(other.keys())))
            else:
                raise AttributeError("Don't try to multiply by an empty expansion.")
            res = dict((k, [0.0, 0.0]) for k in ks)

            for k1 in self.keys():
                for k2 in other.keys():
                    if k1 + k2 in ks:
                        res[k1 + k2][0] += self[k1][0] * other[k2][0]
                        res[k1 + k2][1] += abs(self[k1][1] * other[k2][0])
                        res[k1 + k2][1] += abs(self[k1][0] * other[k2][1])
                        res[k1 + k2][1] += abs(self[k1][1] * other[k2][1])
        elif isinstance(other, float):
            res = dict()
            for k in self.keys():
                res[k] = (self[k][0] * other, self[k][1] * abs(other))
        else:
            raise AttributeError('Can only multiply by float or other expansion')

        return NumEpsExpansion(res)

    def __add__(self, other):
        if self.keys() and other.keys():
            ks = range(min(self.keys() + other.keys()), 1 + min(max(self.keys()), max(other.keys())))
        elif not self.keys() and not other.keys():
            raise AttributeError("Don't try to add 2 empty expansions.")
        elif self.keys():
            return NumEpsExpansion(self._elements)
        elif other.keys():
            return NumEpsExpansion(other._elements)

        res = dict((k, [0.0, 0.0]) for k in ks)
        for k in ks:
            if k in self.keys():
                res[k][0] += self[k][0]
                res[k][1] += self[k][1]
            if k in other.keys():
                res[k][0] += other[k][0]
                res[k][1] += other[k][1]

        return NumEpsExpansion(res)

    def __pow__(self, power, modulo=None):
        if not isinstance(power, int) or int < 1:
            raise AttributeError("Sorry, we can't get non-natural powers")
        result = NumEpsExpansion(self._elements)
        for k in range(power - 1):
            result = result * self
        return result

    def __str__(self):
        result = ''
        for k in sorted(self.keys()):
            result += 'eps^(' + str(k) + ')[' + str(self[k][0]) + '+-' + str(self[k][1]) + '] + '
        return result[:-2]

    def __repr__(self):
        return str(self)


def get_gamma(a, b, max_index):
    """
    Returns coefficients of Laurent series of Gamma(a + bx), x->0
    """
    result = dict()
    if a > 0:
        mpmath.mp.dps = 20
        expansion = list(mpmath.taylor(mpmath.gamma, a, max_index))
        for i in list(xrange(0, len(expansion))):
            result[i] = [float(expansion[i]), 1E-10]
    elif 0 == a:
        result = {0: [-0.5772156649, 1E-10],
                  -1: [1.0000000000, 1E-10],
                  1: [0.9890559953, 1E-10],
                  2: [-0.9074790760, 1E-10],
                  3: [0.9817280868, 1E-10],
                  4: [-0.9819950689, 1E-10],
                  5: [0.9931491146, 1E-10],
                  6: [-0.9960017604, 1E-10],
                  7: [0.9981056937, 1E-10],
                  8: [-0.9990252676, 1E-10],
                  9: [0.9995156560, 1E-10],
                  10: [-0.9997565975, 1E-10]}
    elif -1 == a:
        result = {0: [-0.4227843350, 1E-10],
                  -1: [-1.0000000000, 1E-10],
                  1: [-1.4118403304, 1E-10],
                  2: [-0.5043612543, 1E-10],
                  3: [-1.4860893411, 1E-10],
                  4: [-0.5040942722, 1E-10],
                  5: [-1.4972433868, 1E-10],
                  6: [-0.5012416264, 1E-10],
                  7: [-1.4993473202, 1E-10],
                  8: [-0.5003220526, 1E-10],
                  9: [-1.4998377086, 1E-10],
                  10: [-0.5000811111, 1E-10]}
    elif -2 == a:
        result = {0: [0.4613921675, 1E-10],
                  -1: [0.5000000000, 1E-10],
                  1: [0.9366162489, 1E-10],
                  2: [0.7204887516, 1E-10],
                  3: [1.1032890464, 1E-10],
                  4: [0.8036916593, 1E-10],
                  5: [1.1504675231, 1E-10],
                  6: [0.8258545747, 1E-10],
                  7: [1.1626009475, 1E-10],
                  8: [0.8314615000, 1E-10],
                  9: [1.1656496043, 1E-10],
                  10: [0.8328653577, 1E-10]}
    elif -3 == a:
        result = {0: [-0.2093529447, 1E-10],
                  -1: [-0.1666666666, 1E-10],
                  1: [-0.3819897312, 1E-10],
                  2: [-0.3674928276, 1E-10],
                  3: [-0.4902606246, 1E-10],
                  4: [-0.4313174280, 1E-10],
                  5: [-0.5272616503, 1E-10],
                  6: [-0.4510387417, 1E-10],
                  7: [-0.5378798964, 1E-10],
                  8: [-0.4564471321, 1E-10],
                  9: [-0.5406989121, 1E-10],
                  10: [-0.4578547566, 1E-10]}

    ks = result.keys()
    for k in ks:
        if k > max_index:
            del result[k]
        else:
            result[k][0] *= b ** k
            result[k][1] *= abs(b ** k)

    return NumEpsExpansion(result)


def str_for_cuba(expansion):
    result = '#ifndef INTEGRATE_H_' + '\n' + '#define INTEGRATE_H_' + '\n' + '#define NDIM '
    used_vars = set()
    for element in expansion:
        used_vars = used_vars.union(element[0].getVarsIndexes())
        for logarithm in element[1]:
            used_vars = used_vars.union(logarithm.polynomialProduct.getVarsIndexes())
    if len(used_vars) == 0:
        used_vars.add(1)
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
    result = result + 'return 0;' + '\n' + '}' + '\n' + '#endif /*INTEGRATE_H_*/' + '\n'
    return result


def cuba_calculate(expansion):
    """
    :param expansion:
    :return:
    """
    result = dict()
    split_size = 2
    wd = os.path.expanduser("~") + '/.pole_extractor'
    source = wd + '/' + 'integrate.c'
    header = wd + '/' + 'integrate.h'
    binary = wd + '/' + 'integrate'

    for k in expansion.keys():
        for i in range(0, len(expansion[k]), split_size):
            f = open(header, 'w')
            header_str = str_for_cuba(expansion[k][i:i + split_size])
            f.write(header_str)
            f.close()

            #compiling external C program
            command = 'gcc -Wall -fopenmp -I' + wd + ' -o ' + binary + ' ' + source + ' -lm -lcuba -fopenmp'
            subprocess.Popen([command], shell=True, stderr=subprocess.PIPE).communicate()

            #running external C program
            integrate = subprocess.Popen([binary], env={'OMP_NUM_THREADS': '4', 'CUBAVERBOSE': '0'},
                                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            out, err = integrate.communicate()
            m = out.split(' ', 2)
            try:
                r = float(m[0])
                e = float(m[1])
                if k in result.keys():
                    result[k][0] += r
                    result[k][1] += e
                else:
                    result[k] = [r, e]
            except ValueError:
                print 'Something went wrong during integration. Here\'s what CUBA said:'
                print str(out)
                print str(err)

            os.remove(binary)
            os.remove(header)

    return NumEpsExpansion(result)