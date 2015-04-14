#!/usr/bin/python
# -*- coding: utf8
import collections
import os
import re
import shutil
import subprocess
import time
from uncertainties import ufloat
from rggraphutil import zeroDict
from momentumrepr import configure_mr
import stat
import polynomial

__author__ = 'dima'

maxFunctionLength = 1000000

resultingFunctionTemplate = """
double func_t_{fileIdx}(double k[DIMENSION])
{{
double f=0;
{resultingFunctions}
return f;
}}
"""

functionBodyTemplate = """
{comments}
{vars}
//if({zero_condition}){{
//    return 0;
//}}
{supplementary_definitions}
double f=0;
double aux;
{expr}
return f;
"""

functionTemplate = """
double func{idx}_t_{fileIdx}(double k[DIMENSION])
{{
{functionBody}
}}
"""

functionsCodeTemplate = """
#include <math.h>
#define DIMENSION {dims}
#define Pi 3.14159265358979323846

{functions}

{resultingFunction}
"""

headerCodeTemplate = """
#include <math.h>
#define DIMENSION {dims}

double func_t_{fileIdx}(double k[DIMENSION]);
"""


class FunctionsFile(object):
    def __init__(self, file_idx):
        self.file_idx = file_idx
        self.file_info = None
        self.functions = list()

    def add_function(self, function_body):
        self.functions.append(functionTemplate.format(idx=len(self.functions),
                                                      fileIdx=self.file_idx,
                                                      functionBody=function_body))

    def set_file_info(self, file_info):
        self.file_info = file_info

    def __len__(self):
        return sum(map(len, self.functions))

    def _resulting_function(self):
        function_body = ""
        for i in range(len(self.functions)):
            function_body += "f+=func{idx}_t_{fileIdx}(k);\n".format(fileIdx=self.file_idx, idx=i)
        return resultingFunctionTemplate.format(fileIdx=self.file_idx,
                                                resultingFunctions=function_body)

    def get_c_file(self):
        return functionsCodeTemplate.format(dims=self.file_info.dimension,
                                            functions="\n". join(self.functions),
                                            resultingFunction=self._resulting_function())

    def get_h_file(self):
        return headerCodeTemplate.format(dims=self.file_info.dimension,
                                         fileIdx=self.file_idx)

    def get_file_name(self, prefix):
        return "%s_func_%s_V%s_E%s" % (prefix,
                                       self.file_idx,
                                       self.file_info.dimension,
                                       self.file_info.eps_order)

    def get_next(self):
        return FunctionsFile(self.file_idx+1)


funcFileInfo = collections.namedtuple("funcFileInfo", ["eps_order", "dimension"])
integrandInfo = collections.namedtuple("integrandInfo", ["eps_order", "integrands", "variables", "supp_defs", "supp_conditions", "comments"])


def generate_function_body(expr, variables_list, supplementary_definitions, zero_conditions, comments=""):
    vars_string = ""
    for i in range(len(variables_list)):
        variable = variables_list[i]
        vars_string += "double %s=k[%s];\n" % (variable, i)
    supplementary_definitions_string = ""
    for sup in (supplementary_definitions if isinstance(supplementary_definitions, (tuple, list, set)) else (supplementary_definitions, )):
        supplementary_definitions_string += "double %s;\n" % sup
    expr_str = "f+=" + expr.printc() + ";"
    return functionBodyTemplate.format(comments=comments,
                                       vars=vars_string,
                                       zero_condition=" || ".join(zero_conditions),
                                       supplementary_definitions=supplementary_definitions_string,
                                       expr=expr_str)


def generate_func_files(integrand_iterator, generate_function_body_=generate_function_body, max_function_length=maxFunctionLength):
    files = collections.defaultdict(lambda: FunctionsFile(0))
    for integrand_info in integrand_iterator:
        eps_order = integrand_info.eps_order
        file_info = funcFileInfo(eps_order, len(integrand_info.variables) - 1)
        function_file = files[file_info]
        all_variables = integrand_info.variables

        for integrand, removed_arg, theta_condition in zip(integrand_info.integrands, integrand_info.supp_defs, integrand_info.supp_conditions):
            integrand = integrand[eps_order]
            curr_variables = map(lambda v: str(v), filter(lambda v: v != removed_arg, all_variables))
            supp_defs = [str(removed_arg) + " = 1./(" + polynomial.formatter.format(theta_condition, polynomial.formatter.CPP) + ")"]
            supp_conditions = [polynomial.formatter.format(theta_condition, polynomial.formatter.CPP) + " < 1."]
            function_file.add_function(generate_function_body_(integrand, curr_variables, supp_defs, supp_conditions, ""))
        if len(function_file) > max_function_length:
            function_file.set_file_info(file_info)
            files[file_info] = function_file.get_next()
            yield function_file
    for file_info, function_file in files.items():
        if len(function_file) != 0:
            function_file.set_file_info(file_info)
            yield function_file


