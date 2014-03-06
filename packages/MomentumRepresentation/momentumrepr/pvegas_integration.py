#!/usr/bin/python
# -*- coding: utf8
import collections
import os
import re
import shutil
import subprocess

__author__ = 'mkompan'

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
{supplementary_definitions}
double f=0;
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
integrandInfo = collections.namedtuple("integrandInfo", ["integrand", "variables", "supp_defs", "comments"])


def generate_function_body(expr_string, variables_list, supplementary_definitions, comments=""):
    vars_string = ""
    for i in range(len(variables_list)):
        variable = variables_list[i]
        vars_string += "double %s=k[%s];\n" % (variable, i)
    supplementary_definitions_string = ""
    for sup in supplementary_definitions:
        supplementary_definitions_string += "double %s;\n" % sup
    return functionBodyTemplate.format(comments=comments,
                                       vars=vars_string,
                                       supplementary_definitions=supplementary_definitions_string,
                                       expr="f += %s;" % expr_string)


def generate_func_files(integrand_iterator, generate_function_body_=generate_function_body, max_function_length=maxFunctionLength):
    files = collections.defaultdict(lambda: FunctionsFile(0))
    for integrand_info in integrand_iterator:
        for eps_order in integrand_info.integrand:
            file_info = funcFileInfo(eps_order, len(integrand_info.variables))
            function_file = files[file_info]
            function_file.add_function(generate_function_body_(integrand_info.integrand[eps_order],
                                                               integrand_info.variables,
                                                               integrand_info.supp_defs,
                                                               integrand_info.comments))
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


def parse_pvegas_output(output):
    regex = re.match("result = (.*)", output.splitlines()[-4])
    if regex is not None:
        res = eval(regex.groups()[0])
    regex = re.match("std_dev = (.*)", output.splitlines()[-3])
    if regex is not None:
        std_dev = eval(regex.groups()[0])
    return res, std_dev


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


def execute_pvegas(directory, chdir=True):
    if chdir:
        os.chdir(directory)
    res = collections.defaultdict(lambda :0)
    err = collections.defaultdict(lambda :0)
    for filename in os.listdir("."):
        if filename[-3:] == "run":
            process = subprocess.Popen(["./%s" % filename, "100000", "2", "2"], stdout=subprocess.PIPE)
            output = process.communicate()[0]
            term = parse_pvegas_output(output)
            res[get_eps_from_filename(filename)] += term[0]
            err[get_eps_from_filename(filename)] += term[1]
    return res, err


def compile_pvegas(directory, chdir=True):

    path_to_code = __file__.replace("pvegas_integration.py", "scons/")
    for filename in ["SConstruct.pvegas", "common.py", "scons_config.py", "pvegasCodeTemplate.py"]:
        shutil.copyfile("%s%s" %(path_to_code, filename), "%s/%s" % (directory, filename))
    if chdir:
        os.chdir(directory)
    ret_val = subprocess.call(["scons", "-f", "SConstruct.pvegas"])
    if ret_val != 0:
        raise Exception("scons failed, ret_val = %s" % ret_val)


if __name__ == "__main__":
    graph = "asdasd"
    directory = os.path.join("tmp/", str(graph))
    try:
        os.makedirs(directory)
    except OSError:
        pass
    term1 = integrandInfo({0: "1", 1: "3"}, ('k1', 'k2', 'k3'), ('k1k2 = k3',), '// comment term1')
    term2 = integrandInfo({0: "2", 1: "4"}, ('k1', 'k2', 'k3'), ('k1k2 = k3',), '// comment term2')

    integrand_iterator = [term1, term2 ]
    generate_integrands(integrand_iterator, directory, str(graph))

    compile_pvegas(directory, chdir=True)
    print execute_pvegas(directory, chdir=False)


