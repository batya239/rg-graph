__author__ = 'gleb'

import polynomial
import subprocess
import os
from sympy import mpmath
import reduced_vl
import itertools
import uncertainties
import shutil
import multiprocessing


class NumEpsExpansion():
    """
    Class representing Laurent eps-series.
    """

    def __init__(self, exp=None, precise=False):
        """
        """
        self._precise = precise
        if exp is None:
            self._elements = dict()
            return

        assert(type(exp) == dict)

        self._elements = dict()
        for k in exp.keys():
            if isinstance(exp[k], list) or isinstance(exp[k], tuple):
                #self._elements[k] = PrecisionNumber.fromTuple(exp[k])
                self._elements[k] = uncertainties.ufloat(exp[k][0], exp[k][1])
            #if isinstance(exp[k], PrecisionNumber):
            else:
                self._elements[k] = exp[k]

    def keys(self):
        return self._elements.keys()

    def cut(self, toIndex):
        n_elements = dict()
        for k in self.keys():
            if k < toIndex:
                n_elements[k] = self[k]
        return NumEpsExpansion(n_elements, precise=True)

    def __getitem__(self, item):
        assert(self._precise or item <= max(self.keys()))
        if item in self.keys():
            return self._elements[item]
        else:
            #return PrecisionNumber(value=0.0)
            return uncertainties.ufloat(0.0, 0.0)

    def __str__(self):
        result = ''
        for k in sorted(self.keys()):
            result += 'eps^(' + str(k) + ')[' + str(self[k]) + '] + '
        if not self._precise:
            result += 'O[eps]^' + str(max(self.keys()) + 1) + '   '
        return result[:-3]

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if self._precise != other._precise:
            return False
        if sorted(self.keys()) != sorted(other.keys()):
            return False
        for k in self.keys():
            if not self[k] == other[k]:
                return False
        return True

    def __add__(self, other):
        assert(isinstance(other, NumEpsExpansion))
        res = dict()
        result_precise = self._precise and other._precise
        ks = list(set(self.keys() + other.keys()))

        if result_precise:
            for k in ks:
                res[k] = self[k] + other[k]
        else:
            if self._precise:
                max_index = max(other.keys())
            elif other._precise:
                max_index = max(self.keys())
            else:
                max_index = min(max(self.keys()), max(other.keys()))

            for k in ks:
                if k <= max_index:
                    #res[k] = PrecisionNumber(value=0.0)
                    res[k] = uncertainties.ufloat(0.0, 0.0)
                    if k in self.keys():
                        res[k] += self[k]
                    if k in other.keys():
                        res[k] += other[k]
        return NumEpsExpansion(res, precise=result_precise)

    def __mul__(self, other):
        res = dict()
        if isinstance(other, float) or isinstance(other, int):
            for k in self.keys():
                res[k] = self[k] * float(other)
            return NumEpsExpansion(res, precise=self._precise)
        elif isinstance(other, NumEpsExpansion):
            result_precise = self._precise and other._precise
            if result_precise:
                for k1 in self.keys():
                    for k2 in other.keys():
                        if k1 + k2 not in res.keys():
                            #res[k1 + k2] = PrecisionNumber(value=0)
                            res[k1 + k2] = uncertainties.ufloat(0.0, 0.0)
                        res[k1 + k2] += self[k1] * other[k2]
            else:
                if self._precise:
                    length = max(other.keys()) - min(other.keys()) + 1
                elif other._precise:
                    length = max(self.keys()) - min(self.keys()) + 1
                else:
                    length = min(max(self.keys()) - min(self.keys()), max(other.keys()) - min(other.keys())) + 1
                ks = range(min(self.keys()) + min(other.keys()), min(self.keys()) + min(other.keys()) + length)
                #res = {k: PrecisionNumber(value=0) for k in ks}
                res = {k: uncertainties.ufloat(0.0, 0.0) for k in ks}
                for k1 in self.keys():
                    for k2 in other.keys():
                        if k1 + k2 in res.keys():
                            res[k1 + k2] += self[k1] * other[k2]
            return NumEpsExpansion(res, precise=result_precise)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __pow__(self, power, modulo=None):
        if not isinstance(power, int) or int < 1:
            raise AttributeError("Sorry, we can't get non-natural powers")
        result = NumEpsExpansion(self._elements, precise=self._precise)
        for k in range(power - 1):
            result = result * self
        return result

    @staticmethod
    def gammaCoefficient(rvl, theory, max_index):
        assert(isinstance(rvl, reduced_vl.ReducedVacuumLoop))
        if 3 == theory:
            deg = -3
        else:
            deg = -2
        g11 = sum(rvl.edges_weights()) + deg * rvl.loops()
        if not rvl.zero_momenta():
            g11 += 1
        g12 = rvl.loops()
        d = rvl.loops()
        g21 = -deg
        g22 = -1

        g_coef_1 = get_gamma(g11, g12, max_index)
        g_coef_2 = get_gamma(g21, g22, max_index)
        for _ in itertools.repeat(None, d - 1):
            g_coef_2 *= get_gamma(g21, g22, max_index)

        if not rvl.zero_momenta():
            g_coef_1 *= -1.0
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
                if e1[k].std_dev < e2[k].std_dev:
                    result_base[k] = e1[k]
                else:
                    result_base[k] = e2[k]
        return NumEpsExpansion(exp=result_base)


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
            cmpl = 'gcc -Wall -fopenmp -I' + wd + ' -o ' + binary + ' ' + source + ' -lm -lcuba -fopenmp'
            subprocess.Popen([cmpl], shell=True, stderr=subprocess.PIPE).communicate()

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