def get_eps_from_filename(filename):
    regex = re.match(".*_V\d+_E(.*)\.run", filename)
    if regex is not None:
        return eval(regex.groups()[0])
    else:
        raise NotImplementedError("HZ %s" % filename)


def parse_cuba_output(output):
    # if configure_mr.Configure.debug():
    #     print output
    """SUAVE RESULT:	6.99999999999988 +- 0.00000004572840	p = -999.000"""
    regex = re.match(".*RESULT:.(.*) \+- (.*).p.*", output.splitlines()[-1])
    # print "---"
    # print output.splitlines()[-1]
    if regex is not None:
        try:
            res = eval(regex.groups()[0])
            std_dev = eval(regex.groups()[1])
        except BaseException as e:
            raise AssertionError(output)
        return res, std_dev
    raise AssertionError("\"%s\"" % output)


def generate_integrands(integrand_iterator, directory, graph_name):
    subprocess.call(["rm","-rf", directory])
    try:
        os.makedirs(directory)
    except OSError:
        pass
    for functions_file in generate_func_files(integrand_iterator):
        base_filename = os.path.join(directory, functions_file.get_file_name(graph_name))
        f = open("%s.c" % base_filename, "w")
        f.write(functions_file.get_c_file())
        f.close()
        f = open("%s.h" % base_filename, "w")
        f.write(functions_file.get_h_file())
        f.close()


def execute_cuba(directory, chdir=True):
    if chdir:
        os.chdir(directory)
    res = dict()
    for filename in os.listdir("."):
        if filename.endswith("run") and filename != ".run":
            code = str(configure_mr.Configure.integration_algorithm())
            points = str(configure_mr.Configure.maximum_points_number())
            rel_err = str(configure_mr.Configure.relative_error())
            abs_err = str(configure_mr.Configure.absolute_error())
            os.chmod(filename, os.stat(filename).st_mode | stat.S_IEXEC | stat.S_IREAD | stat.S_IWRITE)
            out_file = open(os.path.basename(filename) + ".log", 'a')
            process = subprocess.Popen(["./%s" % filename, code, points, rel_err, abs_err], stdout=out_file, stderr=subprocess.STDOUT)
            ret_code = process.wait()
            if ret_code != 0:
                raise ValueError("return code must be 0, but " + str(ret_code) + " in file " + filename)
            out_file.close()
            with open(os.path.basename(filename) + ".log", 'r') as out_file:
                term = parse_cuba_output(out_file.read())
            out_file.close()
            assert get_eps_from_filename(filename) not in res
            res[get_eps_from_filename(filename)] = ufloat(*term)
    if chdir:
        os.chdir(DEFAULT_PWD)
    return res


def compile_cuba(directory, chdir=True):

    if "cuba_integration.pyc" in __file__:
        path_to_code = __file__.replace("cuba_integration.pyc", "scons/")
    else:
        path_to_code = __file__.replace("cuba_integration.py", "scons/")
    for filename in ["SConstruct.cuba", "common.py", "scons_config.py", "cuba_code_template.py"]:
        shutil.copyfile("%s%s" %(path_to_code, filename), "%s/%s" % (directory, filename))
    if chdir:
        os.chdir(directory)
    ret_val = subprocess.call(["scons", "-f", "SConstruct.cuba"])
    if chdir:
        os.chdir(DEFAULT_PWD)
    if ret_val != 0:
        raise Exception("scons failed, ret_val = %s" % ret_val)


DEFAULT_PWD = None


def set_default_pwd(pwd=None):
    global DEFAULT_PWD
    if pwd is None:
        p1 = subprocess.Popen("pwd", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = p1.communicate()[0]
        DEFAULT_PWD = out.rstrip()
    else:
        DEFAULT_PWD = pwd

set_default_pwd()


def cuba_generate(integrand_series_list, all_integrations, theta_arg_list, theta_removed_parameter_list):
    time_id = int(round(time.time() * 1000))
    directory = os.path.join("tmp/", str(time_id))
    directory = os.path.abspath(directory)

    terms = list()
    for i in xrange(max(integrand_series_list[0].keys()) + 1):
        term = integrandInfo(i, integrand_series_list, all_integrations, theta_removed_parameter_list, theta_arg_list, '')
        terms.append(term)
    generate_integrands(terms, directory, time_id)
    return directory


def cuba_execute(directory):
    ms = time.time()
    compile_cuba(directory, chdir=True)
    exec_res = execute_cuba(directory, chdir=True)
    if configure_mr.Configure.debug():
        print "Integration done in %s s" % (time.time() - ms)
        print "Result", exec_res, "\n\n"
    return exec_res


def cuba_integrate(integrand_series_list, all_integrations, theta_arg_list, theta_removed_parameter_list):
    directory = cuba_generate(integrand_series_list, all_integrations, theta_arg_list, theta_removed_parameter_list)
    return cuba_execute(directory)