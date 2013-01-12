#!/usr/bin/python
# -*- coding: utf8
import sys
from graphs import Graph
import nickel
from methods import sd_tools
import conserv

import polynomial

def generate_code(graph_nickel_notation, strategyName='STRATEGY_C', startOrder=None, endOrder=-1, fileName='bogner.cc'):
    graph = Graph(graph_nickel_notation)
    name = str(graph.GenerateNickel())
    if name <> graph_nickel_notation:
        raise Exception, "non-minimal Nickel index, minimal index is: %s" % name

    graph._eqsubgraphs = list()

    internalEdges = graph._internal_edges_dict()
    if len(graph.ExternalLines()) == 2:
        internalEdges[1000000] = [i.idx() for i in graph.ExternalNodes()] #Additional edge: suitable way to find F
        conservations = conserv.Conservations(internalEdges)
        equations = sd_tools.find_eq(conservations)
        conservations = sd_tools.apply_eq(conservations, equations)
        graph._qi, graph._qi2l = sd_tools.qi_lambda(conservations, equations)
        graph_ = graph.Clone()
        graph_._cons = conservations
        F = sd_tools.gendet(graph_, N=graph.NLoops() + 1)

        internalEdges = graph._internal_edges_dict()
        conservation = conserv.Conservations(internalEdges)
        conservations = sd_tools.apply_eq(conservations, equations)
        graph._cons = conservations

    else:
        F = None
        conservations = conserv.Conservations(internalEdges)
        equations = sd_tools.find_eq(conservations)
        conservations = sd_tools.apply_eq(conservations, equations)
        graph._qi, graph._qi2l = sd_tools.qi_lambda(conservations, equations)
        graph._cons = conservations

    U = sd_tools.gendet(graph, N=graph.NLoops())

    nLoops = graph.NLoops()
    n = len(graph._qi2l)

    U_ = [(1, x) for x in U]
    polyU = polynomial.poly(U_)
    expressionU = polynomial.formatter.format(polyU, polynomial.formatter.CPP)

    if F is None:
        F_ = polynomial.poly(U_) * polynomial.poly([(1, [x, ]) for x in graph._qi2l])
    else:
        F_ = polynomial.poly([(1, x) for x in F])
    expressionF = polynomial.formatter.format(F_, polynomial.formatter.CPP)

    variables = set(polynomial.formatter.formatVarIndexes(F_, polynomial.formatter.CPP))
    variables |= set(polynomial.formatter.formatVarIndexes(polyU, polynomial.formatter.CPP))

    variablesCode = ''.join(map(lambda v: VARIABLE_TEMPLATE.format(v), variables))

    outFile = open(fileName, 'w+')
    outFile.write(BOGNER_CODE_TEMPLATE.format(
        strategy=strategyName,
        n=n,
        loops=nLoops,
        vars=variablesCode,
        u=expressionU,
        f=expressionF,
        startOrder=startOrder if startOrder == None else -nLoops,
        endOrder=endOrder
    ))
    outFile.close()


VARIABLE_TEMPLATE = '''
symbol {0}("{0}");
parameters.push_back({0});
'''

BOGNER_CODE_TEMPLATE = '''#include <iostream>
#include <stdexcept>
#include <vector>
#include <ginac/ginac.h>
#include "sector_decomposition/sector_decomposition.h"

int main()
{{

try{{

using namespace sector_decomposition;
using namespace GiNaC;
int verbose_level = -1;
CHOICE_STRATEGY = {strategy};

symbol eps("eps");
int n     = {n};
int loops = {loops};

std::vector<ex> parameters;
{vars}

std::vector<exponent> nu_minus_1(n,exponent(0,0));

ex U = {u};
ex F = {f};

std::vector<ex> poly_list;
poly_list.push_back(U);
poly_list.push_back(F);

std::vector<exponent> c(poly_list.size());
c[0] = exponent( n-(loops+1)*2, loops+1 );
c[1] = exponent( -n+2*loops, -loops );
for (int k=0; k<n; k++)
{{
c[0].sum_up(nu_minus_1[k]);
c[1].subtract_off(nu_minus_1[k]);
}}

integrand my_integrand(nu_minus_1, poly_list, c);
monte_carlo_parameters mc_parameters( 5, 15, 10000, 100000 );

std::cout << "\\n\\nvalues_strings=list()\\nsector_strings=list()\\neps=list()\\n\\n";
for (int order={startOrder}; order<={endOrder}; order++)
    {{
      std::cout << "\\n\\n\\neps.append(" << order << ")\\n";
      integration_data global_data(parameters, eps, order);
      monte_carlo_result res = do_sector_decomposition(global_data, my_integrand, mc_parameters);
    }}

}} catch (std::exception &e)
{{
    std::cout << "Exception : " << e.what() << std::endl;
}}

return 0;
}}'''