def parallel_cuba_calculate(expansion, parallel_processes=200):
    """
    :param expansion:
    :return:

    not actually parallel yet.
    """

    def run_integration(src_name, h_name, bin_name, integrand, k, result):
        f = open(h_name, 'w')
        header_str = str_for_cuba(integrand)
        f.write(header_str)
        f.close()

        #compiling external C program
        cmpl = 'gcc -Wall -fopenmp -I' + wd + ' -o ' + bin_name + ' ' + src_name + ' -lm -lcuba -fopenmp'
        subprocess.Popen([cmpl], shell=True, stderr=subprocess.PIPE).communicate()

        #running external C program
        integrate = subprocess.Popen([bin_name], env={'OMP_NUM_THREADS': '4', 'CUBAVERBOSE': '0'},
                                     shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        out, err = integrate.communicate()
        result.put((k, (out, err)))

    result = dict()
    split_size = 2

    wd = os.path.expanduser("~") + '/.pole_extractor'
    source = wd + '/' + 'integrate.c'

    map(lambda x: shutil.rmtree(wd + '/' + x), [s for s in os.listdir(wd) if '.jbf' in s])

    sub_folder_names = []
    sources = []
    headers = []
    binaries = []
    job_num = 0

    results = multiprocessing.Queue()
    jobs = []

    for k in expansion.keys():
        for i in range(0, len(expansion[k]), split_size):

            sub_folder_names.append(wd + '/.jbf' + str(job_num).zfill(5))
            sources.append(sub_folder_names[job_num] + '/' + 'integrate.c')
            headers.append(sub_folder_names[job_num] + '/' + 'integrate.h')
            binaries.append(sub_folder_names[job_num] + '/' + 'integrate')

            os.mkdir(sub_folder_names[-1])
            shutil.copy(source, sources[-1])

            jobs.append(multiprocessing.Process(target=run_integration,
                                                args=(sources[job_num], headers[job_num], binaries[job_num],
                                                      expansion[k][i:i + split_size], k, results)))
            job_num += 1

    for i in range(0, len(jobs), parallel_processes):
        map(lambda x: x.start(), jobs[i:i + parallel_processes])
        map(lambda x: x.join(), jobs[i:i + parallel_processes])
        map(lambda x: shutil.rmtree(x), sub_folder_names[i:i + parallel_processes])

    while not results.empty():
        (k, (out, err)) = results.get()
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

    return NumEpsExpansion(result)